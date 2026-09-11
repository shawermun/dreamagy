"""
System Tray Manager for Dreamagy.
Provides an icon in the Windows notification area with live quota tooltips
and a quick context menu.
"""

from typing import Optional
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from src.core.antigravity_provider import QuotaSnapshot
from src.core.i18n import t


def create_tray_icon(percent: int = 100, is_online: bool = True) -> QtGui.QIcon:
    """Generates a sleek 64x64 icon for the Windows taskbar tray."""
    pixmap = QtGui.QPixmap(64, 64)
    pixmap.fill(Qt.transparent)

    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

    # Outer dark circle
    painter.setBrush(QtGui.QColor("#111317"))
    painter.setPen(QtGui.QPen(QtGui.QColor("#2d3440"), 2))
    painter.drawEllipse(4, 4, 56, 56)

    # Arc gauge indicating percentage
    if is_online:
        color = QtGui.QColor("#10b981") if percent > 40 else (QtGui.QColor("#f59e0b") if percent > 15 else QtGui.QColor("#ef4444"))
        pen = QtGui.QPen(color, 5, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        span_angle = int((percent / 100.0) * 360 * 16)
        painter.drawArc(8, 8, 48, 48, 90 * 16, -span_angle)

        # Inner percentage text or AG mark
        painter.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        painter.setPen(QtGui.QColor("#f8fafc"))
        painter.drawText(QtCore.QRectF(0, 0, 64, 64), Qt.AlignCenter, f"{percent}")
    else:
        painter.setFont(QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold))
        painter.setPen(QtGui.QColor("#64748b"))
        painter.drawText(QtCore.QRectF(0, 0, 64, 64), Qt.AlignCenter, "OFF")

    painter.end()
    return QtGui.QIcon(pixmap)


class DreamagyTray(QtWidgets.QSystemTrayIcon):
    """System tray icon with menu and toggle actions."""
    toggle_widget = QtCore.pyqtSignal()
    request_refresh = QtCore.pyqtSignal()
    open_settings_requested = QtCore.pyqtSignal()
    quit_app = QtCore.pyqtSignal()

    def __init__(self, language: str = "ru", parent=None):
        super().__init__(parent)
        self.language = language
        self.last_snapshot: Optional[QuotaSnapshot] = None
        self.setIcon(create_tray_icon(100, False))
        self.setToolTip(f"Dreamagy ({t('connecting', self.language)})")

        # Menu
        self.menu = QtWidgets.QMenu()
        self.menu.setStyleSheet("""
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

        self.act_show = self.menu.addAction(t("tray_toggle", self.language))
        self.act_show.triggered.connect(self.toggle_widget.emit)

        self.act_settings = self.menu.addAction(t("tray_settings", self.language))
        self.act_settings.triggered.connect(self.open_settings_requested.emit)

        self.act_refresh = self.menu.addAction(t("tray_refresh", self.language))
        self.act_refresh.triggered.connect(self.request_refresh.emit)

        self.menu.addSeparator()

        self.act_quit = self.menu.addAction(t("tray_quit", self.language))
        self.act_quit.triggered.connect(self.quit_app.emit)

        self.setContextMenu(self.menu)
        self.activated.connect(self._on_tray_activated)

    def apply_settings(self, cfg: dict):
        """Applies configuration updates (e.g. language)."""
        self.language = cfg.get("language", self.language)
        self.act_show.setText(t("tray_toggle", self.language))
        self.act_settings.setText(t("tray_settings", self.language))
        self.act_refresh.setText(t("tray_refresh", self.language))
        self.act_quit.setText(t("tray_quit", self.language))
        if self.last_snapshot:
            self.update_status(self.last_snapshot)
        else:
            self.setToolTip(f"Dreamagy ({t('connecting', self.language)})")

    def _on_tray_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger: # Left click
            self.toggle_widget.emit()

    def update_status(self, snapshot: QuotaSnapshot):
        """Updates tray icon and tooltip based on snapshot."""
        self.last_snapshot = snapshot
        if snapshot and snapshot.online and snapshot.items:
            first_pct = snapshot.items[0].percent
            self.setIcon(create_tray_icon(first_pct, True))
            
            lines = [f"{t('app_title', self.language)}: {t('online', self.language)}"]
            for it in snapshot.items:
                lines.append(f"{it.group_name}: {it.percent}% ({it.reset_time_str})")
            self.setToolTip("\n".join(lines))
        else:
            self.setIcon(create_tray_icon(0, False))
            self.setToolTip(f"{t('app_title', self.language)}: {t('offline', self.language)}")
