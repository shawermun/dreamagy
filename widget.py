"""
Main Floating Quota Pill Widget for Dreamagy.
Replicates the minimalist Quotty aesthetic:
- Sleek dark obsidian glassmorphism
- Animated progress bars with healthy green / amber / coral gradients
- Slow floating particles constrained WITHIN the progress bar track
- White vertical timeline marker line for the 5-hour window
- Detachable Elliot Alderson (Mr. Robot) animated pet
- Drag-and-drop repositioning with persistent coordinates
- Right-click context menu and system tray integration
"""

import math
import os
import random
import shutil
import time
from typing import List, Optional
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QTimer

from pet_elliot import ElliotPet
from antigravity_provider import LimitItem, QuotaSnapshot
from i18n import t


class Particle:
    """Luminous micro-spark / bubble drifting smoothly inside the progress bar capsule."""
    def __init__(self, x: float, bar_top: float, bar_h: float):
        self.x = x
        self.bar_top = bar_top
        self.bar_h = bar_h
        # Smooth horizontal drift speed (leftward)
        self.vx = random.uniform(-0.35, -0.75)
        # Vertical sine wave oscillation within capsule height
        self.osc_phase = random.uniform(0, math.pi * 2)
        self.osc_speed = random.uniform(0.04, 0.08)
        self.osc_amp = bar_h * 0.28
        self.bar_center_y = bar_top + bar_h / 2.0
        self.y = self.bar_center_y + math.sin(self.osc_phase) * self.osc_amp
        self.radius = random.uniform(1.1, 2.1)
        self.base_alpha = random.randint(160, 240)
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.05, 0.11)

    def update(self, min_x: float, max_x: float):
        self.x += self.vx
        self.osc_phase += self.osc_speed
        self.pulse_phase += self.pulse_speed
        self.y = self.bar_center_y + math.sin(self.osc_phase) * self.osc_amp
        # Wrap around smoothly when exiting on the left
        if self.x < min_x:
            self.x = max_x - random.uniform(0, 4)
            self.osc_phase = random.uniform(0, math.pi * 2)


class AnimatedProgressBar:
    """Represents a single progress bar with animated lerp, shimmer, and particle effects."""
    def __init__(self, shimmer_offset: float = 0.0):
        self.current_fraction = 0.0
        self.target_fraction = 0.0
        self.current_elapsed = 0.0
        self.target_elapsed = 0.0
        self.particles: List[Particle] = []
        self.color_hex = "#34d399"
        self.is_healthy = True
        self.has_initialized = False
        self.shimmer_phase = shimmer_offset
        self.target_particle_count = 16

    def update(
        self,
        dt: float,
        fill_rect: Optional[QRectF] = None,
        color_healthy: str = "#34d399",
        color_warning: str = "#f59e0b",
        color_critical: str = "#ef4444",
        animations_enabled: bool = True,
        shimmer_enabled: bool = True,
        particles_enabled: bool = True
    ):
        # Progress shimmer wave (~2.2s cycle)
        if animations_enabled and shimmer_enabled:
            self.shimmer_phase = (self.shimmer_phase + 0.008) % 1.0

        # Initial snap or smooth lerp
        if not self.has_initialized:
            self.current_fraction = self.target_fraction
            self.current_elapsed = self.target_elapsed
            self.has_initialized = True
        else:
            if animations_enabled:
                self.current_fraction += (self.target_fraction - self.current_fraction) * 0.14
                self.current_elapsed += (self.target_elapsed - self.current_elapsed) * 0.12
            else:
                self.current_fraction = self.target_fraction
                self.current_elapsed = self.target_elapsed

        # Color
        if self.current_fraction < 0.15:
            self.color_hex = color_critical
        elif not self.is_healthy:
            self.color_hex = color_warning
        else:
            self.color_hex = color_healthy

        # Update particles inside fill_rect
        if animations_enabled and particles_enabled and fill_rect and fill_rect.width() > 16:
            min_x = fill_rect.left() + 3
            max_x = fill_rect.right() - 3
            if len(self.particles) < self.target_particle_count:
                needed = self.target_particle_count - len(self.particles)
                for _ in range(needed):
                    px = random.uniform(min_x, max_x)
                    self.particles.append(Particle(px, fill_rect.top(), fill_rect.height()))

            for pt in self.particles:
                pt.bar_top = fill_rect.top()
                pt.bar_h = fill_rect.height()
                pt.bar_center_y = fill_rect.top() + fill_rect.height() / 2.0
                if pt.x > max_x:
                    pt.x = random.uniform(min_x, max_x)
                pt.update(min_x, max_x)
        else:
            self.particles.clear()


class DreamagyWidget(QtWidgets.QWidget):
    """Floating Quotty-style window with Antigravity limits & Elliot pet."""

    position_changed = QtCore.pyqtSignal(int, int)
    opacity_changed = QtCore.pyqtSignal(float)
    pet_toggled = QtCore.pyqtSignal(bool)
    pet_detach_toggled = QtCore.pyqtSignal(bool)
    pet_scale_changed = QtCore.pyqtSignal(float)
    pet_avatar_changed = QtCore.pyqtSignal(str)
    limit_rows_changed = QtCore.pyqtSignal(list)
    open_settings_requested = QtCore.pyqtSignal()
    request_refresh = QtCore.pyqtSignal()
    quit_app = QtCore.pyqtSignal()

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_Hover, True)
        self.setWindowOpacity(self.config.get("opacity", 0.95))

        self._dragging = False
        self._drag_start_pos = QPoint()

        self.language = self.config.get("language", "ru")
        self.font_family = self.config.get("font_family", "Segoe UI")
        self.font_size = int(self.config.get("font_size", 9))
        self.animations_enabled = bool(self.config.get("animations_enabled", True))
        self.shimmer_enabled = bool(self.config.get("shimmer_enabled", True))
        self.particles_enabled = bool(self.config.get("particles_enabled", True))
        self.pet_animations_enabled = bool(self.config.get("pet_animations_enabled", True))
        self.color_bg = self.config.get("color_bg", "#11151b")
        self.color_bar_healthy = self.config.get("color_bar_healthy", "#34d399")
        self.color_bar_warning = self.config.get("color_bar_warning", "#f59e0b")
        self.color_bar_critical = self.config.get("color_bar_critical", "#ef4444")

        self.show_pet = self.config.get("show_pet", True)
        self.pet_detached = self.config.get("pet_detached", False)
        self.pet_scale = float(self.config.get("pet_scale", 1.0))
        self.current_pet = self.config.get("current_pet", "elliot_live")
        self.limit_rows = list(self.config.get("limit_rows", ["weekly", "5hour"]))

        # Create the pet widget — it manages its own window when detached
        self.pet = ElliotPet(
            parent=None if self.pet_detached else self,
            width=76, height=88,
            detached=self.pet_detached,
            scale=self.pet_scale,
            pet_avatar=self.current_pet
        )
        self.pet.set_animations_enabled(self.animations_enabled and self.pet_animations_enabled)
        if self.pet_detached:
            pet_x = self.config.get("pet_pos_x", 50)
            pet_y = self.config.get("pet_pos_y", 50)
            self.pet.move(pet_x, pet_y)
        self.pet.setVisible(self.show_pet)
        self.pet.position_changed.connect(self._on_pet_pos_changed)
        self.pet.context_menu_requested.connect(self._show_context_menu)
        self.pet.pet_changed.connect(self._on_pet_avatar_changed)

        self.bars = [
            AnimatedProgressBar(shimmer_offset=0.0),
            AnimatedProgressBar(shimmer_offset=0.35),
            AnimatedProgressBar(shimmer_offset=0.70)
        ]
        self.snapshot: Optional[QuotaSnapshot] = None
        self.pulse_phase = 0.0

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_animation_frame)
        self.anim_timer.start(16)

        self._recalculate_size()
        pos_x = self.config.get("pos_x", 120)
        pos_y = self.config.get("pos_y", 120)
        self.move(pos_x, pos_y)

    def apply_settings(self, cfg: dict):
        """Applies dynamic settings (colors, typography, animations, language)."""
        self.config.update(cfg)
        self.language = cfg.get("language", self.language)
        self.font_family = cfg.get("font_family", self.font_family)
        self.font_size = int(cfg.get("font_size", self.font_size))
        self.animations_enabled = bool(cfg.get("animations_enabled", self.animations_enabled))
        self.shimmer_enabled = bool(cfg.get("shimmer_enabled", self.shimmer_enabled))
        self.particles_enabled = bool(cfg.get("particles_enabled", self.particles_enabled))
        self.pet_animations_enabled = bool(cfg.get("pet_animations_enabled", self.pet_animations_enabled))
        self.color_bg = cfg.get("color_bg", self.color_bg)
        self.color_bar_healthy = cfg.get("color_bar_healthy", self.color_bar_healthy)
        self.color_bar_warning = cfg.get("color_bar_warning", self.color_bar_warning)
        self.color_bar_critical = cfg.get("color_bar_critical", self.color_bar_critical)

        self.pet.set_animations_enabled(self.animations_enabled and self.pet_animations_enabled)
        self._recalculate_size()
        self.update()

    def _recalculate_size(self):
        num_rows = len(self.limit_rows)
        pill_w = 356
        pill_h = 88 if num_rows <= 2 else 88 + (num_rows - 2) * 26
        if self.show_pet and not self.pet_detached:
            pet_w = int(round(76 * self.pet_scale))
            pet_h = int(round(88 * self.pet_scale))
            total_w = pill_w + pet_w + 14
            total_h = max(pill_h, pet_h) + 16
            self.setFixedSize(total_w, total_h)
            pet_y = (total_h - pet_h) // 2
            self.pet.move(4, pet_y)
        else:
            total_w = pill_w + 12
            total_h = pill_h + 16
            self.setFixedSize(total_w, total_h)

    def _on_pet_pos_changed(self, x: int, y: int):
        """Save pet position when pet is dragged independently."""
        self.config["pet_pos_x"] = x
        self.config["pet_pos_y"] = y

    def _on_pet_avatar_changed(self, pet_name: str):
        self.current_pet = pet_name
        self.config["current_pet"] = pet_name
        self.pet_avatar_changed.emit(pet_name)

    def update_snapshot(self, snapshot: QuotaSnapshot):
        self.snapshot = snapshot
        if snapshot:
            for i, row_key in enumerate(self.limit_rows):
                if i >= len(self.bars):
                    break
                it = snapshot.get_item(row_key)
                if it:
                    bar = self.bars[i]
                    bar.target_fraction = it.remaining_fraction
                    bar.target_elapsed = it.elapsed_fraction
                    bar.is_healthy = it.is_healthy
                    if not bar.has_initialized:
                        bar.current_fraction = it.remaining_fraction
                        bar.current_elapsed = it.elapsed_fraction
                        bar.has_initialized = True
        self.update()

    def _on_animation_frame(self):
        if self.animations_enabled:
            self.pulse_phase += 0.05
        self.update()

    # --- Mouse & Drag Handling ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and (event.buttons() & Qt.LeftButton):
            new_pos = event.globalPos() - self._drag_start_pos
            self.move(new_pos)
            # Move docked pet along with widget
            if self.show_pet and not self.pet_detached:
                pass  # pet is a child widget, moves automatically
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self.position_changed.emit(self.x(), self.y())
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # --- Limit Rows & Pet Helpers ---
    def set_limit_rows(self, rows: List[str]):
        self.limit_rows = list(rows)
        self.config["limit_rows"] = list(rows)
        self._recalculate_size()
        if self.snapshot:
            self.update_snapshot(self.snapshot)
        self.limit_rows_changed.emit(self.limit_rows)
        self.update()

    def _set_row_at(self, idx: int, key: str):
        rows = list(self.limit_rows)
        while len(rows) <= idx:
            rows.append(key)
        rows[idx] = key
        self.set_limit_rows(rows)

    def _toggle_third_row(self):
        rows = list(self.limit_rows)
        if len(rows) >= 3:
            rows = rows[:2]
        else:
            candidate = "claude_gpt" if "claude_gpt" not in rows else "weekly"
            rows.append(candidate)
        self.set_limit_rows(rows)

    def set_pet_avatar(self, pet_name: str):
        pets = ElliotPet.get_available_pets(self.language)
        for dname, fname, path in pets:
            if fname == pet_name:
                self.pet.set_pet_image(path, save_name=fname)
                self._on_pet_avatar_changed(fname)
                break

    def add_custom_pet_dialog(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите изображение питомца", "", "Изображения (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            from pet_elliot import PETS_DIR
            os.makedirs(PETS_DIR, exist_ok=True)
            dest_name = os.path.basename(file_path)
            dest_path = os.path.join(PETS_DIR, dest_name)
            try:
                if os.path.abspath(file_path) != os.path.abspath(dest_path):
                    shutil.copy2(file_path, dest_path)
                self.set_pet_avatar(dest_name)
            except Exception as e:
                print(f"[Widget] Error copying pet avatar: {e}")

    # --- Context Menu ---
    def _show_context_menu(self, pos: QPoint):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #12151b;
                color: #e2e8f0;
                border: 1px solid #2d3440;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 20px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #222938;
                color: #10b981;
            }
            QMenu::separator {
                height: 1px;
                background-color: #222730;
                margin: 4px 6px;
            }
        """)

        # --- Pet Submenu ---
        pet_menu = menu.addMenu(t("pet_menu", self.language))
        act_show_pet = pet_menu.addAction(t("show_pet", self.language))
        act_show_pet.setCheckable(True)
        act_show_pet.setChecked(self.show_pet)
        act_show_pet.triggered.connect(self.toggle_pet)
        pet_menu.addSeparator()

        available_pets = ElliotPet.get_available_pets(self.language)
        for display_name, file_name, file_path in available_pets:
            act_p = pet_menu.addAction(display_name)
            act_p.setCheckable(True)
            act_p.setChecked(self.current_pet == file_name)
            act_p.triggered.connect(lambda _, fn=file_name: self.set_pet_avatar(fn))

        pet_menu.addSeparator()
        act_add_pet = pet_menu.addAction(t("add_custom_pet", self.language))
        act_add_pet.triggered.connect(self.add_custom_pet_dialog)

        if self.show_pet:
            if self.pet_detached:
                act_dock = menu.addAction(t("attach_pet", self.language))
            else:
                act_dock = menu.addAction(t("detach_pet", self.language))
            act_dock.triggered.connect(self.toggle_pet_detach)

            scale_menu = menu.addMenu(t("pet_scale_menu", self.language))
            for s_val, s_lbl in [
                (0.75, t("scale_small", self.language)),
                (1.0, t("scale_normal", self.language)),
                (1.25, t("scale_large", self.language)),
                (1.5, t("scale_huge", self.language))
            ]:
                act_s = scale_menu.addAction(s_lbl)
                act_s.setCheckable(True)
                act_s.setChecked(abs(self.pet_scale - s_val) < 0.05)
                act_s.triggered.connect(lambda _, v=s_val: self.set_pet_scale(v))

        # --- Limit Rows Setup Menu ---
        limit_menu = menu.addMenu(t("limits_menu", self.language))

        act_def = limit_menu.addAction(t("preset_weekly_5h", self.language))
        act_def.setCheckable(True)
        act_def.setChecked(self.limit_rows == ["weekly", "5hour"])
        act_def.triggered.connect(lambda: self.set_limit_rows(["weekly", "5hour"]))

        act_claude_5h = limit_menu.addAction(t("preset_5h_claude", self.language))
        act_claude_5h.setCheckable(True)
        act_claude_5h.setChecked(self.limit_rows == ["5hour", "claude_gpt"])
        act_claude_5h.triggered.connect(lambda: self.set_limit_rows(["5hour", "claude_gpt"]))

        act_all = limit_menu.addAction(t("preset_all_three", self.language))
        act_all.setCheckable(True)
        act_all.setChecked(self.limit_rows == ["weekly", "5hour", "claude_gpt"])
        act_all.triggered.connect(lambda: self.set_limit_rows(["weekly", "5hour", "claude_gpt"]))

        limit_menu.addSeparator()

        row_names = {
            "weekly": t("weekly_limit", self.language),
            "5hour": t("five_hour_limit", self.language),
            "claude_gpt": t("claude_gpt_limit", self.language),
            "claude_weekly": t("claude_weekly_limit", self.language)
        }

        # Submenu for Row 1
        row1_menu = limit_menu.addMenu(t("row_1", self.language))
        for k, lbl in row_names.items():
            act_r1 = row1_menu.addAction(lbl)
            act_r1.setCheckable(True)
            act_r1.setChecked(len(self.limit_rows) > 0 and self.limit_rows[0] == k)
            act_r1.triggered.connect(lambda _, key=k: self._set_row_at(0, key))

        # Submenu for Row 2
        row2_menu = limit_menu.addMenu(t("row_2", self.language))
        for k, lbl in row_names.items():
            act_r2 = row2_menu.addAction(lbl)
            act_r2.setCheckable(True)
            act_r2.setChecked(len(self.limit_rows) > 1 and self.limit_rows[1] == k)
            act_r2.triggered.connect(lambda _, key=k: self._set_row_at(1, key))

        limit_menu.addSeparator()
        has_3_rows = len(self.limit_rows) >= 3
        act_toggle_3 = limit_menu.addAction(t("remove_third_row", self.language) if has_3_rows else t("add_third_row", self.language))
        act_toggle_3.triggered.connect(self._toggle_third_row)

        op_menu = menu.addMenu(t("opacity_menu", self.language))
        for val, lbl in [(1.0, "100%"), (0.95, "95%"), (0.85, "85%"), (0.70, "70%"), (0.50, "50%")]:
            act = op_menu.addAction(lbl)
            act.setCheckable(True)
            act.setChecked(abs(self.windowOpacity() - val) < 0.03)
            act.triggered.connect(lambda _, v=val: self.set_widget_opacity(v))

        menu.addSeparator()

        act_refresh = menu.addAction(t("refresh_now", self.language))
        act_refresh.triggered.connect(self.request_refresh.emit)

        act_reset = menu.addAction(t("reset_position", self.language))
        act_reset.triggered.connect(self.reset_position)

        act_settings = menu.addAction(t("open_settings", self.language))
        act_settings.triggered.connect(self.open_settings_requested.emit)

        menu.addSeparator()

        act_quit = menu.addAction(t("quit", self.language))
        act_quit.triggered.connect(self.quit_app.emit)

        menu.exec_(pos)

    def toggle_pet(self):
        self.show_pet = not self.show_pet
        self.pet.setVisible(self.show_pet)
        if not self.show_pet and self.pet_detached:
            self.pet.hide()
        self._recalculate_size()
        self.pet_toggled.emit(self.show_pet)
        self.update()

    def toggle_pet_detach(self):
        self.pet_detached = not self.pet_detached
        self.pet.hide()

        if self.pet_detached:
            # Detach: re-parent to None (own top-level window)
            global_pos = self.pet.mapToGlobal(QPoint(0, 0))
            self.pet.setParent(None)
            self.pet.set_detached(True)
            self.pet.move(global_pos)
            self.pet.show()
        else:
            # Dock: re-parent back to this widget
            self.pet.set_detached(False)
            self.pet.setParent(self)
            self.pet.show()

        self._recalculate_size()
        self.pet_detach_toggled.emit(self.pet_detached)
        self.update()

    def set_pet_scale(self, scale: float):
        self.pet_scale = scale
        self.config["pet_scale"] = scale
        self.pet.set_scale(scale)
        self._recalculate_size()
        self.pet_scale_changed.emit(scale)
        self.update()

    def set_widget_opacity(self, val: float):
        self.setWindowOpacity(val)
        self.opacity_changed.emit(val)

    def reset_position(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = 50
        self.move(x, y)
        self.position_changed.emit(x, y)

    # --- Paint Event ---
    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

        if self.show_pet and not self.pet_detached:
            pet_w = int(round(76 * self.pet_scale))
            pet_offset = pet_w + 8
        else:
            pet_offset = 6
        num_rows = len(self.limit_rows)
        pill_w = 356
        pill_h = 88 if num_rows <= 2 else 88 + (num_rows - 2) * 26
        pill_y = max(6.0, (self.height() - pill_h) / 2.0)
        pill_rect = QRectF(pet_offset, pill_y, pill_w, pill_h)

        # 1. Background (Dark glassmorphism pill with subtle border)
        bg_base = QtGui.QColor(self.color_bg)
        bg_grad = QtGui.QLinearGradient(pill_rect.left(), pill_rect.top(), pill_rect.left(), pill_rect.bottom())
        bg_grad.setColorAt(0.0, QtGui.QColor(bg_base.red(), bg_base.green(), bg_base.blue(), 245))
        bg_grad.setColorAt(1.0, QtGui.QColor(max(0, bg_base.red() - 6), max(0, bg_base.green() - 7), max(0, bg_base.blue() - 9), 250))
        
        # Subtle glowing glass border
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 22), 1.0))
        p.setBrush(bg_grad)
        p.drawRoundedRect(pill_rect, 12.0, 12.0)

        # 2. Header Row
        font_title = QtGui.QFont(self.font_family, max(8, self.font_size + 1), QtGui.QFont.DemiBold)
        p.setFont(font_title)
        p.setPen(QtGui.QColor("#f8fafc"))
        title_text = t("app_title", self.language)
        p.drawText(QRectF(pill_rect.left() + 16, pill_rect.top() + 8, 250, 18), Qt.AlignLeft | Qt.AlignVCenter, title_text)

        # 3. Quota Bars (Dynamic rows based on self.limit_rows)
        default_labels = {
            "weekly": (t("weekly_limit", self.language), 1.0, t("resets_mon", self.language)),
            "5hour": (t("five_hour_limit", self.language), 0.29, t("resets_unknown", self.language)),
            "claude_gpt": (t("claude_gpt_limit", self.language), 1.0, t("resets_unknown", self.language)),
            "claude_weekly": (t("claude_weekly_limit", self.language), 1.0, t("resets_unknown", self.language)),
        }

        row_y = pill_rect.top() + 30
        for idx, row_key in enumerate(self.limit_rows):
            if idx >= len(self.bars):
                break
            bar_anim = self.bars[idx]
            item = self.snapshot.get_item(row_key) if self.snapshot else None
            if item:
                label_left = item.label
                pct_str = f"{item.percent}%"
                reset_str = item.reset_time_str
            else:
                d_lbl, d_frac, d_rst = default_labels.get(row_key, (row_key, 1.0, t("resets_unknown", self.language)))
                label_left = d_lbl
                pct_str = f"{int(d_frac * 100)}%"
                reset_str = d_rst

            # Text Row
            font_row = QtGui.QFont(self.font_family, max(7, self.font_size - 1), QtGui.QFont.Normal)
            p.setFont(font_row)
            p.setPen(QtGui.QColor("#94a3b8"))
            p.drawText(QRectF(pill_rect.left() + 16, row_y, 140, 14), Qt.AlignLeft | Qt.AlignVCenter, label_left)

            # Percentage (Mint / Accent)
            font_pct = QtGui.QFont(self.font_family, max(7, self.font_size - 1), QtGui.QFont.DemiBold)
            p.setFont(font_pct)
            p.setPen(QtGui.QColor(bar_anim.color_hex))
            p.drawText(QRectF(pill_rect.right() - 175, row_y, 40, 14), Qt.AlignRight | Qt.AlignVCenter, pct_str)

            # Reset info (Muted)
            p.setFont(font_row)
            p.setPen(QtGui.QColor("#64748b"))
            p.drawText(QRectF(pill_rect.right() - 130, row_y, 114, 14), Qt.AlignRight | Qt.AlignVCenter, reset_str)

            # Progress Bar Track (Quotty style rounded capsule)
            track_y = row_y + 15
            track_w = 324
            track_h = 7.5
            track_rect = QRectF(pill_rect.left() + 16, track_y, track_w, track_h)

            p.setPen(Qt.NoPen)
            p.setBrush(QtGui.QColor("#242a35"))
            p.drawRoundedRect(track_rect, track_h / 2.0, track_h / 2.0)

            # Fill bar
            clamped_fraction = max(0.0, min(1.0, bar_anim.current_fraction))
            fill_w = max(track_h, track_w * clamped_fraction)
            fill_rect = QRectF(track_rect.left(), track_rect.top(), fill_w, track_h)

            # Breathing subtle pulse for the fill bar
            pulse_brightness = int(math.sin(self.pulse_phase * 1.5 + idx * 1.2) * 6) if self.animations_enabled else 0
            base_col = QtGui.QColor(bar_anim.color_hex)
            fill_grad = QtGui.QLinearGradient(fill_rect.left(), fill_rect.top(), fill_rect.right(), fill_rect.bottom())
            fill_grad.setColorAt(0.0, base_col.lighter(112 + pulse_brightness))
            fill_grad.setColorAt(1.0, base_col.lighter(100 + pulse_brightness))
            p.setBrush(fill_grad)
            p.drawRoundedRect(fill_rect, track_h / 2.0, track_h / 2.0)

            # Update particles & shimmer
            bar_anim.update(
                0.016,
                fill_rect,
                color_healthy=self.color_bar_healthy,
                color_warning=self.color_bar_warning,
                color_critical=self.color_bar_critical,
                animations_enabled=self.animations_enabled,
                shimmer_enabled=self.shimmer_enabled,
                particles_enabled=self.particles_enabled
            )

            # Clip path for all inner bar effects (particles and shimmer)
            clip_path = QtGui.QPainterPath()
            clip_path.addRoundedRect(fill_rect, track_h / 2.0, track_h / 2.0)

            # 1) White light shimmer animation (sleek glowing angled beam sweeping across the bar)
            if self.animations_enabled and self.shimmer_enabled and clamped_fraction > 0.03:
                shimmer_w = max(55.0, fill_w * 0.35)
                sweep_dist = fill_w + shimmer_w * 2.0
                sweep_x = fill_rect.left() - shimmer_w + sweep_dist * bar_anim.shimmer_phase

                # Angled light sweep
                shimmer_grad = QtGui.QLinearGradient(
                    sweep_x - 15, fill_rect.top(),
                    sweep_x + shimmer_w + 15, fill_rect.bottom()
                )
                shimmer_grad.setColorAt(0.0, QtGui.QColor(255, 255, 255, 0))
                shimmer_grad.setColorAt(0.35, QtGui.QColor(255, 255, 255, 50))
                shimmer_grad.setColorAt(0.5, QtGui.QColor(255, 255, 255, 190))
                shimmer_grad.setColorAt(0.65, QtGui.QColor(255, 255, 255, 50))
                shimmer_grad.setColorAt(1.0, QtGui.QColor(255, 255, 255, 0))

                p.save()
                p.setClipPath(clip_path)
                p.setPen(Qt.NoPen)
                p.setBrush(shimmer_grad)
                p.drawRect(QRectF(sweep_x - 25, fill_rect.top(), shimmer_w + 50, track_h))
                p.restore()

            # 2) Floating luminous particles CLIPPED to the fill capsule
            if self.animations_enabled and self.particles_enabled:
                p.save()
                p.setClipPath(clip_path)
                p.setPen(Qt.NoPen)
                for pt in bar_anim.particles:
                    curr_alpha = int(pt.base_alpha * (0.75 + 0.25 * math.sin(pt.pulse_phase)))
                    curr_alpha = max(90, min(255, curr_alpha))
                    # Soft luminous aura
                    glow_alpha = max(15, min(95, int(curr_alpha * 0.35)))
                    p.setBrush(QtGui.QColor(255, 255, 255, glow_alpha))
                    p.drawEllipse(QPointF(pt.x, pt.y), pt.radius + 1.2, pt.radius + 1.2)
                    # Bright white core
                    p.setBrush(QtGui.QColor(255, 255, 255, curr_alpha))
                    p.drawEllipse(QPointF(pt.x, pt.y), pt.radius, pt.radius)
                p.restore()

            row_y += 26
