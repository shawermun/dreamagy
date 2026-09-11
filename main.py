"""
Dreamagy Entry Point.
Launches the floating Quotty-inspired Antigravity quota monitor with Elliot Alderson pet.
"""

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal

from config import load_config, save_config
from antigravity_provider import AntigravityProvider, QuotaSnapshot
from widget import DreamagyWidget
from tray import DreamagyTray
from settings_dialog import SettingsDialog

try:
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class KeyboardActivityWatcher(QtCore.QObject):
    """Monitors global typing activity across all Windows apps using win32api.GetAsyncKeyState."""
    typing_detected = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._check_keys)
        # Check standard keys: alphanumeric, enter, space, backspace (exclude mouse and modifiers)
        self._keys = [k for k in range(8, 256) if k not in (0x10, 0x11, 0x12, 0x14, 0x5B, 0x5C)]

    def start(self):
        if HAS_WIN32:
            self._timer.start(50)

    def stop(self):
        self._timer.stop()

    def _check_keys(self):
        if not HAS_WIN32:
            return
        for k in self._keys:
            state = win32api.GetAsyncKeyState(k)
            if (state & 0x8000) or (state & 0x0001):
                self.typing_detected.emit()
                break


class QuotaWorker(QThread):
    """Background worker thread to query Antigravity language server without UI lag."""
    quota_updated = pyqtSignal(object)

    def __init__(self, interval_seconds: int = 15, lang: str = "ru"):
        super().__init__()
        self.interval = interval_seconds
        self.provider = AntigravityProvider(lang=lang)
        self._running = True
        self._force_refresh = False

    def trigger_now(self):
        self._force_refresh = True

    def run(self):
        while self._running:
            try:
                snapshot = self.provider.fetch_status()
                self.quota_updated.emit(snapshot)
            except Exception as e:
                print(f"[Worker] Error fetching quota: {e}")

            # Sleep in increments of 0.2s to be responsive to trigger_now
            slept = 0.0
            while slept < self.interval and self._running and not self._force_refresh:
                self.msleep(200)
                slept += 0.2

            self._force_refresh = False

    def stop(self):
        self._running = False
        self.wait(1000)


class DreamagyApp:
    def __init__(self):
        self.cfg = load_config()
        self.widget = DreamagyWidget(self.cfg)
        self.tray = DreamagyTray(language=self.cfg.get("language", "ru"))
        self.settings_dialog = SettingsDialog(self.cfg)

        # Background worker
        refresh_sec = self.cfg.get("refresh_seconds", 15)
        self.worker = QuotaWorker(interval_seconds=refresh_sec, lang=self.cfg.get("language", "ru"))

        # Global keyboard listener for typing reaction
        self.keyboard_watcher = KeyboardActivityWatcher()
        self.keyboard_watcher.typing_detected.connect(self.widget.pet.on_keyboard_activity)

        # Wire signals
        self.worker.quota_updated.connect(self._on_quota_updated)

        self.widget.position_changed.connect(self._on_pos_changed)
        self.widget.opacity_changed.connect(self._on_opacity_changed)
        self.widget.pet_toggled.connect(self._on_pet_toggled)
        self.widget.pet_detach_toggled.connect(self._on_pet_detach_toggled)
        self.widget.pet_scale_changed.connect(self._on_pet_scale_changed)
        self.widget.pet_avatar_changed.connect(self._on_pet_avatar_changed)
        self.widget.limit_rows_changed.connect(self._on_limit_rows_changed)
        self.widget.open_settings_requested.connect(self._on_open_settings)
        self.widget.request_refresh.connect(self.worker.trigger_now)
        self.widget.quit_app.connect(self._on_quit)

        self.tray.toggle_widget.connect(self._on_toggle_widget)
        self.tray.open_settings_requested.connect(self._on_open_settings)
        self.tray.request_refresh.connect(self.worker.trigger_now)
        self.tray.quit_app.connect(self._on_quit)

        self.settings_dialog.settings_saved.connect(self._on_settings_saved)

    def start(self):
        self.widget.show()
        # If pet is detached, show it as independent window
        if self.cfg.get("show_pet", True) and self.cfg.get("pet_detached", False):
            self.widget.pet.show()
        self.tray.show()
        self.keyboard_watcher.start()
        self.worker.start()

    def _on_quota_updated(self, snapshot: QuotaSnapshot):
        self.widget.update_snapshot(snapshot)
        self.tray.update_status(snapshot)

    def _on_open_settings(self):
        self.settings_dialog.cfg = dict(self.cfg)
        self.settings_dialog._load_values()
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def _on_settings_saved(self, new_cfg: dict):
        self.cfg.update(new_cfg)
        save_config(self.cfg)
        self.worker.provider.set_language(self.cfg.get("language", "ru"))
        self.widget.apply_settings(self.cfg)
        self.tray.apply_settings(self.cfg)
        self.worker.trigger_now()

    def _on_pos_changed(self, x: int, y: int):
        self.cfg["pos_x"] = x
        self.cfg["pos_y"] = y
        save_config(self.cfg)

    def _on_opacity_changed(self, val: float):
        self.cfg["opacity"] = val
        save_config(self.cfg)

    def _on_pet_toggled(self, visible: bool):
        self.cfg["show_pet"] = visible
        save_config(self.cfg)

    def _on_pet_detach_toggled(self, detached: bool):
        self.cfg["pet_detached"] = detached
        if detached:
            self.cfg["pet_pos_x"] = self.widget.pet.x()
            self.cfg["pet_pos_y"] = self.widget.pet.y()
        save_config(self.cfg)

    def _on_pet_scale_changed(self, scale: float):
        self.cfg["pet_scale"] = scale
        save_config(self.cfg)

    def _on_pet_avatar_changed(self, avatar: str):
        self.cfg["current_pet"] = avatar
        save_config(self.cfg)

    def _on_limit_rows_changed(self, rows: list):
        self.cfg["limit_rows"] = rows
        save_config(self.cfg)

    def _on_toggle_widget(self):
        if self.widget.isVisible():
            self.widget.hide()
        else:
            self.widget.show()
            self.widget.raise_()
            self.widget.activateWindow()

    def _on_quit(self):
        # Save pet position before quitting
        if self.cfg.get("pet_detached", False):
            self.cfg["pet_pos_x"] = self.widget.pet.x()
            self.cfg["pet_pos_y"] = self.widget.pet.y()
            save_config(self.cfg)
        self.keyboard_watcher.stop()
        self.worker.stop()
        self.settings_dialog.close()
        self.widget.pet.hide()
        self.widget.close()
        self.tray.hide()
        QtWidgets.QApplication.quit()


def main():
    # Enable High DPI scaling
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Keep running in tray even if window hidden

    # Set default app font
    font = QtGui.QFont("Segoe UI", 9)
    app.setFont(font)

    dreamagy = DreamagyApp()
    dreamagy.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
