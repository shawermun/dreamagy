"""
Antigravity Quota Provider for Dreamagy.
Extracts CSRF token and HTTPS port from Antigravity Language Server,
queries the GetUserStatus RPC, and calculates model group limits, reset times,
and spending pace markers.
"""

import os
import re
import ssl
import json
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from i18n import t

WINDOW_SECONDS = 5 * 3600  # 5-hour quota window (default)
WINDOW_SECONDS_5H = 5 * 3600       # 5-hour quota window
WINDOW_SECONDS_WEEKLY = 7 * 86400  # 7-day weekly quota window

@dataclass
class LimitItem:
    group_name: str         # e.g., "Gemini (Flash & Pro)" or "Claude / GPT"
    label: str              # e.g., "5-hour limit" or "Weekly · all models"
    remaining_fraction: float # 0.0 to 1.0
    percent: int            # 0 to 100
    reset_time_str: str     # Formatted: "Resets 08:10 · 2h 30m"
    elapsed_fraction: float # 0.0 to 1.0 (where we are in the cycle)
    is_healthy: bool        # True if spending pace is safe

@dataclass
class QuotaSnapshot:
    online: bool
    status_text: str
    tier_name: str
    plan_name: str
    items: List[LimitItem]
    raw_models: List[dict]
    items_by_key: Dict[str, LimitItem] = field(default_factory=dict)

    def get_item(self, key: str) -> Optional[LimitItem]:
        if key in self.items_by_key:
            return self.items_by_key[key]
        if key == "claude" and "claude_gpt" in self.items_by_key:
            return self.items_by_key["claude_gpt"]
        if key in ("gemini_weekly", "weekly_gemini") and "weekly" in self.items_by_key:
            return self.items_by_key["weekly"]
        if key in ("weekly_claude", "claude_weekly") and "claude_weekly" in self.items_by_key:
            return self.items_by_key["claude_weekly"]
        if self.items:
            return self.items[0]
        return None


class AntigravityProvider:
    def __init__(self, lang: str = "ru"):
        self.cached_port: Optional[int] = None
        self.cached_token: Optional[str] = None
        self.last_successful_fetch = 0.0
        self.last_snapshot: Optional[QuotaSnapshot] = None
        self.lang = lang
        self._ctx = ssl.create_default_context()
        self._ctx.check_hostname = False
        self._ctx.verify_mode = ssl.CERT_NONE

    def set_language(self, lang: str):
        self.lang = lang

    def find_credentials(self) -> tuple[Optional[str], List[int]]:
        """Finds token and candidate ports from main.log or process inspection."""
        token = None
        ports = []

        # 1. Inspect main.log (fastest & most reliable)
        log_paths = [
            os.path.expandvars(r"%APPDATA%\Antigravity\logs\main.log"),
            os.path.expandvars(r"%APPDATA%\Antigravity IDE\logs\main.log"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\antigravity\logs\main.log"),
        ]

        for lp in log_paths:
            if os.path.exists(lp):
                try:
                    with open(lp, "r", encoding="utf-8", errors="ignore") as f:
                        # read tail if file is large
                        f.seek(0, os.SEEK_END)
                        size = f.tell()
                        read_bytes = min(size, 256 * 1024)
                        f.seek(size - read_bytes)
                        text = f.read()

                    tokens = re.findall(r"--csrf_token[ =]+([a-zA-Z0-9\-]+)", text)
                    if tokens:
                        token = tokens[-1]
                    raw_ports = re.findall(r"127\.0\.0\.1:(\d+)", text)
                    if raw_ports:
                        for p_str in reversed(raw_ports):
                            p = int(p_str)
                            if p not in ports:
                                ports.append(p)
                    if token and ports:
                        break
                except Exception as e:
                    print(f"[Provider] Error reading log {lp}: {e}")

        # 2. If cached port is known, prepend it
        if self.cached_port and self.cached_port not in ports:
            ports.insert(0, self.cached_port)
        if self.cached_token and not token:
            token = self.cached_token

        return token, ports

    def _call_rpc(self, port: int, token: str, method_name: str) -> Optional[dict]:
        """Calls a LanguageServerService Connect RPC method."""
        url = f"https://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/{method_name}"
        payload = json.dumps({"metadata": {"ideName": "antigravity"}}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Codeium-Csrf-Token": token,
                "Connect-Protocol-Version": "1"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, context=self._ctx, timeout=1.5) as resp:
                if resp.status == 200:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw)
        except Exception:
            return None
        return None

    def fetch_status(self, lang: Optional[str] = None) -> QuotaSnapshot:
        """Queries the language server and builds a QuotaSnapshot."""
        if lang:
            self.lang = lang
        active_lang = self.lang
        token, ports = self.find_credentials()
        if not token or not ports:
            return QuotaSnapshot(
                online=False,
                status_text=t("offline", active_lang),
                tier_name="Offline",
                plan_name="Antigravity offline",
                items=[],
                raw_models=[],
                items_by_key={}
            )

        candidate_ports = []
        if self.cached_port and self.cached_port in ports:
            candidate_ports.append(self.cached_port)
        for p in ports:
            if p not in candidate_ports:
                candidate_ports.append(p)

        user_status_data = None
        quota_summary_data = None
        working_port = None

        # Try ports
        for port in candidate_ports[:6]:
            res = self._call_rpc(port, token, "GetUserStatus")
            if res and "userStatus" in res:
                user_status_data = res
                working_port = port
                # Also fetch RetrieveUserQuotaSummary on the same port for accurate weekly & 5h buckets
                quota_summary_data = self._call_rpc(port, token, "RetrieveUserQuotaSummary")
                break

        if not user_status_data or "userStatus" not in user_status_data:
            # If failed, keep last snapshot if recent
            if self.last_snapshot:
                return self.last_snapshot
            return QuotaSnapshot(
                online=False,
                status_text=t("offline", active_lang),
                tier_name="",
                plan_name="",
                items=[],
                raw_models=[],
                items_by_key={}
            )

        # Cache successful connection
        self.cached_port = working_port
        self.cached_token = token
        self.last_successful_fetch = time.time()

        user_status = user_status_data.get("userStatus", {})
        plan_status = user_status.get("planStatus", {})
        plan_info = plan_status.get("planInfo", {})
        plan_name = plan_info.get("planName", "Antigravity Pro")
        user_tier = user_status.get("userTier", {})
        tier_name = user_tier.get("name", "Active")

        cascade = user_status.get("cascadeModelConfigData", {})
        models = cascade.get("clientModelConfigs", [])

        # Process model quotas
        snapshot = self._build_snapshot(models, plan_name, tier_name, lang=active_lang, quota_summary=quota_summary_data)
        self.last_snapshot = snapshot
        return snapshot

    def _build_snapshot(
        self,
        models: List[dict],
        plan_name: str,
        tier_name: str,
        lang: str = "ru",
        quota_summary: Optional[dict] = None
    ) -> QuotaSnapshot:
        now_utc = datetime.now(timezone.utc)

        gemini_weekly = None
        gemini_5h = None
        claude_weekly = None
        claude_5h = None

        if quota_summary:
            groups = quota_summary.get("response", {}).get("groups", [])
            for g in groups:
                disp_grp = (g.get("displayName") or "").lower()
                for b in g.get("buckets", []):
                    b_id = (b.get("bucketId") or "").lower()
                    b_window = (b.get("window") or "").lower()
                    b_disp = (b.get("displayName") or "").lower()
                    rem = float(b.get("remainingFraction", 1.0))
                    rst_str = b.get("resetTime")
                    rst_dt = None
                    if rst_str:
                        try:
                            clean_str = rst_str.replace("Z", "+00:00")
                            rst_dt = datetime.fromisoformat(clean_str)
                        except Exception:
                            pass
                    b_data = {"rem_fraction": rem, "reset_dt": rst_dt, "bucketId": b.get("bucketId")}
                    is_gemini = ("gemini" in disp_grp) or ("gemini" in b_id)
                    is_weekly = (b_window == "weekly") or ("weekly" in b_id) or ("weekly" in b_disp)
                    is_5h = (b_window == "5h") or ("5h" in b_id) or ("five hour" in b_disp) or ("5-hour" in b_disp)
                    if is_gemini:
                        if is_weekly and not gemini_weekly:
                            gemini_weekly = b_data
                        elif is_5h and not gemini_5h:
                            gemini_5h = b_data
                    else:
                        if is_weekly and not claude_weekly:
                            claude_weekly = b_data
                        elif is_5h and not claude_5h:
                            claude_5h = b_data

        # Fallback model items from GetUserStatus
        gemini_items = []
        claude_items = []

        for m in models:
            q = m.get("quotaInfo")
            if not q:
                continue
            label = m.get("label", "")
            rem_fraction = float(q.get("remainingFraction", 1.0))
            reset_str = q.get("resetTime")

            # Parse reset time
            reset_dt = None
            if reset_str:
                try:
                    clean_str = reset_str.replace("Z", "+00:00")
                    reset_dt = datetime.fromisoformat(clean_str)
                except Exception:
                    pass

            item_data = {
                "label": label,
                "rem_fraction": rem_fraction,
                "reset_dt": reset_dt
            }

            if "gemini" in label.lower():
                gemini_items.append(item_data)
            else:
                claude_items.append(item_data)

        items_by_key: Dict[str, LimitItem] = {}

        # 1. Weekly limit (default row 1)
        if gemini_weekly:
            weekly_item = self._create_limit_item(
                group_name=t("weekly_group", lang),
                label=t("weekly_limit", lang),
                rem_fraction=gemini_weekly["rem_fraction"],
                reset_dt=gemini_weekly["reset_dt"],
                now_utc=now_utc,
                lang=lang,
                window_seconds=WINDOW_SECONDS_WEEKLY
            )
        else:
            days_until_monday = (7 - now_utc.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            monday_dt = (now_utc + timedelta(days=days_until_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            weekly_reset_str = t("resets_mon", lang)
            weekly_item = LimitItem(
                group_name=t("weekly_group", lang),
                label=t("weekly_limit", lang),
                remaining_fraction=1.0,
                percent=100,
                reset_time_str=weekly_reset_str,
                elapsed_fraction=0.0,
                is_healthy=True
            )
        items_by_key["weekly"] = weekly_item
        items_by_key["gemini_weekly"] = weekly_item

        # 2. 5-hour limit (Gemini pool, default row 2)
        if gemini_5h:
            gemini_fraction = gemini_5h["rem_fraction"]
            gemini_reset = gemini_5h["reset_dt"]
        elif gemini_items:
            worst_gemini = min(gemini_items, key=lambda x: x["rem_fraction"])
            gemini_fraction = worst_gemini["rem_fraction"]
            gemini_reset = worst_gemini["reset_dt"]
        else:
            gemini_fraction = 1.0
            gemini_reset = None

        five_hour_item = self._create_limit_item(
            group_name="Gemini",
            label=t("five_hour_limit", lang),
            rem_fraction=gemini_fraction,
            reset_dt=gemini_reset,
            now_utc=now_utc,
            lang=lang,
            window_seconds=WINDOW_SECONDS_5H
        )
        items_by_key["5hour"] = five_hour_item
        items_by_key["gemini"] = five_hour_item
        items_by_key["gemini_5h"] = five_hour_item

        # 3. Claude & GPT limit
        if claude_5h:
            claude_fraction = claude_5h["rem_fraction"]
            claude_reset = claude_5h["reset_dt"]
        elif claude_items:
            worst_claude = min(claude_items, key=lambda x: x["rem_fraction"])
            claude_fraction = worst_claude["rem_fraction"]
            claude_reset = worst_claude["reset_dt"]
        else:
            claude_fraction = 1.0
            claude_reset = None

        claude_item = self._create_limit_item(
            group_name="Claude & GPT",
            label=t("claude_gpt_limit", lang),
            rem_fraction=claude_fraction,
            reset_dt=claude_reset,
            now_utc=now_utc,
            lang=lang,
            window_seconds=WINDOW_SECONDS_5H
        )
        items_by_key["claude_gpt"] = claude_item
        items_by_key["claude"] = claude_item
        items_by_key["claude_5h"] = claude_item

        # 4. Claude & GPT Weekly limit (optional row)
        if claude_weekly:
            claude_weekly_item = self._create_limit_item(
                group_name="Claude & GPT",
                label=t("claude_weekly_limit", lang),
                rem_fraction=claude_weekly["rem_fraction"],
                reset_dt=claude_weekly["reset_dt"],
                now_utc=now_utc,
                lang=lang,
                window_seconds=WINDOW_SECONDS_WEEKLY
            )
            items_by_key["claude_weekly"] = claude_weekly_item
            items_by_key["weekly_claude"] = claude_weekly_item

        # Default items list order: Row 0 is Weekly, Row 1 is 5-hour, Row 2 is Claude & GPT
        items: List[LimitItem] = [weekly_item, five_hour_item, claude_item]

        return QuotaSnapshot(
            online=True,
            status_text=t("app_title", lang),
            tier_name=tier_name,
            plan_name=plan_name,
            items=items,
            raw_models=models,
            items_by_key=items_by_key
        )

    def _create_limit_item(
        self,
        group_name: str,
        label: str,
        rem_fraction: float,
        reset_dt: Optional[datetime],
        now_utc: datetime,
        lang: str = "ru",
        window_seconds: float = WINDOW_SECONDS_5H
    ) -> LimitItem:
        percent = int(round(rem_fraction * 100))
        
        # Calculate time string and elapsed fraction
        if reset_dt:
            delta_seconds = (reset_dt - now_utc).total_seconds()
            local_reset = reset_dt.astimezone().strftime("%H:%M")
            pfx = t("resets_prefix", lang)
            unit_d = t("time_d", lang) or "d"
            unit_h = t("time_h", lang) or "h"
            unit_m = t("time_m", lang) or "m"
            
            if delta_seconds > 0:
                hours = int(delta_seconds // 3600)
                mins = int((delta_seconds % 3600) // 60)
                if hours >= 24:
                    days = int(hours // 24)
                    rem_hours = hours % 24
                    time_desc = f"{days}{unit_d} {rem_hours}{unit_h}"
                elif hours > 0:
                    time_desc = f"{hours}{unit_h} {mins:02d}{unit_m}"
                else:
                    time_desc = f"{mins}{unit_m}"
                reset_str = f"{pfx} {local_reset} · {time_desc}"
            else:
                reset_str = f"{pfx} {local_reset}"

            # Calculate where we are in the cycle window
            time_left = max(0.0, delta_seconds)
            elapsed_fraction = max(0.0, min(1.0, 1.0 - (time_left / max(1.0, window_seconds))))
        else:
            reset_str = t("resets_unknown", lang)
            elapsed_fraction = 0.5

        quota_remaining = rem_fraction
        time_remaining = 1.0 - elapsed_fraction
        is_healthy = quota_remaining >= (time_remaining * 0.85)

        return LimitItem(
            group_name=group_name,
            label=label,
            remaining_fraction=rem_fraction,
            percent=percent,
            reset_time_str=reset_str,
            elapsed_fraction=elapsed_fraction,
            is_healthy=is_healthy
        )


if __name__ == "__main__":
    provider = AntigravityProvider()
    snap = provider.fetch_status()
    print(f"Online: {snap.online} ({snap.status_text})")
    print(f"Plan: {snap.plan_name} | Tier: {snap.tier_name}")
    for it in snap.items:
        print(f"[{it.group_name}] {it.label}: {it.percent}% | {it.reset_time_str} | Marker: {it.elapsed_fraction*100:.1f}% | Safe: {it.is_healthy}")
