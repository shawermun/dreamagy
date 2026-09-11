"""
Universal Animated Pet Companion Widget for Dreamagy.
Supports:
1. Codex / vscode-pets 8x9 Sprite Atlas (Clippy, Tux, YoRHa 2B, etc.) with state-machine
   (idle, running, waving, jumping, failed, review).
2. Live Frame Sequences (e.g. Elliot Live video).
3. Procedural Photo Companions (breathing, blinks, parallax, posture sway, glitch, hacking lean).
4. Interactive Speech Bubbles with companion-specific quotes.
"""

import math
import os
import json
import random
import time
from typing import List, Tuple, Optional, Dict
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QTimer
from src.core.i18n import t
from src.pets import pet_catalog

QUOTES = [
    "hello, friend.",
    "control is an illusion.",
    "daemon active.",
    "root@fsociety:~#",
    "stay paranoid.",
    "leave me here.",
    "everything is connected."
]

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_PATH = os.path.join(ROOT_DIR, "assets", "elliot.png")
PETS_DIR = os.path.join(ROOT_DIR, "assets", "pets")

# Standard Codex 8x9 Atlas layout (matching pet-companion & vscode-pets)
DEFAULT_CODEX_ROWS: Dict[str, dict] = {
    "idle": {"index": 0, "frames": 6, "fps": 6},
    "running-right": {"index": 1, "frames": 8, "fps": 8},
    "running-left": {"index": 2, "frames": 8, "fps": 8},
    "waving": {"index": 3, "frames": 4, "fps": 6},
    "jumping": {"index": 4, "frames": 5, "fps": 7},
    "failed": {"index": 5, "frames": 8, "fps": 7},
    "waiting": {"index": 6, "frames": 6, "fps": 6},
    "running": {"index": 7, "frames": 6, "fps": 8},
    "review": {"index": 8, "frames": 6, "fps": 6},
}


class PetCompanionWidget(QtWidgets.QWidget):
    """Universal animated pet companion widget supporting Sprite Atlases, Sequences, and Photos."""
    clicked = QtCore.pyqtSignal()
    position_changed = QtCore.pyqtSignal(int, int)
    context_menu_requested = QtCore.pyqtSignal(QtCore.QPoint)
    pet_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, width=76, height=88, detached=False, scale=1.0, pet_avatar="clippit"):
        super().__init__(parent)
        self._detached = detached
        self._base_width = width
        self._base_height = height
        self._scale = scale
        self.setFixedSize(int(round(width * scale)), int(round(height * scale)))
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        if detached:
            self._apply_detached_flags()

        # Mode: 'atlas', 'sequence', or 'photo'
        self.pet_mode = "photo"
        self.is_atlas = False
        self.is_animated_sequence = False

        # Atlas state
        self._spritesheet = QtGui.QPixmap()
        self.atlas_cols = 8
        self.atlas_rows = 9
        self.atlas_rows_def = dict(DEFAULT_CODEX_ROWS)
        self.atlas_state = "idle"
        self.atlas_frame = 0
        self.last_atlas_frame_time = time.time()
        self.atlas_state_end_time = 0.0
        self.is_pixel_art = True

        # Animated sequence state (for live video companions)
        self.frames: List[QtGui.QPixmap] = []
        self.current_frame_idx = 0
        self.frame_direction = 1
        self.last_frame_time = time.time()
        self.normal_frame_interval = 0.033
        self.fast_frame_interval = 0.022

        # Speech bubble
        self.speech_text = ""
        self.speech_opacity = 0.0
        self.speech_start_time = 0.0
        self.speech_duration = 3.2
        self.current_quotes: List[str] = list(QUOTES)

        # Photo procedural animation state
        self.current_pet_name = pet_avatar
        self.current_pet_path = ""
        self._photo = QtGui.QPixmap()

        # Load initial pet
        pet_path = os.path.join(PETS_DIR, pet_avatar)
        if not os.path.exists(pet_path):
            pet_path = ASSET_PATH
        if not self.set_pet_image(pet_path, save_name=pet_avatar):
            print(f"[PetCompanionWidget] Asset not found: {pet_path}")

        # Animation state
        self.animations_enabled = True
        self.start_time = time.time()
        self.breath_phase = 0.0

        # Blink state (natural blink & double blink)
        self.is_blinking = False
        self.blink_progress = 0.0
        self.double_blink = False
        self.next_blink_time = time.time() + random.uniform(3.0, 5.5)

        # Micro-parallax / glance state
        self.parallax_offset_x = 0.0
        self.parallax_target_x = 0.0
        self.next_glance_time = time.time() + random.uniform(2.0, 5.0)

        # Head sway / tilt state
        self.head_sway_active = False
        self.head_sway_start = 0.0
        self.head_sway_duration = 1.6
        self.head_sway_angle = 0.0
        self.head_sway_dx = 0.0
        self.next_idle_sway_time = time.time() + random.uniform(7.0, 14.0)

        # Hood adjustment state
        self.hood_adjust_active = False
        self.hood_adjust_start = 0.0
        self.hood_adjust_duration = 1.1
        self.hood_adjust_angle = 0.0
        self.hood_adjust_dy = 0.0
        self.hood_adjust_scale_y = 1.0

        # Posture shift state
        self.posture_tilt = 0.0
        self.target_posture_tilt = 0.0
        self.posture_dy = 0.0
        self.target_posture_dy = 0.0
        self.next_posture_time = time.time() + random.uniform(8.0, 16.0)

        # Typing focus lean state
        self.typing_active = False
        self.typing_lean_y = 0.0
        self.typing_tilt = 0.0
        self.typing_jitter_x = 0.0
        self.typing_end_time = 0.0

        # Glitch state
        self.glitch_active = False
        self.glitch_start_time = 0.0
        self.glitch_duration = 0.28
        self.glitch_dx = 0
        self.glitch_dy = 0

        # Legacy compatibility aliases
        self.wave_active = False
        self.wave_start_time = 0.0
        self.wave_duration = 0.35
        self.wave_offset_x = 0.0
        self.brow_lift_active = False
        self.speech_fade_start = 0.0

        # Dragging (for detached mode)
        self._dragging = False
        self._drag_start_pos = QPoint()
        self._press_pos = QPoint()

        # Animation timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def _apply_detached_flags(self):
        """Set window flags for independent floating window mode."""
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def set_detached(self, detached: bool):
        """Switch between docked and detached modes."""
        self._detached = detached
        if detached:
            self._apply_detached_flags()

    def set_scale(self, scale: float):
        """Set scale multiplier (0.75, 1.0, 1.25, 1.5)."""
        self._scale = scale
        self.setFixedSize(int(round(self._base_width * scale)), int(round(self._base_height * scale)))
        self.update()

    def set_animations_enabled(self, enabled: bool):
        """Enable or disable pet animations."""
        self.animations_enabled = enabled
        if not enabled:
            self.breath_phase = 0.0
            self.parallax_offset_x = 0.0
            self.head_sway_angle = 0.0
            self.head_sway_dx = 0.0
            self.hood_adjust_angle = 0.0
            self.hood_adjust_dy = 0.0
            self.hood_adjust_scale_y = 1.0
            self.posture_tilt = 0.0
            self.posture_dy = 0.0
            self.typing_lean_y = 0.0
            self.typing_tilt = 0.0
            self.is_blinking = False
            self.glitch_active = False
            self.atlas_frame = 0
        self.update()

    def show_speech(self, text: str, duration: float = 3.2):
        """Displays a speech bubble over the companion."""
        self.speech_text = text
        self.speech_opacity = 1.0
        self.speech_start_time = time.time()
        self.speech_duration = duration
        self.update()

    @classmethod
    def get_available_pets(cls, lang: str = "ru") -> List[Tuple[str, str, str]]:
        """
        Returns list of (display_name, filename_or_dirname, full_path) for all assets in assets/pets/.
        Correctly categorizes Atlas pets, Image Sequences, and Photo companions.
        """
        if not os.path.exists(PETS_DIR):
            os.makedirs(PETS_DIR, exist_ok=True)
        results = []
        valid_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

        for fname in sorted(os.listdir(PETS_DIR)):
            item_path = os.path.join(PETS_DIR, fname)
            if os.path.isdir(item_path):
                # 1. Check if Codex 8x9 Sprite Atlas
                manifest_file = os.path.join(item_path, "pet.json")
                has_sprite = any(
                    os.path.exists(os.path.join(item_path, f"spritesheet.{ext}"))
                    for ext in ("webp", "png", "gif")
                )
                if has_sprite or os.path.exists(manifest_file):
                    catalog_info = pet_catalog.get_pet_info(fname.lower())
                    if catalog_info:
                        label_key = f"display_name_{lang}"
                        display_name = catalog_info.get(label_key, catalog_info.get("display_name_ru", fname))
                    else:
                        display_name = f"🐾 {fname.replace('_', ' ').replace('-', ' ').title()}"
                    results.append((display_name, fname, item_path))
                    continue

                # 2. Check for animation frame files inside (sequence)
                has_frames = any(os.path.splitext(f)[1].lower() in valid_exts for f in os.listdir(item_path))
                if has_frames:
                    if fname.lower() == "elliot_live":
                        display_name = t("pet_elliot_live", lang)
                    else:
                        display_name = f"🎬 {fname.replace('_', ' ').title()}"
                    results.append((display_name, fname, item_path))

            elif os.path.isfile(item_path):
                base, ext = os.path.splitext(fname)
                if ext.lower() in valid_exts:
                    if base.lower() == "elliot":
                        display_name = t("pet_elliot_photo", lang)
                    else:
                        display_name = f"📸 {base.replace('_', ' ').title()}"
                    results.append((display_name, fname, item_path))

        if not any(r[1] in ("elliot.png", "elliot") for r in results) and os.path.exists(ASSET_PATH):
            results.append((t("pet_elliot_photo", lang), "elliot.png", ASSET_PATH))

        def sort_key(entry):
            name = entry[1].lower()
            if name == "clippit":
                return (0, "")
            elif name == "tux":
                return (1, "")
            elif name == "elliot_live":
                return (2, "")
            elif name in ("elliot.png", "elliot"):
                return (3, "")
            return (4, name)

        results.sort(key=sort_key)
        return results

    def set_pet_image(self, image_path: str, save_name: Optional[str] = None) -> bool:
        """Loads and activates a new pet (Codex Sprite Atlas, Image Sequence, or Single Photo)."""
        if not os.path.exists(image_path):
            cand = os.path.join(PETS_DIR, image_path)
            if os.path.exists(cand):
                image_path = cand
            else:
                return False

        if os.path.isdir(image_path):
            dir_name = os.path.basename(image_path)
            
            # --- 1. Check if Codex 8x9 Sprite Atlas ---
            sprite_path = None
            for ext in ("webp", "png", "gif"):
                cand = os.path.join(image_path, f"spritesheet.{ext}")
                if os.path.exists(cand):
                    sprite_path = cand
                    break

            manifest_path = os.path.join(image_path, "pet.json")
            if sprite_path and os.path.exists(sprite_path):
                pix = QtGui.QPixmap(sprite_path)
                if not pix.isNull():
                    self._spritesheet = pix
                    self.atlas_cols = 8
                    self.atlas_rows = 9
                    self.atlas_rows_def = dict(DEFAULT_CODEX_ROWS)
                    self.is_pixel_art = True
                    self.current_quotes = list(QUOTES)

                    # Check pet.json metadata
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            if "cols" in data:
                                self.atlas_cols = max(1, int(data["cols"]))
                            if "rows" in data:
                                self.atlas_rows = max(1, int(data["rows"]))
                            if "rowsDef" in data and isinstance(data["rowsDef"], list):
                                for r in data["rowsDef"]:
                                    rid = r.get("id")
                                    if rid:
                                        self.atlas_rows_def[rid] = {
                                            "index": r.get("index", 0),
                                            "frames": r.get("frames", 6),
                                            "fps": r.get("fps", 6)
                                        }
                        except Exception as e:
                            print(f"[PetCompanionWidget] Warning reading {manifest_path}: {e}")

                    # Check catalog metadata for quotes and pixel art styling
                    cat_info = pet_catalog.get_pet_info(dir_name.lower())
                    if cat_info:
                        if "quotes" in cat_info:
                            self.current_quotes = list(cat_info["quotes"])
                        if "pixel_art" in cat_info:
                            self.is_pixel_art = cat_info["pixel_art"]

                    self.pet_mode = "atlas"
                    self.is_atlas = True
                    self.is_animated_sequence = False
                    self.atlas_state = "idle"
                    self.atlas_frame = 0
                    self.last_atlas_frame_time = time.time()
                    self.atlas_state_end_time = 0.0

                    cw = max(1, self._spritesheet.width() // self.atlas_cols)
                    ch = max(1, self._spritesheet.height() // self.atlas_rows)
                    self._photo = self._spritesheet.copy(0, 0, cw, ch)

                    self.current_pet_path = image_path
                    self.current_pet_name = save_name if save_name else dir_name
                    self.pet_changed.emit(self.current_pet_name)
                    self.update()
                    return True

            # --- 2. Check if Image Sequence ---
            valid_exts = {".png", ".jpg", ".jpeg", ".webp"}
            frame_files = sorted([f for f in os.listdir(image_path) if os.path.splitext(f)[1].lower() in valid_exts])
            if frame_files:
                loaded = []
                for fn in frame_files:
                    pix = QtGui.QPixmap(os.path.join(image_path, fn))
                    if not pix.isNull():
                        loaded.append(pix)
                if loaded:
                    self.frames = loaded
                    self.pet_mode = "sequence"
                    self.is_animated_sequence = True
                    self.is_atlas = False
                    self.current_frame_idx = 0
                    self.frame_direction = 1
                    self.last_frame_time = time.time()
                    self._photo = self.frames[0]
                    self.current_quotes = list(QUOTES)
                    self.current_pet_path = image_path
                    self.current_pet_name = save_name if save_name else dir_name
                    self.pet_changed.emit(self.current_pet_name)
                    self.update()
                    return True

        # --- 3. Single Photo / Avatar ---
        if os.path.isfile(image_path):
            pix = QtGui.QPixmap(image_path)
            if not pix.isNull():
                self.pet_mode = "photo"
                self.is_animated_sequence = False
                self.is_atlas = False
                self.frames = []
                self._photo = pix
                self.current_quotes = list(QUOTES)
                self.current_pet_path = image_path
                self.current_pet_name = save_name if save_name else os.path.basename(image_path)
                self.pet_changed.emit(self.current_pet_name)
                self.update()
                return True

        return False

    def on_keyboard_activity(self):
        """Called whenever user types on keyboard — switches companion into focus/running mode."""
        self.typing_active = True
        self.typing_end_time = time.time() + 1.2
        if self.pet_mode == "atlas":
            if self.atlas_state not in ("waving", "jumping"):
                if "running" in self.atlas_rows_def:
                    self.atlas_state = "running"
                elif "review" in self.atlas_rows_def:
                    self.atlas_state = "review"

    def reaction_adjust_hood(self):
        """Reaction: Shoulder lift, head tilt, settles back."""
        self.hood_adjust_active = True
        self.hood_adjust_start = time.time()
        self.hood_adjust_duration = 1.1

    def reaction_head_sway(self):
        """Reaction: Thoughtfully sways/tilts head side-to-side."""
        self.head_sway_active = True
        self.head_sway_start = time.time()
        self.head_sway_duration = 1.6

    def reaction_double_blink(self):
        """Reaction: Rapid double-blink with a micro-glance."""
        self.is_blinking = True
        self.blink_progress = 0.0
        self.double_blink = True
        self.parallax_target_x = random.choice([-1.5, 1.5])

    def reaction_glitch(self, quote=None):
        """Reaction: Chromatic RGB channel shift glitch."""
        self.trigger_glitch(quote)

    def reaction_blink_glitch(self):
        self.reaction_double_blink()
        self.trigger_glitch()

    def reaction_wave(self):
        self.wave_active = True
        self.wave_start_time = time.time()
        if self.pet_mode == "atlas":
            self.atlas_state = "waving" if "waving" in self.atlas_rows_def else "idle"
            self.atlas_frame = 0
            self.atlas_state_end_time = time.time() + 1.2
        else:
            self.reaction_adjust_hood()

    def reaction_side_glance(self):
        self.parallax_target_x = random.choice([-2.0, 2.0])
        self.parallax_offset_x = self.parallax_target_x
        self.brow_lift_active = True
        self.reaction_head_sway()

    def trigger_glitch(self, quote=None):
        """Trigger glitch and show quote."""
        self.glitch_active = True
        self.glitch_start_time = time.time()
        self.glitch_dx = random.choice([-3, 3])
        self.glitch_dy = random.choice([-2, 2])
        chosen_quote = quote if quote else random.choice(self.current_quotes)
        self.show_speech(chosen_quote)

    def trigger_random_reaction(self):
        """Trigger interactive click reaction based on the companion type."""
        now = time.time()
        quote = random.choice(self.current_quotes) if self.current_quotes else ""

        if self.pet_mode == "atlas":
            actions = [act for act in ("waving", "jumping") if act in self.atlas_rows_def]
            chosen_act = random.choice(actions) if actions else "idle"
            self.atlas_state = chosen_act
            self.atlas_frame = 0
            r_cfg = self.atlas_rows_def.get(chosen_act, {"frames": 6, "fps": 6})
            duration = max(1.0, (r_cfg.get("frames", 6) / max(1, r_cfg.get("fps", 6))) * 1.5)
            self.atlas_state_end_time = now + duration
            if quote:
                self.show_speech(quote)
            return

        if self.pet_mode == "sequence":
            self.typing_end_time = now + 1.8
            if quote:
                self.show_speech(quote)
            return

        # Photo mode procedural reactions
        r = random.random()
        if r < 0.35:
            self.reaction_adjust_hood()
        elif r < 0.65:
            self.reaction_head_sway()
        elif r < 0.85:
            self.reaction_double_blink()
        else:
            self.trigger_glitch()

        if quote and not self.speech_text:
            self.show_speech(quote)

    def update_animation(self):
        """Timer callback running at ~60 FPS."""
        now = time.time()

        # Update speech bubble fade
        if self.speech_text and self.speech_opacity > 0.0:
            elapsed = now - self.speech_start_time
            if elapsed > self.speech_duration:
                self.speech_opacity = max(0.0, self.speech_opacity - 0.06)
                if self.speech_opacity <= 0.0:
                    self.speech_text = ""
                    self.update()

        # --- Atlas Mode Update ---
        if self.pet_mode == "atlas":
            if not self.animations_enabled:
                self.atlas_frame = 0
                self.update()
                return

            # Check action state expiry
            if self.atlas_state in ("waving", "jumping", "failed") and now >= self.atlas_state_end_time:
                self.atlas_state = "idle"
                self.atlas_frame = 0
            elif self.typing_active:
                if now >= self.typing_end_time:
                    self.typing_active = False
                    if self.atlas_state in ("running", "review"):
                        self.atlas_state = "idle"
                        self.atlas_frame = 0
                else:
                    if self.atlas_state not in ("waving", "jumping"):
                        self.atlas_state = "running" if "running" in self.atlas_rows_def else "idle"

            # Frame stepping
            r_cfg = self.atlas_rows_def.get(self.atlas_state, self.atlas_rows_def.get("idle", {"frames": 6, "fps": 6}))
            fps = max(1, r_cfg.get("fps", 6))
            frames_count = max(1, r_cfg.get("frames", 6))
            interval = 1.0 / fps

            if now - self.last_atlas_frame_time >= interval:
                self.atlas_frame = (self.atlas_frame + 1) % frames_count
                self.last_atlas_frame_time = now
                self.update()
            return

        # --- Sequence Mode Update ---
        if self.pet_mode == "sequence" and self.frames:
            if not self.animations_enabled:
                self.current_frame_idx = 0
                self._photo = self.frames[0]
                self.update()
                return

            if self.typing_active and now >= self.typing_end_time:
                self.typing_active = False

            cur_interval = self.fast_frame_interval if self.typing_active else self.normal_frame_interval
            if now - self.last_frame_time >= cur_interval:
                num_frames = len(self.frames)
                next_idx = self.current_frame_idx + self.frame_direction
                if next_idx >= num_frames:
                    self.current_frame_idx = num_frames - 2 if num_frames > 1 else 0
                    self.frame_direction = -1
                elif next_idx < 0:
                    self.current_frame_idx = 1 if num_frames > 1 else 0
                    self.frame_direction = 1
                else:
                    self.current_frame_idx = next_idx

                self._photo = self.frames[self.current_frame_idx]
                self.last_frame_time = now
                self.update()
            return

        # --- Photo Mode Procedural Animations ---
        if not self.animations_enabled:
            return

        # 1. Breathing cycle
        t_elapsed = now - self.start_time
        self.breath_phase = math.sin(t_elapsed * 1.5)

        # 2. Typing activity
        if self.typing_active:
            if now < self.typing_end_time:
                self.typing_lean_y = -3.5
                self.typing_tilt = -1.5
                self.typing_jitter_x = (random.random() - 0.5) * 0.8
            else:
                self.typing_active = False
                self.typing_lean_y = 0.0
                self.typing_tilt = 0.0
                self.typing_jitter_x = 0.0

        # 3. Posture shifting
        if now >= self.next_posture_time:
            self.target_posture_tilt = random.uniform(-2.2, 2.2)
            self.target_posture_dy = random.uniform(-1.2, 1.2)
            self.next_posture_time = now + random.uniform(10.0, 18.0)
        self.posture_tilt += (self.target_posture_tilt - self.posture_tilt) * 0.03
        self.posture_dy += (self.target_posture_dy - self.posture_dy) * 0.03

        # 4. Head sway animation
        if self.head_sway_active:
            sway_t = (now - self.head_sway_start) / self.head_sway_duration
            if sway_t >= 1.0:
                self.head_sway_active = False
                self.head_sway_angle = 0.0
                self.head_sway_dx = 0.0
                self.brow_lift_active = False
            else:
                decay = math.sin((1.0 - sway_t) * (math.pi / 2.0))
                self.head_sway_angle = math.sin(sway_t * math.pi * 3.5) * 3.2 * decay
                self.head_sway_dx = math.sin(sway_t * math.pi * 3.5) * 1.8 * decay

        # 5. Hood adjust animation
        if self.hood_adjust_active:
            hood_t = (now - self.hood_adjust_start) / self.hood_adjust_duration
            if hood_t >= 1.0:
                self.hood_adjust_active = False
                self.hood_adjust_angle = 0.0
                self.hood_adjust_dy = 0.0
                self.hood_adjust_scale_y = 1.0
                self.wave_active = False
            else:
                if hood_t < 0.4:
                    p = hood_t / 0.4
                    ease = math.sin(p * math.pi / 2.0)
                    self.hood_adjust_dy = -3.2 * ease
                    self.hood_adjust_angle = -2.8 * ease
                    self.hood_adjust_scale_y = 1.0 + 0.025 * ease
                elif hood_t < 0.65:
                    p = (hood_t - 0.4) / 0.25
                    micro = math.sin(p * math.pi * 2.0) * 0.8
                    self.hood_adjust_dy = -3.2 + micro
                    self.hood_adjust_angle = -2.8 + micro * 0.8
                    self.hood_adjust_scale_y = 1.025
                else:
                    p = (hood_t - 0.65) / 0.35
                    ease = math.cos(p * math.pi / 2.0)
                    self.hood_adjust_dy = -3.2 * ease
                    self.hood_adjust_angle = -2.8 * ease
                    self.hood_adjust_scale_y = 1.0 + 0.025 * ease

        # 6. Natural blink & double blink
        if not self.is_blinking:
            if now >= self.next_blink_time:
                self.is_blinking = True
                self.blink_progress = 0.0
                self.double_blink = (random.random() < 0.30)
        else:
            speed = 0.16 if not self.double_blink else 0.22
            self.blink_progress += speed
            if self.blink_progress >= 1.0:
                if self.double_blink:
                    self.double_blink = False
                    self.blink_progress = 0.0
                else:
                    self.is_blinking = False
                    self.blink_progress = 0.0
                    self.next_blink_time = now + random.uniform(3.0, 6.0)

        # 7. Micro-parallax glance
        if now >= self.next_glance_time:
            self.parallax_target_x = random.choice([-2.0, -1.0, 0.0, 1.0, 2.0])
            self.next_glance_time = now + random.uniform(2.5, 6.0)
        self.parallax_offset_x += (self.parallax_target_x - self.parallax_offset_x) * 0.08

        # 8. Occasional idle head sway
        if not self.head_sway_active and not self.hood_adjust_active and now >= self.next_idle_sway_time:
            self.reaction_head_sway()
            self.next_idle_sway_time = now + random.uniform(8.0, 18.0)

        # 9. Glitch expiry
        if self.glitch_active:
            if now - self.glitch_start_time > self.glitch_duration:
                self.glitch_active = False
                self.glitch_dx = 0
                self.glitch_dy = 0

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._press_pos = event.globalPos()
            if self._detached:
                self._dragging = True
                self._drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            if self._detached:
                self.context_menu_requested.emit(event.globalPos())
                event.accept()
            else:
                event.ignore()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._detached and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPos() - self._drag_start_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            is_click = True
            if hasattr(self, "_press_pos"):
                dist = (event.globalPos() - self._press_pos).manhattanLength()
                if dist > 5:
                    is_click = False
            if self._dragging:
                self._dragging = False
                self.position_changed.emit(self.x(), self.y())
            if is_click:
                self.trigger_random_reaction()
                self.clicked.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()

        # --- Draw Atlas Mode ---
        if self.pet_mode == "atlas" and not self._spritesheet.isNull():
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, not self.is_pixel_art)
            
            cw = self._spritesheet.width() / float(self.atlas_cols)
            ch = self._spritesheet.height() / float(self.atlas_rows)

            r_cfg = self.atlas_rows_def.get(self.atlas_state, self.atlas_rows_def.get("idle", {"index": 0, "frames": 6}))
            row_idx = r_cfg.get("index", 0)
            col_idx = self.atlas_frame % max(1, r_cfg.get("frames", 1))

            src_rect = QRectF(col_idx * cw, row_idx * ch, cw, ch)

            # Aspect-fit inside widget
            aspect = cw / max(ch, 1.0)
            margin = 2
            tw = w - margin * 2
            th = h - margin * 2
            if tw / th > aspect:
                draw_h = th
                draw_w = draw_h * aspect
            else:
                draw_w = tw
                draw_h = draw_w / aspect
            draw_x = margin + (tw - draw_w) / 2.0
            draw_y = margin + (th - draw_h) / 2.0

            target_rect = QRectF(draw_x, draw_y, draw_w, draw_h)
            painter.drawPixmap(target_rect, self._spritesheet, src_rect)

            if self.speech_text and self.speech_opacity > 0.01:
                self._draw_speech_bubble(painter, w / 2.0)
            return

        # Fallback if photo asset is missing
        if self._photo.isNull():
            painter.setBrush(QtGui.QColor("#111317"))
            painter.setPen(QtGui.QPen(QtGui.QColor("#2d3440"), 1))
            painter.drawRoundedRect(2, 2, w - 4, h - 4, 8, 8)
            painter.setPen(QtGui.QColor("#64748b"))
            painter.setFont(QtGui.QFont("Consolas", 7))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "E")
            return

        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Target rect for the photo inside the widget, centered
        margin = 2
        target = QRectF(margin, margin, w - margin * 2, h - margin * 2)

        src_w = self._photo.width()
        src_h = self._photo.height()
        aspect = src_w / max(src_h, 1)
        if target.width() / target.height() > aspect:
            draw_h = target.height()
            draw_w = draw_h * aspect
        else:
            draw_w = target.width()
            draw_h = draw_w / aspect
        draw_x = target.left() + (target.width() - draw_w) / 2.0
        draw_y = target.top() + (target.height() - draw_h) / 2.0

        # Pivot point at chest / neck area
        pivot_x = draw_x + draw_w / 2.0
        pivot_y = draw_y + draw_h * 0.85

        # Calculate breathing and combined transforms
        if self.is_animated_sequence:
            total_tilt = self.typing_tilt
            total_dx = (self.typing_jitter_x if self.typing_active else 0.0)
            total_dy = self.typing_lean_y
            total_scale_y = 1.0
        else:
            breath_y = self.breath_phase * 0.8
            breath_scale_y = 1.0 + self.breath_phase * 0.008
            total_tilt = self.posture_tilt + self.head_sway_angle + self.hood_adjust_angle + self.typing_tilt
            blink_dip = math.sin(self.blink_progress * math.pi) * 1.5 if self.is_blinking else 0.0
            total_dx = self.parallax_offset_x + self.head_sway_dx + (self.typing_jitter_x if self.typing_active else 0.0)
            total_dy = breath_y + self.posture_dy + self.hood_adjust_dy + self.typing_lean_y + blink_dip
            total_scale_y = breath_scale_y * self.hood_adjust_scale_y

        painter.save()
        painter.translate(pivot_x + total_dx, pivot_y + total_dy)
        painter.rotate(total_tilt)
        painter.scale(1.0, total_scale_y)
        painter.translate(-pivot_x, -pivot_y)

        # Glitch RGB split
        if self.glitch_active:
            painter.save()
            painter.translate(self.glitch_dx, self.glitch_dy)

            painter.save()
            painter.setOpacity(0.25)
            painter.translate(-2.0, 0)
            painter.drawPixmap(QRectF(draw_x, draw_y, draw_w, draw_h),
                               self._photo, QRectF(0, 0, src_w, src_h))
            painter.restore()

            painter.save()
            painter.setOpacity(0.25)
            painter.translate(2.0, 0)
            painter.drawPixmap(QRectF(draw_x, draw_y, draw_w, draw_h),
                               self._photo, QRectF(0, 0, src_w, src_h))
            painter.restore()
            painter.restore()

        painter.setOpacity(1.0)
        painter.drawPixmap(QRectF(draw_x, draw_y, draw_w, draw_h),
                           self._photo, QRectF(0, 0, src_w, src_h))
        painter.restore()

        if self.speech_text and self.speech_opacity > 0.01:
            self._draw_speech_bubble(painter, w / 2.0)

    def _draw_speech_bubble(self, p: QtGui.QPainter, cx: float):
        p.save()
        p.setOpacity(self.speech_opacity)
        font = QtGui.QFont("Segoe UI", 7, QtGui.QFont.Bold)
        p.setFont(font)

        fm = QtGui.QFontMetrics(font)
        disp = self.speech_text
        text_w = min(self.width() - 4, fm.horizontalAdvance(disp) + 10)
        text_h = fm.height() + 4

        bx = max(2.0, cx - (text_w / 2.0))
        by = 2.0

        bubble_rect = QRectF(bx, by, text_w, text_h)
        p.setBrush(QtGui.QColor(12, 16, 22, 240))
        p.setPen(QtGui.QPen(QtGui.QColor(56, 189, 248, 190), 1.0))
        p.drawRoundedRect(bubble_rect, 4, 4)

        p.setPen(QtGui.QColor("#38bdf8"))
        p.drawText(bubble_rect, Qt.AlignCenter, disp)
        p.restore()


# Backwards compatibility alias
ElliotPet = PetCompanionWidget

__all__ = ["PetCompanionWidget", "ElliotPet", "PETS_DIR", "ASSET_PATH", "QUOTES", "DEFAULT_CODEX_ROWS"]
