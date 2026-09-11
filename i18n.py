"""
Localization / Internationalization (i18n) module for Dreamagy.
Supports Russian (ru), English (en), and Simplified Chinese (zh).
"""

TRANSLATIONS = {
    "ru": {
        "app_title": "Antigravity",
        "weekly_limit": "Недельные лимиты",
        "five_hour_limit": "5-ти часовые",
        "claude_gpt_limit": "Claude & GPT",
        "claude_weekly_limit": "Claude & GPT (Недельный)",
        "weekly_group": "Недельный",
        "resets_mon": "Сброс Пн 00:00",
        "resets_prefix": "Сброс",
        "resets_format": "Сброс {time} · {rem}",
        "resets_unknown": "Сброс --:--",
        "time_d": "д",
        "time_h": "ч",
        "time_m": "м",
        "offline": "Офлайн",
        "online": "Онлайн",
        "connecting": "Подключение...",
        
        # Context menu
        "pet_menu": "🐾 Выбор питомца",
        "pet_elliot_live": "🎬 Эллиот (Живое видео)",
        "pet_elliot_photo": "📸 Эллиот (Фото)",
        "pet_catalog_menu": "📥 Скачать из каталога...",
        "pet_downloading": "⏳ Загрузка питомца...",
        "pet_download_success": "Питомец '{}' успешно установлен!",
        "pet_download_error": "Ошибка загрузки: {}",
        "show_pet": "Показывать питомца",
        "add_custom_pet": "➕ Добавить своего питомца...",
        "attach_pet": "📌 Прикрепить к плашке",
        "detach_pet": "🔓 Отстегнуть от плашки",
        "pet_scale_menu": "🔍 Размер питомца",
        "scale_small": "Маленький (0.75x)",
        "scale_normal": "Нормальный (1.0x)",
        "scale_large": "Большой (1.25x)",
        "scale_huge": "Огромный (1.5x)",
        
        "limits_menu": "📊 Настройка лимитов",
        "preset_weekly_5h": "Недельные + 5-ти часовые (По умолчанию)",
        "preset_5h_claude": "5-ти часовые + Claude & GPT",
        "preset_all_three": "Все 3 лимита (Недельные, 5h, Claude & GPT)",
        "row_1": "Строка 1",
        "row_2": "Строка 2",
        "add_third_row": "Добавить 3-ю строку лимитов",
        "remove_third_row": "Убрать 3-ю строку лимитов",
        
        "opacity_menu": "👁 Прозрачность",
        "refresh_now": "🔄 Обновить лимиты сейчас",
        "reset_position": "⚙ Сбросить позицию на экране",
        "open_settings": "⚙ Настройки оформления и языка...",
        "quit": "❌ Выход",
        
        # Settings Dialog
        "settings_dialog_title": "Настройки Dreamagy",
        "tab_appearance": "🎨 Оформление",
        "tab_typography": "🔤 Шрифт",
        "tab_animations": "✨ Анимации",
        "tab_language": "🌐 Язык",
        
        "color_bg_label": "Цвет фона плашки:",
        "color_healthy_label": "Цвет шкалы (нормальный > 40%):",
        "color_warning_label": "Цвет шкалы (внимание 15-40%):",
        "color_critical_label": "Цвет шкалы (критический < 15%):",
        "btn_reset_colors": "Сбросить цвета по умолчанию",
        
        "font_family_label": "Шрифт интерфейса:",
        "font_size_label": "Размер шрифта:",
        "btn_browse_fonts": "Обзор...",
        "preview_text": "Antigravity · Недельные лимиты 100% · 5-ти часовые 84%",
        
        "anim_master_label": "Включить все анимации",
        "anim_shimmer_label": "Световой перелив шкал (Shimmer)",
        "anim_particles_label": "Плавающие частицы внутри шкал",
        "anim_pet_label": "Живые анимации питомца (капюшон, наклон головы, моргание)",
        
        "language_select_label": "Выберите язык интерфейса:",
        "btn_save": "Сохранить",
        "btn_apply": "Применить",
        "btn_cancel": "Отмена",
        
        # Tray
        "tray_toggle": "👁 Показать / Скрыть виджет",
        "tray_refresh": "🔄 Обновить лимиты",
        "tray_settings": "⚙ Настройки...",
        "tray_quit": "❌ Выход"
    },
    
    "en": {
        "app_title": "Antigravity",
        "weekly_limit": "Weekly limits",
        "five_hour_limit": "5-hour limit",
        "claude_gpt_limit": "Claude & GPT",
        "claude_weekly_limit": "Claude & GPT (Weekly)",
        "weekly_group": "Weekly",
        "resets_mon": "Resets Mon 00:00",
        "resets_prefix": "Resets",
        "resets_format": "Resets {time} · {rem}",
        "resets_unknown": "Resets --:--",
        "time_d": "d",
        "time_h": "h",
        "time_m": "m",
        "offline": "Offline",
        "online": "Online",
        "connecting": "Connecting...",
        
        # Context menu
        "pet_menu": "🐾 Choose Companion",
        "pet_elliot_live": "🎬 Elliot (Live Video)",
        "pet_elliot_photo": "📸 Elliot (Photo)",
        "pet_catalog_menu": "📥 Download from Catalog...",
        "pet_downloading": "⏳ Downloading companion...",
        "pet_download_success": "Pet '{}' downloaded successfully!",
        "pet_download_error": "Download error: {}",
        "show_pet": "Show Companion",
        "add_custom_pet": "➕ Add custom companion...",
        "attach_pet": "📌 Dock to Widget",
        "detach_pet": "🔓 Detach Window",
        "pet_scale_menu": "🔍 Companion Scale",
        "scale_small": "Small (0.75x)",
        "scale_normal": "Normal (1.0x)",
        "scale_large": "Large (1.25x)",
        "scale_huge": "Huge (1.5x)",
        
        "limits_menu": "📊 Quota Setup",
        "preset_weekly_5h": "Weekly + 5-hour (Default)",
        "preset_5h_claude": "5-hour + Claude & GPT",
        "preset_all_three": "All 3 Limits (Weekly, 5h, Claude & GPT)",
        "row_1": "Row 1",
        "row_2": "Row 2",
        "add_third_row": "Add 3rd Limit Row",
        "remove_third_row": "Remove 3rd Limit Row",
        
        "opacity_menu": "👁 Opacity",
        "refresh_now": "🔄 Refresh Quotas Now",
        "reset_position": "⚙ Reset Screen Position",
        "open_settings": "⚙ Settings & Language...",
        "quit": "❌ Quit",
        
        # Settings Dialog
        "settings_dialog_title": "Dreamagy Settings",
        "tab_appearance": "🎨 Appearance",
        "tab_typography": "🔤 Typography",
        "tab_animations": "✨ Animations",
        "tab_language": "🌐 Language",
        
        "color_bg_label": "Pill Background Color:",
        "color_healthy_label": "Healthy Bar Color (> 40%):",
        "color_warning_label": "Warning Bar Color (15-40%):",
        "color_critical_label": "Critical Bar Color (< 15%):",
        "btn_reset_colors": "Reset to Defaults",
        
        "font_family_label": "Interface Font:",
        "font_size_label": "Font Size:",
        "btn_browse_fonts": "Browse...",
        "preview_text": "Antigravity · Weekly limits 100% · 5-hour limit 84%",
        
        "anim_master_label": "Enable All Animations",
        "anim_shimmer_label": "White Light Shimmer Sweep",
        "anim_particles_label": "Floating Luminous Particles",
        "anim_pet_label": "Lifelike Companion Motion (hood, head tilt, blinks)",
        
        "language_select_label": "Choose Interface Language:",
        "btn_save": "Save",
        "btn_apply": "Apply",
        "btn_cancel": "Cancel",
        
        # Tray
        "tray_toggle": "👁 Show / Hide Widget",
        "tray_refresh": "🔄 Refresh Quotas",
        "tray_settings": "⚙ Settings...",
        "tray_quit": "❌ Quit"
    },
    
    "zh": {
        "app_title": "Antigravity",
        "weekly_limit": "周限额",
        "five_hour_limit": "5小时限额",
        "claude_gpt_limit": "Claude & GPT",
        "claude_weekly_limit": "Claude & GPT (周限额)",
        "weekly_group": "周限额",
        "resets_mon": "重置于 周一 00:00",
        "resets_prefix": "重置于",
        "resets_format": "重置于 {time} · {rem}",
        "resets_unknown": "重置于 --:--",
        "time_d": "天",
        "time_h": "时",
        "time_m": "分",
        "offline": "离线",
        "online": "在线",
        "connecting": "连接中...",
        
        # Context menu
        "pet_menu": "🐾 伴侣宠物选择",
        "pet_elliot_live": "🎬 艾略特 (动态视频)",
        "pet_elliot_photo": "📸 艾略特 (静态照片)",
        "pet_catalog_menu": "📥 从目录下载宠物...",
        "pet_downloading": "⏳ 正在下载伴侣...",
        "pet_download_success": "宠物伴侣 '{}' 下载并安装成功！",
        "pet_download_error": "下载错误: {}",
        "show_pet": "显示宠物伴侣",
        "add_custom_pet": "➕ 添加自定义宠物...",
        "attach_pet": "📌 固定在面板旁",
        "detach_pet": "🔓 独立浮动窗口",
        "pet_scale_menu": "🔍 宠物缩放比例",
        "scale_small": "较小 (0.75x)",
        "scale_normal": "正常 (1.0x)",
        "scale_large": "较大 (1.25x)",
        "scale_huge": "巨大 (1.5x)",
        
        "limits_menu": "📊 限额面板设置",
        "preset_weekly_5h": "周限额 + 5小时限额 (默认)",
        "preset_5h_claude": "5小时限额 + Claude & GPT",
        "preset_all_three": "显示全部3项限额 (周限额, 5h, Claude & GPT)",
        "row_1": "第一行",
        "row_2": "第二行",
        "add_third_row": "添加第3行限额",
        "remove_third_row": "移除第3行限额",
        
        "opacity_menu": "👁 透明度",
        "refresh_now": "🔄 立即刷新配额",
        "reset_position": "⚙ 重置屏幕位置",
        "open_settings": "⚙ 外观与语言设置...",
        "quit": "❌ 退出",
        
        # Settings Dialog
        "settings_dialog_title": "Dreamagy 设置",
        "tab_appearance": "🎨 外观",
        "tab_typography": "🔤 字体",
        "tab_animations": "✨ 动效",
        "tab_language": "🌐 语言",
        
        "color_bg_label": "面板背景颜色:",
        "color_healthy_label": "正常配额条颜色 (> 40%):",
        "color_warning_label": "警示配额条颜色 (15-40%):",
        "color_critical_label": "临界配额条颜色 (< 15%):",
        "btn_reset_colors": "恢复默认颜色",
        
        "font_family_label": "界面字体:",
        "font_size_label": "字体大小:",
        "btn_browse_fonts": "浏览...",
        "preview_text": "Antigravity · 周限额 100% · 5小时限额 84%",
        
        "anim_master_label": "开启所有动效",
        "anim_shimmer_label": "进度条白色光晕扫光 (Shimmer)",
        "anim_particles_label": "内部发光微粒浮动",
        "anim_pet_label": "宠物生动动作 (整理兜帽、侧头思考、自然眨眼)",
        
        "language_select_label": "选择界面语言:",
        "btn_save": "保存",
        "btn_apply": "应用",
        "btn_cancel": "取消",
        
        # Tray
        "tray_toggle": "👁 显示 / 隐藏小部件",
        "tray_refresh": "🔄 刷新限额",
        "tray_settings": "⚙ 设置...",
        "tray_quit": "❌ 退出"
    }
}


def t(key: str, lang: str = "ru") -> str:
    """Translates key to target language. Falls back to Russian or key if missing."""
    lang_dict = TRANSLATIONS.get(lang) or TRANSLATIONS.get("ru", {})
    val = lang_dict.get(key)
    if val is not None:
        return val
    # Fallback to Russian
    ru_dict = TRANSLATIONS.get("ru", {})
    return ru_dict.get(key, key)
