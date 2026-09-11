"""
Pet Elliot Alderson (Mr. Robot / Rami Malek) photo-realistic animated companion for Dreamagy.
Uses a high-quality cutout photo asset with procedural breathing, blinking,
micro-glance parallax, and cyberpunk glitch effects.
Supports docked (child widget) and detached (independent floating window) modes.
"""

import math
import os
import random
import time
from typing import List, Tuple, Optional
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QTimer
from i18n import t

QUOTES = [
    "hello, friend.",
    "control is an illusion.",
    "daemon active.",
    "root@fsociety:~#",
    "stay paranoid.",
    "leave me here.",
    "everything is connected."
]

ASSET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "elliot.png")
PETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pets")


class ElliotPet(QtWidgets.QWidget):
    """Animated Elliot Alderson and custom companion widget with photo-realistic rendering."""
    clicked = QtCore.pyqtSignal()
    position_changed = QtCore.pyqtSignal(int, int)
    context_menu_requested = QtCore.pyqtSignal(QtCore.QPoint)
    pet_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, width=76, height=88, detached=False, scale=1.0, pet_avatar="elliot_live"):
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

        # Animated sequence state (for live video companions)
        self.is_animated_sequence = False
        self.frames: List[QtGui.QPixmap] = []
        self.current_frame_idx = 0
        self.frame_direction = 1
        self.last_frame_time = time.time()
        self.normal_frame_interval = 0.033
        self.fast_frame_interval = 0.022

        # Load pet photo asset or sequence
        self.current_pet_name = pet_avatar
        self.current_pet_path = ""
        self._photo = QtGui.QPixmap()
        pet_path = os.path.join(PETS_DIR, pet_avatar)
        if not os.path.exists(pet_path):
            pet_path = ASSET_PATH
        if not self.set_pet_image(pet_path, save_name=pet_avatar):
            print(f"[ElliotPet] Asset not found: {pet_path}")

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

        # Head sway / tilt state (задумчиво качает головой)
        self.head_sway_active = False
        self.head_sway_start = 0.0
        self.head_sway_duration = 1.6
        self.head_sway_angle = 0.0
        self.head_sway_dx = 0.0
        self.next_idle_sway_time = time.time() + random.uniform(7.0, 14.0)

        # Hood adjustment state (поправляет капюшон)
        self.hood_adjust_active = False
        self.hood_adjust_start = 0.0
        self.hood_adjust_duration = 1.1
        self.hood_adjust_angle = 0.0
        self.hood_adjust_dy = 0.0
        self.hood_adjust_scale_y = 1.0

        # Posture shift state (естественная смена позы раз в 10-18 сек)
        self.posture_tilt = 0.0
        self.target_posture_tilt = 0.0
        self.posture_dy = 0.0
        self.target_posture_dy = 0.0
        self.next_posture_time = time.time() + random.uniform(8.0, 16.0)

        # Keyboard typing reaction
        self.typing_active = False
        self.typing_end_time = 0.0
        self.typing_lean_y = 0.0
        self.typing_tilt = 0.0
        self.typing_jitter_x = 0.0
        self.typing_jitter_y = 0.0

        # Glitch state
        self.glitch_active = False
        self.glitch_end_time = 0.0
        self.glitch_dx = 0
        self.glitch_dy = 0

        # Legacy compatibility aliases
        self.wave_active = False
        self.wave_start_time = 0.0
        self.wave_duration = 0.35
        self.wave_offset_x = 0.0
        self.brow_lift_active = False

        # Speech text (maintained for compatibility, but bubble not drawn)
        self.speech_text = ""
        self.speech_opacity = 0.0
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
        """Enable or disable pet procedural animations."""
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
        self.update()

    @classmethod
    def get_available_pets(cls, lang: str = "ru") -> List[Tuple[str, str, str]]:
        """Returns list of (display_name, filename_or_dirname, full_path) for all assets in assets/pets/."""
        if not os.path.exists(PETS_DIR):
            os.makedirs(PETS_DIR, exist_ok=True)
        results = []
        valid_exts = {".png", ".jpg", ".jpeg", ".webp"}
        for fname in sorted(os.listdir(PETS_DIR)):
            item_path = os.path.join(PETS_DIR, fname)
            if os.path.isdir(item_path):
                # Check for animation frame files inside
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

        if not results and os.path.exists(ASSET_PATH):
            results.append((t("pet_elliot_photo", lang), "elliot.png", ASSET_PATH))

        def sort_key(entry):
            name = entry[1].lower()
            if name == "elliot_live":
                return (0, "")
            elif name in ("elliot.png", "elliot"):
                return (1, "")
            return (2, name)

        results.sort(key=sort_key)
        return results

    def set_pet_image(self, image_path: str, save_name: Optional[str] = None) -> bool:
        """Loads and activates a new pet image or animated sequence directory."""
        if not os.path.exists(image_path):
            return False

        if os.path.isdir(image_path):
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
                    self.is_animated_sequence = True
                    self.current_frame_idx = 0
                    self.frame_direction = 1
                    self.last_frame_time = time.time()
                    self._photo = self.frames[0]
                    self.current_pet_path = image_path
                    self.current_pet_name = save_name if save_name else os.path.basename(image_path)
                    self.pet_changed.emit(self.current_pet_name)
                    self.update()
                    return True

        if os.path.isfile(image_path):
            pix = QtGui.QPixmap(image_path)
            if not pix.isNull():
                self.is_animated_sequence = False
                self.frames = []
                self._photo = pix
                self.current_pet_path = image_path
                self.current_pet_name = save_name if save_name else os.path.basename(image_path)
                self.pet_changed.emit(self.current_pet_name)
                self.update()
                return True

        return False

    def on_keyboard_activity(self):
        """Called whenever user types on keyboard — activates smooth hacking focus lean."""
        self.typing_active = True
        self.typing_end_time = time.time() + 1.2

    def reaction_adjust_hood(self):
        """Reaction: Elliot adjusts his hood — shoulder lifts, head tilts, and smoothly settles back."""
        self.hood_adjust_active = True
        self.hood_adjust_start = time.time()
        self.hood_adjust_duration = 1.1

    def reaction_head_sway(self):
        """Reaction: Elliot thoughtfully sways/tilts his head side-to-side."""
        self.head_sway_active = True
        self.head_sway_start = time.time()
        self.head_sway_duration = 1.6

    def reaction_double_blink(self):
        """Reaction: Natural rapid double-blink with a micro-glance."""
        self.is_blinking = True
        self.blink_progress = 0.0
        self.double_blink = True
        self.parallax_target_x = random.choice([-1.5, 1.5])

    def reaction_glitch(self, quote=None):
        """Reaction: Chromatic RGB channel shift glitch."""
        self.trigger_glitch(quote)

    # Backward compatibility aliases
    def reaction_blink_glitch(self):
        self.reaction_double_blink()
        self.trigger_glitch()

    def reaction_wave(self):
        self.wave_active = True
        self.wave_start_time = time.time()
        self.reaction_adjust_hood()

    def reaction_side_glance(self):
        self.parallax_target_x = random.choice([-2.0, 2.0])
        self.parallax_offset_x = self.parallax_target_x
        self.brow_lift_active = True
        self.reaction_head_sway()

    def trigger_random_reaction(self):
        """Cycles through cinematic, procedural interactions or live video sequence reactions."""
        self._reaction_idx = getattr(self, "_reaction_idx", 0) + 1
        if self.is_animated_sequence:
            choice = self._reaction_idx % 3
            if choice == 0:
                self.reaction_glitch()
            elif choice == 1:
                # Responsive ping-pong direction bounce
                self.frame_direction = -self.frame_direction
                self.on_keyboard_activity()
            else:
                self.reaction_glitch(random.choice(QUOTES))
        else:
            choice = self._reaction_idx % 4
            if choice == 0:
                self.reaction_adjust_hood()
            elif choice == 1:
                self.reaction_head_sway()
            elif choice == 2:
                self.reaction_double_blink()
            else:
                self.reaction_glitch()

    def trigger_glitch(self, quote=None):
        self.glitch_active = True
        self.glitch_end_time = time.time() + 0.35
        self.speech_text = quote if quote else random.choice(QUOTES)
        self.speech_opacity = 1.0
        self.speech_fade_start = time.time() + 2.5
        self.update()

    def update_animation(self):
        if not self.animations_enabled:
            return

        now = time.time()
        elapsed = now - self.start_time

        # Live video frame stepping (ping-pong loop with typing acceleration)
        if self.is_animated_sequence and self.frames:
            interval = self.fast_frame_interval if self.typing_active else self.normal_frame_interval
            dt = now - self.last_frame_time
            if dt >= interval:
                steps = int(dt / interval)
                self.last_frame_time += steps * interval
                if now - self.last_frame_time > interval * 4:
                    self.last_frame_time = now
                n = len(self.frames)
                if n > 1:
                    for _ in range(min(steps, n)):
                        next_idx = self.current_frame_idx + self.frame_direction
                        if next_idx >= n:
                            self.frame_direction = -1
                            self.current_frame_idx = n - 2
                        elif next_idx < 0:
                            self.frame_direction = 1
                            self.current_frame_idx = 1
                        else:
                            self.current_frame_idx = next_idx
                    self._photo = self.frames[self.current_frame_idx]
        else:
            # 1. Smooth organic breathing
            self.breath_phase = math.sin(elapsed * 1.5)

            # 2. Idle posture shift (every 8-16s)
            if now >= self.next_posture_time:
                self.target_posture_tilt = random.choice([-1.5, -0.7, 0.0, 0.7, 1.5])
                self.target_posture_dy = random.choice([-0.8, 0.0, 0.6])
                self.next_posture_time = now + random.uniform(8.0, 16.0)
            self.posture_tilt += (self.target_posture_tilt - self.posture_tilt) * 0.04
            self.posture_dy += (self.target_posture_dy - self.posture_dy) * 0.04

            # 3. Idle head sway (every 7-14s when not already active)
            if not self.head_sway_active and now >= self.next_idle_sway_time:
                if random.random() < 0.65:
                    self.head_sway_active = True
                    self.head_sway_start = now
                    self.head_sway_duration = 1.8
                self.next_idle_sway_time = now + random.uniform(7.0, 14.0)

            # 4. Head sway animation (качает головой)
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

            # 5. Hood adjust animation (поправляет капюшон)
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
                self.parallax_target_x = random.choice([-0.8, -0.4, 0.0, 0.0, 0.4, 0.8])
                self.next_glance_time = now + random.uniform(2.0, 5.0)
            self.parallax_offset_x += (self.parallax_target_x - self.parallax_offset_x) * 0.12

        # 8. Typing focus (smooth organic forward lean)
        if self.typing_active:
            if now > self.typing_end_time:
                self.typing_active = False
                self.typing_lean_y = 0.0
                self.typing_tilt = 0.0
            else:
                self.typing_lean_y = 1.0
                self.typing_tilt = math.sin((now - self.start_time) * 10.0) * 0.5
        else:
            self.typing_lean_y *= 0.85
            self.typing_tilt *= 0.85

        # 9. Glitch
        if self.glitch_active:
            if now > self.glitch_end_time:
                self.glitch_active = False
                self.glitch_dx = 0
                self.glitch_dy = 0
            else:
                self.glitch_dx = random.choice([-2, 0, 2])
                self.glitch_dy = random.choice([-1, 0, 1])

        # 10. Speech fade
        if self.speech_opacity > 0.0:
            if now > self.speech_fade_start:
                self.speech_opacity = max(0.0, self.speech_opacity - 0.035)

        self.update()

    # --- Mouse events for dragging in detached mode and click interactions ---
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
                event.ignore()  # Forward to parent widget in docked mode
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
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()

        if self._photo.isNull():
            painter.setBrush(QtGui.QColor("#111317"))
            painter.setPen(QtGui.QPen(QtGui.QColor("#2d3440"), 1))
            painter.drawRoundedRect(2, 2, w - 4, h - 4, 8, 8)
            painter.setPen(QtGui.QColor("#64748b"))
            painter.setFont(QtGui.QFont("Consolas", 7))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "E")
            return

        # Target rect for the photo inside the widget, centered
        margin = 2
        target = QRectF(margin, margin, w - margin * 2, h - margin * 2)

        # Aspect-fit the photo into the target rect
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

        # Translate & rotate around chest pivot
        painter.translate(pivot_x + total_dx, pivot_y + total_dy)
        painter.rotate(total_tilt)
        painter.scale(1.0, total_scale_y)
        painter.translate(-pivot_x, -pivot_y)

        # Glitch: draw RGB-shifted shadow copies with subtle opacity
        if self.glitch_active:
            painter.save()
            painter.translate(self.glitch_dx, self.glitch_dy)

            # Red channel shift
            painter.save()
            painter.setOpacity(0.25)
            painter.translate(-2.0, 0)
            painter.drawPixmap(QRectF(draw_x, draw_y, draw_w, draw_h),
                               self._photo, QRectF(0, 0, src_w, src_h))
            painter.restore()

            # Cyan channel shift
            painter.save()
            painter.setOpacity(0.25)
            painter.translate(2.0, 0)
            painter.drawPixmap(QRectF(draw_x, draw_y, draw_w, draw_h),
                               self._photo, QRectF(0, 0, src_w, src_h))
            painter.restore()

            painter.restore()

        # Draw the main photo cleanly without any artificial stripes or boxes
        painter.setOpacity(1.0)
        painter.drawPixmap(QRectF(draw_x, draw_y, draw_w, draw_h),
                           self._photo, QRectF(0, 0, src_w, src_h))

        painter.restore()

    def _draw_speech_bubble(self, p: QtGui.QPainter, cx: float):
        p.save()
        p.setOpacity(self.speech_opacity)
        font = QtGui.QFont("Consolas", 7, QtGui.QFont.Bold)
        p.setFont(font)

        fm = QtGui.QFontMetrics(font)
        # compact message text
        disp = self.speech_text
        text_w = min(self.width() - 4, fm.horizontalAdvance(disp) + 10)
        text_h = fm.height() + 4

        bx = max(2.0, cx - (text_w / 2.0))
        by = 2.0

        bubble_rect = QRectF(bx, by, text_w, text_h)
        p.setBrush(QtGui.QColor(12, 16, 22, 240))
        p.setPen(QtGui.QPen(QtGui.QColor(16, 185, 129, 190), 1.0))
        p.drawRoundedRect(bubble_rect, 4, 4)

        p.setPen(QtGui.QColor("#10b981"))
        p.drawText(bubble_rect, Qt.AlignCenter, disp)
        p.restore()
