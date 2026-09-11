import os
import sys
import math
import time
import shutil
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QRectF
from src.core.config import load_config
from src.core.antigravity_provider import LimitItem, QuotaSnapshot
from src.ui.widget import DreamagyWidget
from src.pets.pet_elliot import ElliotPet

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
cfg = load_config()

def qpixmap_to_pil(pixmap: QtGui.QPixmap) -> Image.Image:
    qimg = pixmap.toImage().convertToFormat(QtGui.QImage.Format_RGBA8888)
    ptr = qimg.bits()
    ptr.setsize(qimg.byteCount())
    return Image.frombuffer('RGBA', (qimg.width(), qimg.height()), bytes(ptr), 'raw', 'RGBA', 0, 1)

def save_gif(frames, output_path, duration=42, loop=0):
    """Saves a list of RGBA PIL images as an optimized animated GIF."""
    rgb_frames = []
    for f in frames:
        bg = Image.new("RGB", f.size, (13, 17, 23))
        bg.paste(f, mask=f.split()[3])
        rgb_frames.append(bg.convert("P", palette=Image.ADAPTIVE, colors=128))

    rgb_frames[0].save(
        output_path,
        save_all=True,
        append_images=rgb_frames[1:],
        duration=duration,
        loop=loop,
        optimize=True
    )
    print(f"Saved {output_path} ({os.path.getsize(output_path) // 1024} KB)")

def generate_quota_bars_gif():
    # =====================================================================
    # 1. QUOTA BARS GIF: Highly Dynamic Video-Like Quota Animation
    # =====================================================================
    print("Generating dynamic quota bars GIF...")
    cfg_bars = dict(cfg)
    cfg_bars["language"] = "en"
    cfg_bars["show_pet"] = False
    cfg_bars["limit_rows"] = ["weekly", "5hour", "claude_gpt"]

    widget_bars = DreamagyWidget(cfg_bars)

    num_bar_frames = 72
    b_card_w = widget_bars.width() + 28
    b_card_h = widget_bars.height() + 24
    bars_frames = []

    for i in range(num_bar_frames):
        t_cycle = i / float(num_bar_frames)

        pct_w = int(88 - 4 * math.sin(t_cycle * math.pi * 2.0))
        pct_5h = int(28 - 6 * math.sin(t_cycle * math.pi * 2.0))
        pct_c = int(94 - 3 * math.cos(t_cycle * math.pi * 2.0))

        frac_w = pct_w / 100.0
        frac_5h = pct_5h / 100.0
        frac_c = pct_c / 100.0

        items_map = {
            "weekly": LimitItem("Gemini", "Weekly limit", frac_w, pct_w, "Resets Mon 08:00", 1.0 - frac_w, True),
            "5hour": LimitItem("Gemini", "5-hour limit", frac_5h, pct_5h, "Resets 06:49 · 3h 40m", 1.0 - frac_5h, False),
            "claude_gpt": LimitItem("Claude/GPT", "Claude & GPT", frac_c, pct_c, "Resets 08:03 · 4h 55m", 1.0 - frac_c, True),
        }

        snap = QuotaSnapshot(
            online=True,
            status_text="Antigravity Online",
            tier_name="Pro",
            plan_name="Antigravity",
            items=list(items_map.values()),
            raw_models=[],
            items_by_key=items_map
        )
        widget_bars.update_snapshot(snap)

        for idx, key in enumerate(["weekly", "5hour", "claude_gpt"]):
            bar = widget_bars.bars[idx]
            bar.current_fraction = items_map[key].remaining_fraction
            bar.shimmer_phase = (t_cycle * 2.5 + idx * 0.15) % 1.0
            bar.color_hex = widget_bars.color_bar_warning if not items_map[key].is_healthy else widget_bars.color_bar_healthy

            for pt in bar.particles:
                pt.x += pt.vx * 2.4
                pt.osc_phase += pt.osc_speed * 1.6

        widget_bars.pulse_phase += 0.09

        canvas = QtGui.QPixmap(b_card_w, b_card_h)
        canvas.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(canvas)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        p.setPen(QtGui.QPen(QtGui.QColor("#21262d"), 1.2))
        p.setBrush(QtGui.QColor("#0d1117"))
        p.drawRoundedRect(QRectF(1, 1, b_card_w - 2, b_card_h - 2), 14.0, 14.0)

        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 22), 1.0))
        p.drawLine(QtCore.QPointF(20, 2), QtCore.QPointF(b_card_w - 20, 2))

        p.save()
        p.translate(14, 12)
        widget_bars.render(p, QtCore.QPoint(0, 0))
        p.restore()
        p.end()

        bars_frames.append(qpixmap_to_pil(canvas))

    save_gif(bars_frames, "assets/quota_bars.gif", duration=42)

def generate_elliot_gif():
    # =====================================================================
    # 2. ELLIOT COMPANION GIF: Real Video Sequence of Live Elliot Alderson
    # =====================================================================
    print("Generating live video Elliot companion GIF...")
    elliot = ElliotPet(parent=None, width=112, height=130, detached=False, scale=1.45, pet_avatar="elliot_live")
    num_elliot_frames = 76
    e_card_w = 270
    e_card_h = 244
    elliot_frames = []

    total_src_frames = len(elliot.frames)
    print(f"Loaded {total_src_frames} video frames from elliot_live")

    for i in range(num_elliot_frames):
        t_ratio = i / float(num_elliot_frames)

        # Ping-pong or smooth cycle across the real video frames
        if total_src_frames > 0:
            ping_pong = math.sin(t_ratio * math.pi)
            f_idx = int(ping_pong * (total_src_frames - 1))
            f_idx = max(0, min(total_src_frames - 1, f_idx))
            elliot._photo = elliot.frames[f_idx]

        # Glitch reaction at frame 48..53
        if 48 <= i <= 52:
            elliot.glitch_active = True
            elliot.glitch_dx = 4 if i % 2 == 0 else -4
            elliot.glitch_dy = 2 if i % 3 == 0 else -2
        else:
            elliot.glitch_active = False
            elliot.glitch_dx = 0
            elliot.glitch_dy = 0

        canvas = QtGui.QPixmap(e_card_w, e_card_h)
        canvas.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(canvas)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        p.setPen(QtGui.QPen(QtGui.QColor("#21262d"), 1.2))
        p.setBrush(QtGui.QColor("#0d1117"))
        p.drawRoundedRect(QRectF(1, 1, e_card_w - 2, e_card_h - 2), 16.0, 16.0)

        p.setPen(Qt.NoPen)
        p.setBrush(QtGui.QColor("#ef4444"))
        p.drawEllipse(QPoint(16, 15), 3, 3)
        p.setBrush(QtGui.QColor("#f59e0b"))
        p.drawEllipse(QPoint(26, 15), 3, 3)
        p.setBrush(QtGui.QColor("#10b981"))
        p.drawEllipse(QPoint(36, 15), 3, 3)

        p.setFont(QtGui.QFont("Consolas", 8, QtGui.QFont.Normal))
        p.setPen(QtGui.QColor("#64748b"))
        p.drawText(QRectF(48, 7, e_card_w - 56, 16), Qt.AlignLeft | Qt.AlignVCenter, "daemon: fsociety")

        # Render Elliot centered
        p.save()
        ex = (e_card_w - elliot.width()) // 2
        ey = 26
        p.translate(ex, ey)
        elliot.render(p, QtCore.QPoint(0, 0))
        p.restore()

        # Terminal prompt pill at bottom with live blinking cursor
        pill_rect = QRectF(14, e_card_h - 28, e_card_w - 28, 20)
        p.setPen(QtGui.QPen(QtGui.QColor("#30363d"), 1.0))
        p.setBrush(QtGui.QColor("#161b22"))
        p.drawRoundedRect(pill_rect, 6.0, 6.0)

        p.setFont(QtGui.QFont("Consolas", 8, QtGui.QFont.DemiBold))
        cursor = "_" if (i // 10) % 2 == 0 else " "
        p.setPen(QtGui.QColor("#38bdf8" if (i // 15) % 2 == 0 else "#34d399"))
        p.drawText(pill_rect, Qt.AlignCenter, f"root@fsociety:~# status active{cursor}")

        p.end()
        elliot_frames.append(qpixmap_to_pil(canvas))

    save_gif(elliot_frames, "assets/elliot.gif", duration=42)


def generate_demo_gif():
    # =====================================================================
    # 3. DEMO HERO GIF: Full Dreamagy Widget with Live Video Elliot
    # =====================================================================
    print("Generating live video demo hero GIF...")
    cfg_demo = dict(cfg)
    cfg_demo["language"] = "en"
    cfg_demo["show_pet"] = True
    cfg_demo["pet_detached"] = False
    cfg_demo["pet_scale"] = 1.0
    cfg_demo["current_pet"] = "elliot_live"
    cfg_demo["limit_rows"] = ["weekly", "5hour", "claude_gpt"]

    widget_demo = DreamagyWidget(cfg_demo)
    num_demo_frames = 76
    card_w = widget_demo.width() + 32
    card_h = widget_demo.height() + 28
    demo_frames = []

    pet = widget_demo.pet
    pet_frames = len(pet.frames)

    for i in range(num_demo_frames):
        t_cycle = i / float(num_demo_frames)

        # Step pet live video
        if pet_frames > 0:
            ping_pong = math.sin(t_cycle * math.pi)
            f_idx = int(ping_pong * (pet_frames - 1))
            f_idx = max(0, min(pet_frames - 1, f_idx))
            pet._photo = pet.frames[f_idx]

        pct_w = int(88 - 4 * math.sin(t_cycle * math.pi * 2.0))
        pct_5h = int(28 - 6 * math.sin(t_cycle * math.pi * 2.0))
        pct_c = int(94 - 3 * math.cos(t_cycle * math.pi * 2.0))

        frac_w = pct_w / 100.0
        frac_5h = pct_5h / 100.0
        frac_c = pct_c / 100.0

        items_map = {
            "weekly": LimitItem("Gemini", "Weekly limit", frac_w, pct_w, "Resets Mon 08:00", 1.0 - frac_w, True),
            "5hour": LimitItem("Gemini", "5-hour limit", frac_5h, pct_5h, "Resets 06:49 · 3h 40m", 1.0 - frac_5h, False),
            "claude_gpt": LimitItem("Claude/GPT", "Claude & GPT", frac_c, pct_c, "Resets 08:03 · 4h 55m", 1.0 - frac_c, True),
        }

        snap = QuotaSnapshot(
            online=True,
            status_text="Antigravity Online",
            tier_name="Pro",
            plan_name="Antigravity",
            items=list(items_map.values()),
            raw_models=[],
            items_by_key=items_map
        )
        widget_demo.update_snapshot(snap)

        for idx, key in enumerate(["weekly", "5hour", "claude_gpt"]):
            bar = widget_demo.bars[idx]
            bar.current_fraction = items_map[key].remaining_fraction
            bar.shimmer_phase = (t_cycle * 2.5 + idx * 0.15) % 1.0
            bar.color_hex = widget_demo.color_bar_warning if not items_map[key].is_healthy else widget_demo.color_bar_healthy
            for pt in bar.particles:
                pt.x += pt.vx * 2.4
                pt.osc_phase += pt.osc_speed * 1.6

        widget_demo.pulse_phase += 0.09

        canvas = QtGui.QPixmap(card_w, card_h)
        canvas.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(canvas)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        p.setPen(QtGui.QPen(QtGui.QColor("#21262d"), 1.2))
        p.setBrush(QtGui.QColor("#0d1117"))
        p.drawRoundedRect(QRectF(1, 1, card_w - 2, card_h - 2), 16.0, 16.0)

        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 22), 1.0))
        p.drawLine(QtCore.QPointF(24, 2), QtCore.QPointF(card_w - 24, 2))

        p.save()
        p.translate(16, 14)
        widget_demo.render(p, QtCore.QPoint(0, 0))
        p.restore()
        p.end()

        demo_frames.append(qpixmap_to_pil(canvas))

    save_gif(demo_frames, "assets/demo.gif", duration=42)

def generate_pets_showcase_gif():
    # =====================================================================
    # 4. PETS SHOWCASE GIF: Interactive Roster of All 9 Companions
    # =====================================================================
    print("Generating 9-companions animated showcase GIF...")

    CARD_W = 680
    CARD_H = 432
    num_showcase_frames = 72

    pets_showcase_meta = [
        {"id": "elliot_live",   "name": "Elliot Alderson",  "color": "#38bdf8", "type": "video"},
        {"id": "clippit",       "name": "Clippy (Скрепыш)", "color": "#60a5fa", "type": "atlas", "action1": "waving", "action2": "idle", "speed": 0.28},
        {"id": "tux",           "name": "Tux (Linux)",      "color": "#f59e0b", "type": "atlas", "action1": "running-right", "action2": "running-right", "speed": 0.35},
        {"id": "yorha-sit-2b",  "name": "YoRHa 2B",         "color": "#e2e8f0", "type": "atlas", "action1": "jumping", "action2": "waiting", "speed": 0.30},
        {"id": "nyako-shigure", "name": "Shigure Ui",       "color": "#f472b6", "type": "atlas", "action1": "waving", "action2": "idle", "speed": 0.26},
        {"id": "dario",         "name": "Dario Amodei",     "color": "#818cf8", "type": "atlas", "action1": "review", "action2": "idle", "speed": 0.25},
        {"id": "yelling-dario", "name": "Yelling Dario",    "color": "#ef4444", "type": "atlas", "action1": "running", "action2": "running", "speed": 0.36},
        {"id": "trump",         "name": "Donald Trump",     "color": "#fbbf24", "type": "atlas", "action1": "running-right", "action2": "running-right", "speed": 0.32},
        {"id": "slavik",        "name": "Славик (Slavik)",   "color": "#34d399", "type": "atlas", "action1": "running", "action2": "idle", "speed": 0.30},
    ]

    widgets_showcase = []
    for m in pets_showcase_meta:
        w = ElliotPet(parent=None, width=72, height=80, pet_avatar=m["id"])
        w.set_animations_enabled(False)
        widgets_showcase.append((m, w))

    showcase_frames = []
    for i in range(num_showcase_frames):
        t_cycle = i / float(num_showcase_frames)

        canvas = QtGui.QPixmap(CARD_W, CARD_H)
        canvas.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(canvas)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Card background
        p.setPen(QtGui.QPen(QtGui.QColor("#21262d"), 1.4))
        p.setBrush(QtGui.QColor("#0d1117"))
        p.drawRoundedRect(QRectF(1, 1, CARD_W - 2, CARD_H - 2), 16.0, 16.0)

        # Shimmer line on top edge
        shim_x = int((t_cycle * (CARD_W + 120)) - 60)
        grad = QtGui.QLinearGradient(shim_x, 2, shim_x + 80, 2)
        grad.setColorAt(0.0, QtGui.QColor(255, 255, 255, 0))
        grad.setColorAt(0.5, QtGui.QColor(56, 189, 248, 120))
        grad.setColorAt(1.0, QtGui.QColor(255, 255, 255, 0))
        p.setPen(QtGui.QPen(QtGui.QBrush(grad), 1.6))
        p.drawLine(QtCore.QPointF(20, 2), QtCore.QPointF(CARD_W - 20, 2))

        # Window dots
        p.setPen(Qt.NoPen)
        p.setBrush(QtGui.QColor("#ef4444"))
        p.drawEllipse(QPoint(18, 18), 4, 4)
        p.setBrush(QtGui.QColor("#f59e0b"))
        p.drawEllipse(QPoint(30, 18), 4, 4)
        p.setBrush(QtGui.QColor("#10b981"))
        p.drawEllipse(QPoint(42, 18), 4, 4)

        # Header title
        font_hdr = QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold)
        p.setFont(font_hdr)
        p.setPen(QtGui.QColor("#f0f6fc"))
        p.drawText(QRectF(56, 10, 380, 16), Qt.AlignLeft | Qt.AlignVCenter, "✨ Персонажи на выбор · Interactive Companions")

        # Header badge
        badge_rect = QRectF(CARD_W - 205, 9, 190, 18)
        p.setPen(QtGui.QPen(QtGui.QColor("#30363d"), 1.0))
        p.setBrush(QtGui.QColor("#161b22"))
        p.drawRoundedRect(badge_rect, 5.0, 5.0)

        # Pulsing status dot inside badge
        dot_pulse = (math.sin(t_cycle * math.pi * 2.0 * 2.0) + 1.0) / 2.0
        p.setPen(Qt.NoPen)
        p.setBrush(QtGui.QColor(52, 211, 153, int(150 + dot_pulse * 105)))
        p.drawEllipse(QPoint(int(CARD_W - 195), 18), 3, 3)

        p.setFont(QtGui.QFont("Consolas", 7, QtGui.QFont.DemiBold))
        p.setPen(QtGui.QColor("#38bdf8"))
        p.drawText(QRectF(CARD_W - 186, 9, 168, 18), Qt.AlignLeft | Qt.AlignVCenter, "9 COMPANIONS · ACTIVE")

        # Header divider
        p.setPen(QtGui.QPen(QtGui.QColor("#21262d"), 1.0))
        p.drawLine(QtCore.QPointF(14, 34), QtCore.QPointF(CARD_W - 14, 34))

        # Grid parameters
        cols = 3
        cell_w = 210
        cell_h = 120
        gap_x = 11
        gap_y = 9
        start_x = 14
        start_y = 42

        for idx, (meta, pet_w) in enumerate(widgets_showcase):
            col = idx % cols
            row = idx // cols
            cx = start_x + col * (cell_w + gap_x)
            cy = start_y + row * (cell_h + gap_y)

            # Subtle cell pulse
            pulse = (math.sin(t_cycle * math.pi * 2.0 * 2.0 + idx * 0.75) + 1.0) / 2.0
            acc_base = QtGui.QColor(meta["color"])

            # Cell background & border
            cell_rect = QRectF(cx, cy, cell_w, cell_h)
            cell_border = QtGui.QColor(acc_base.red(), acc_base.green(), acc_base.blue(), int(35 + pulse * 45))
            p.setPen(QtGui.QPen(cell_border, 1.0))
            p.setBrush(QtGui.QColor("#161b22"))
            p.drawRoundedRect(cell_rect, 10.0, 10.0)

            # Animate pet
            if meta["type"] == "video" and len(pet_w.frames) > 0:
                ping_pong = math.sin(t_cycle * math.pi)
                f_idx = int(ping_pong * (len(pet_w.frames) - 1))
                f_idx = max(0, min(len(pet_w.frames) - 1, f_idx))
                pet_w._photo = pet_w.frames[f_idx]
                # Glitch reaction on Elliot around frame 32-36
                if 32 <= i <= 36:
                    pet_w.glitch_active = True
                    pet_w.glitch_dx = 3 if i % 2 == 0 else -3
                else:
                    pet_w.glitch_active = False
                    pet_w.glitch_dx = 0
            else:
                action = meta["action1"] if i < (num_showcase_frames // 2) else meta["action2"]
                pet_w.atlas_state = action
                speed = meta.get("speed", 0.3)
                pet_w.atlas_frame = int(i * speed)

            # Draw pet
            p.save()
            px = cx + (cell_w - pet_w.width()) // 2
            py = cy + 5
            p.translate(px, py)
            pet_w.render(p, QtCore.QPoint(0, 0))
            p.restore()

            # Animated name pill badge
            pill_rect = QRectF(cx + 8, cy + cell_h - 26, cell_w - 16, 20)
            pill_border_alpha = int(140 + pulse * 115)
            pill_pen_color = QtGui.QColor(acc_base.red(), acc_base.green(), acc_base.blue(), pill_border_alpha)
            p.setPen(QtGui.QPen(pill_pen_color, 1.2))
            p.setBrush(QtGui.QColor("#0d1117"))
            p.drawRoundedRect(pill_rect, 5.0, 5.0)

            # Pill status dot
            dot_x = int(cx + 17)
            dot_y = int(cy + cell_h - 16)
            p.setPen(Qt.NoPen)
            p.setBrush(QtGui.QColor(acc_base.red(), acc_base.green(), acc_base.blue(), int(180 + pulse * 75)))
            p.drawEllipse(QPoint(dot_x, dot_y), 2, 2)

            # Pill text with icon
            p.setFont(QtGui.QFont("Segoe UI", 8, QtGui.QFont.DemiBold))
            text_color = acc_base.lighter(int(115 + pulse * 25))
            p.setPen(text_color)
            full_label = meta["name"]
            p.drawText(QRectF(cx + 20, cy + cell_h - 26, cell_w - 36, 20), Qt.AlignCenter, full_label)

        p.end()
        showcase_frames.append(qpixmap_to_pil(canvas))

    save_gif(showcase_frames, "assets/pets_showcase.gif", duration=42)


if __name__ == "__main__":
    only_showcase = "--only-showcase" in sys.argv
    if not only_showcase:
        generate_quota_bars_gif()
        generate_elliot_gif()
        generate_demo_gif()
    generate_pets_showcase_gif()
    print("All live video GIFs and Pet Showcase successfully rendered!")
