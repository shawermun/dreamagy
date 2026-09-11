"""
Settings Dialog for Dreamagy.
Allows customizing:
- Colors (Pill background, progress bar healthy/warning/critical)
- Typography (Font family, size, system font picker)
- Animations (Master switch, shimmer, particles, pet animations)
- Language (Russian, English, Simplified Chinese)
"""

from typing import Dict
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from src.core.i18n import t


class ColorButton(QtWidgets.QPushButton):
    """Button displaying a colored swatch and hex code, opening QColorDialog on click."""
    color_changed = pyqtSignal(str)

    def __init__(self, initial_hex: str, parent=None):
        super().__init__(parent)
        self._hex = initial_hex
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._pick_color)
        self._update_style()

    def get_color(self) -> str:
        return self._hex

    def set_color(self, hex_code: str):
        self._hex = hex_code
        self._update_style()

    def _update_style(self):
        self.setText(f"  {self._hex.upper()}  ")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #1a202c;
                color: #e2e8f0;
                border: 2px solid {self._hex};
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                font-weight: bold;
                padding-left: 10px;
                padding-right: 10px;
            }}
            QPushButton:hover {{
                background-color: #242d3d;
            }}
        """)

    def _pick_color(self):
        col = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._hex), self, "Select Color")
        if col.isValid():
            self._hex = col.name()
            self._update_style()
            self.color_changed.emit(self._hex)


class SettingsDialog(QtWidgets.QDialog):
    """Modern dark obsidian settings window for Dreamagy."""
    settings_saved = pyqtSignal(dict)

    def __init__(self, current_config: dict, parent=None):
        super().__init__(parent)
        self.cfg = dict(current_config)
        self.lang = self.cfg.get("language", "ru")

        self.setWindowTitle(t("settings_dialog_title", self.lang))
        self.setFixedSize(540, 440)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        self._build_ui()
        self._load_values()
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1217;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #232a36;
                border-radius: 8px;
                background-color: #141820;
                top: -1px;
                padding: 10px;
            }
            QTabBar::tab {
                background: #10141b;
                color: #94a3b8;
                border: 1px solid #1e2430;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 6px 12px;
                margin-right: 3px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background: #141820;
                color: #10b981;
                border-color: #2d3748;
            }
            QLabel {
                color: #cbd5e1;
                font-size: 12px;
            }
            QComboBox, QSpinBox {
                background-color: #1c222d;
                color: #f1f5f9;
                border: 1px solid #2d3748;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QCheckBox {
                color: #cbd5e1;
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid #3b4252;
                background: #181d26;
            }
            QCheckBox::indicator:checked {
                background-color: #10b981;
                border-color: #10b981;
                image: none;
            }
            QPushButton#ActionBtn {
                background-color: #10b981;
                color: #042f2e;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton#ActionBtn:hover {
                background-color: #34d399;
            }
            QPushButton#SecondaryBtn {
                background-color: #1f2735;
                color: #cbd5e1;
                border: 1px solid #2d3748;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton#SecondaryBtn:hover {
                background-color: #2b3547;
                color: #f8fafc;
            }
        """)

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.tabBar().setExpanding(False)
        self.tab_widget.tabBar().setElideMode(Qt.ElideNone)

        # 1. Appearance Tab
        self.tab_appearance = QtWidgets.QWidget()
        layout_app = QtWidgets.QFormLayout(self.tab_appearance)
        layout_app.setSpacing(12)
        layout_app.setContentsMargins(14, 14, 14, 14)
        layout_app.setLabelAlignment(Qt.AlignLeft)
        layout_app.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)

        self.btn_col_bg = ColorButton(self.cfg.get("color_bg", "#11151b"))
        self.btn_col_healthy = ColorButton(self.cfg.get("color_bar_healthy", "#34d399"))
        self.btn_col_warning = ColorButton(self.cfg.get("color_bar_warning", "#f59e0b"))
        self.btn_col_critical = ColorButton(self.cfg.get("color_bar_critical", "#ef4444"))

        self.lbl_col_bg = QtWidgets.QLabel(t("color_bg_label", self.lang))
        self.lbl_col_healthy = QtWidgets.QLabel(t("color_healthy_label", self.lang))
        self.lbl_col_warning = QtWidgets.QLabel(t("color_warning_label", self.lang))
        self.lbl_col_critical = QtWidgets.QLabel(t("color_critical_label", self.lang))

        for lbl in (self.lbl_col_bg, self.lbl_col_healthy, self.lbl_col_warning, self.lbl_col_critical):
            lbl.setMinimumWidth(210)

        layout_app.addRow(self.lbl_col_bg, self.btn_col_bg)
        layout_app.addRow(self.lbl_col_healthy, self.btn_col_healthy)
        layout_app.addRow(self.lbl_col_warning, self.btn_col_warning)
        layout_app.addRow(self.lbl_col_critical, self.btn_col_critical)

        self.btn_reset_colors = QtWidgets.QPushButton(t("btn_reset_colors", self.lang))
        self.btn_reset_colors.setObjectName("SecondaryBtn")
        self.btn_reset_colors.clicked.connect(self._reset_colors)
        layout_app.addRow("", self.btn_reset_colors)

        # 2. Typography Tab
        self.tab_typography = QtWidgets.QWidget()
        layout_type = QtWidgets.QVBoxLayout(self.tab_typography)
        layout_type.setSpacing(10)
        layout_type.setContentsMargins(14, 14, 14, 14)

        form_type = QtWidgets.QFormLayout()
        form_type.setSpacing(12)
        form_type.setLabelAlignment(Qt.AlignLeft)
        form_type.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)

        self.lbl_font_family = QtWidgets.QLabel(t("font_family_label", self.lang))
        self.lbl_font_family.setMinimumWidth(150)
        self.combo_font = QtWidgets.QComboBox()
        common_fonts = [
            "Segoe UI", "Inter", "Roboto", "Arial", "Consolas",
            "JetBrains Mono", "Fira Code", "Microsoft YaHei", "Calibri"
        ]
        self.combo_font.addItems(common_fonts)
        self.combo_font.currentTextChanged.connect(self._on_font_changed)

        self.btn_browse_fonts = QtWidgets.QPushButton(t("btn_browse_fonts", self.lang))
        self.btn_browse_fonts.setObjectName("SecondaryBtn")
        self.btn_browse_fonts.setFixedWidth(84)
        self.btn_browse_fonts.clicked.connect(self._browse_system_font)

        h_font_row = QtWidgets.QHBoxLayout()
        h_font_row.addWidget(self.combo_font, 1)
        h_font_row.addWidget(self.btn_browse_fonts)
        form_type.addRow(self.lbl_font_family, h_font_row)

        self.lbl_font_size = QtWidgets.QLabel(t("font_size_label", self.lang))
        self.lbl_font_size.setMinimumWidth(150)
        self.spin_font_size = QtWidgets.QSpinBox()
        self.spin_font_size.setRange(7, 14)
        self.spin_font_size.setValue(self.cfg.get("font_size", 9))
        self.spin_font_size.valueChanged.connect(self._on_font_changed)
        form_type.addRow(self.lbl_font_size, self.spin_font_size)

        layout_type.addLayout(form_type)

        # Preview box
        self.lbl_preview_header = QtWidgets.QLabel("Предпросмотр (Preview):")
        self.lbl_preview_header.setStyleSheet("color: #64748b; font-size: 11px; margin-top: 6px;")
        layout_type.addWidget(self.lbl_preview_header)

        self.preview_box = QtWidgets.QFrame()
        self.preview_box.setStyleSheet("""
            QFrame {
                background-color: #11151b;
                border: 1px solid #2d3748;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        preview_layout = QtWidgets.QVBoxLayout(self.preview_box)
        self.preview_label = QtWidgets.QLabel(t("preview_text", self.lang))
        self.preview_label.setStyleSheet("color: #f8fafc;")
        preview_layout.addWidget(self.preview_label)
        layout_type.addWidget(self.preview_box)
        layout_type.addStretch()

        # 3. Animations Tab
        self.tab_animations = QtWidgets.QWidget()
        layout_anim = QtWidgets.QVBoxLayout(self.tab_animations)
        layout_anim.setSpacing(12)
        layout_anim.setContentsMargins(14, 16, 14, 14)

        self.chk_master_anim = QtWidgets.QCheckBox(t("anim_master_label", self.lang))
        self.chk_master_anim.setStyleSheet("font-weight: bold; font-size: 13px; color: #10b981;")
        self.chk_master_anim.toggled.connect(self._on_master_anim_toggled)

        self.chk_shimmer = QtWidgets.QCheckBox(t("anim_shimmer_label", self.lang))
        self.chk_particles = QtWidgets.QCheckBox(t("anim_particles_label", self.lang))
        self.chk_pet_anim = QtWidgets.QCheckBox(t("anim_pet_label", self.lang))

        layout_anim.addWidget(self.chk_master_anim)
        layout_anim.addSpacing(4)
        sub_layout = QtWidgets.QVBoxLayout()
        sub_layout.setContentsMargins(24, 0, 0, 0)
        sub_layout.setSpacing(10)
        sub_layout.addWidget(self.chk_shimmer)
        sub_layout.addWidget(self.chk_particles)
        sub_layout.addWidget(self.chk_pet_anim)
        layout_anim.addLayout(sub_layout)
        layout_anim.addStretch()

        # 4. Language Tab
        self.tab_language = QtWidgets.QWidget()
        layout_lang = QtWidgets.QVBoxLayout(self.tab_language)
        layout_lang.setSpacing(14)
        layout_lang.setContentsMargins(14, 16, 14, 14)

        self.lbl_lang_select = QtWidgets.QLabel(t("language_select_label", self.lang))
        self.combo_lang = QtWidgets.QComboBox()
        self.combo_lang.addItem("🇷🇺 Русский", "ru")
        self.combo_lang.addItem("🇬🇧 English", "en")
        self.combo_lang.addItem("🇨🇳 简体中文", "zh")
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)

        layout_lang.addWidget(self.lbl_lang_select)
        layout_lang.addWidget(self.combo_lang)
        layout_lang.addStretch()

        # Add tabs
        self.tab_widget.addTab(self.tab_appearance, t("tab_appearance", self.lang))
        self.tab_widget.addTab(self.tab_typography, t("tab_typography", self.lang))
        self.tab_widget.addTab(self.tab_animations, t("tab_animations", self.lang))
        self.tab_widget.addTab(self.tab_language, t("tab_language", self.lang))
        main_layout.addWidget(self.tab_widget)

        # Bottom Buttons
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.setSpacing(8)

        self.btn_cancel = QtWidgets.QPushButton(t("btn_cancel", self.lang))
        self.btn_cancel.setObjectName("SecondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_apply = QtWidgets.QPushButton(t("btn_apply", self.lang))
        self.btn_apply.setObjectName("SecondaryBtn")
        self.btn_apply.clicked.connect(self._apply_changes)

        self.btn_save = QtWidgets.QPushButton(t("btn_save", self.lang))
        self.btn_save.setObjectName("ActionBtn")
        self.btn_save.clicked.connect(self._save_changes)

        btn_box.addStretch()
        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_apply)
        btn_box.addWidget(self.btn_save)
        main_layout.addLayout(btn_box)

    def _load_values(self):
        # Colors
        self.btn_col_bg.set_color(self.cfg.get("color_bg", "#11151b"))
        self.btn_col_healthy.set_color(self.cfg.get("color_bar_healthy", "#34d399"))
        self.btn_col_warning.set_color(self.cfg.get("color_bar_warning", "#f59e0b"))
        self.btn_col_critical.set_color(self.cfg.get("color_bar_critical", "#ef4444"))

        # Fonts
        curr_font = self.cfg.get("font_family", "Segoe UI")
        idx = self.combo_font.findText(curr_font)
        if idx >= 0:
            self.combo_font.setCurrentIndex(idx)
        else:
            self.combo_font.addItem(curr_font)
            self.combo_font.setCurrentText(curr_font)
        self.spin_font_size.setValue(self.cfg.get("font_size", 9))
        self._on_font_changed()

        # Animations
        self.chk_master_anim.setChecked(self.cfg.get("animations_enabled", True))
        self.chk_shimmer.setChecked(self.cfg.get("shimmer_enabled", True))
        self.chk_particles.setChecked(self.cfg.get("particles_enabled", True))
        self.chk_pet_anim.setChecked(self.cfg.get("pet_animations_enabled", True))
        self._on_master_anim_toggled(self.chk_master_anim.isChecked())

        # Language
        lang = self.cfg.get("language", "ru")
        self.lang = lang
        for i in range(self.combo_lang.count()):
            if self.combo_lang.itemData(i) == lang:
                self.combo_lang.setCurrentIndex(i)
                break
        self._retranslate_ui()

    def _on_master_anim_toggled(self, checked: bool):
        self.chk_shimmer.setEnabled(checked)
        self.chk_particles.setEnabled(checked)
        self.chk_pet_anim.setEnabled(checked)

    def _on_font_changed(self):
        family = self.combo_font.currentText()
        size = self.spin_font_size.value()
        f = QtGui.QFont(family, size)
        self.preview_label.setFont(f)

    def _browse_system_font(self):
        current_f = QtGui.QFont(self.combo_font.currentText(), self.spin_font_size.value())
        ok, font = QtWidgets.QFontDialog.getFont(current_f, self, "Select Font")
        if ok:
            family = font.family()
            size = font.pointSize()
            if self.combo_font.findText(family) < 0:
                self.combo_font.addItem(family)
            self.combo_font.setCurrentText(family)
            self.spin_font_size.setValue(size)
            self._on_font_changed()

    def _reset_colors(self):
        self.btn_col_bg.set_color("#11151b")
        self.btn_col_healthy.set_color("#34d399")
        self.btn_col_warning.set_color("#f59e0b")
        self.btn_col_critical.set_color("#ef4444")

    def _on_lang_changed(self, idx: int):
        new_lang = self.combo_lang.itemData(idx)
        if new_lang:
            self.lang = new_lang
            self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(t("settings_dialog_title", self.lang))
        self.tab_widget.setTabText(0, t("tab_appearance", self.lang))
        self.tab_widget.setTabText(1, t("tab_typography", self.lang))
        self.tab_widget.setTabText(2, t("tab_animations", self.lang))
        self.tab_widget.setTabText(3, t("tab_language", self.lang))

        self.lbl_col_bg.setText(t("color_bg_label", self.lang))
        self.lbl_col_healthy.setText(t("color_healthy_label", self.lang))
        self.lbl_col_warning.setText(t("color_warning_label", self.lang))
        self.lbl_col_critical.setText(t("color_critical_label", self.lang))
        self.btn_reset_colors.setText(t("btn_reset_colors", self.lang))

        self.lbl_font_family.setText(t("font_family_label", self.lang))
        self.btn_browse_fonts.setText(t("btn_browse_fonts", self.lang))
        self.lbl_font_size.setText(t("font_size_label", self.lang))
        self.preview_label.setText(t("preview_text", self.lang))

        self.chk_master_anim.setText(t("anim_master_label", self.lang))
        self.chk_shimmer.setText(t("anim_shimmer_label", self.lang))
        self.chk_particles.setText(t("anim_particles_label", self.lang))
        self.chk_pet_anim.setText(t("anim_pet_label", self.lang))

        self.lbl_lang_select.setText(t("language_select_label", self.lang))
        self.btn_cancel.setText(t("btn_cancel", self.lang))
        self.btn_apply.setText(t("btn_apply", self.lang))
        self.btn_save.setText(t("btn_save", self.lang))

    def get_settings(self) -> dict:
        return {
            "color_bg": self.btn_col_bg.get_color(),
            "color_bar_healthy": self.btn_col_healthy.get_color(),
            "color_bar_warning": self.btn_col_warning.get_color(),
            "color_bar_critical": self.btn_col_critical.get_color(),
            "font_family": self.combo_font.currentText(),
            "font_size": self.spin_font_size.value(),
            "animations_enabled": self.chk_master_anim.isChecked(),
            "shimmer_enabled": self.chk_shimmer.isChecked(),
            "particles_enabled": self.chk_particles.isChecked(),
            "pet_animations_enabled": self.chk_pet_anim.isChecked(),
            "language": self.combo_lang.currentData() or "ru"
        }

    def _apply_changes(self):
        new_settings = self.get_settings()
        self.cfg.update(new_settings)
        self.settings_saved.emit(self.cfg)

    def _save_changes(self):
        self._apply_changes()
        self.accept()
