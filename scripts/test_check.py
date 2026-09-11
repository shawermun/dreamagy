import sys
import os
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    from src.core.config import load_config, DEFAULT_CONFIG
    from src.core.antigravity_provider import AntigravityProvider
    from src.ui.widget import DreamagyWidget
    from src.pets.pet_elliot import ElliotPet, PetCompanionWidget
    from src.ui.tray import DreamagyTray, create_tray_icon
    from src.pets import pet_catalog

    app = QtWidgets.QApplication(sys.argv)
    cfg = load_config()
    
    # Verify new config fields exist
    assert "pet_detached" in DEFAULT_CONFIG, "pet_detached should be in DEFAULT_CONFIG"
    assert "pet_pos_x" in DEFAULT_CONFIG, "pet_pos_x should be in DEFAULT_CONFIG"
    assert "pet_pos_y" in DEFAULT_CONFIG, "pet_pos_y should be in DEFAULT_CONFIG"
    print("Config defaults OK")

    widget = DreamagyWidget(cfg)
    provider = AntigravityProvider()
    snap = provider.fetch_status()
    print("Snapshot fetched successfully:", snap.online, "Items:", len(snap.items))
    widget.update_snapshot(snap)
    print("Widget size:", widget.width(), widget.height())

    pix = QtGui.QPixmap(widget.size())
    pix.fill(QtCore.Qt.transparent)
    widget.render(pix)
    print("Widget rendered to QPixmap successfully!")

    widget.pet.trigger_glitch("hello test")
    pet_pix = QtGui.QPixmap(widget.pet.size())
    widget.pet.render(pet_pix)
    print("Pet rendered to QPixmap successfully!")

    # Check that pet photo asset was loaded
    if not widget.pet._photo.isNull():
        print(f"Pet photo loaded: {widget.pet._photo.width()}x{widget.pet._photo.height()}")
    else:
        print("WARNING: Pet photo asset not found, using fallback placeholder")

    # Check labels and grouping are correct in items_by_key
    assert "weekly" in snap.items_by_key, "items_by_key must have 'weekly'"
    assert "5hour" in snap.items_by_key, "items_by_key must have '5hour'"
    assert "claude_gpt" in snap.items_by_key, "items_by_key must have 'claude_gpt'"
    
    assert snap.items_by_key["weekly"].label == "Недельные лимиты", f"Expected 'Недельные лимиты', got {snap.items_by_key['weekly'].label}"
    assert snap.items_by_key["5hour"].label == "5-ти часовые", f"Expected '5-ти часовые', got {snap.items_by_key['5hour'].label}"
    assert snap.items_by_key["claude_gpt"].label == "Claude & GPT", f"Expected 'Claude & GPT', got {snap.items_by_key['claude_gpt'].label}"
    if snap.online:
        print(f"Live Weekly Limit: {snap.items_by_key['weekly'].percent}% | Reset: {snap.items_by_key['weekly'].reset_time_str}")
        assert 0 < snap.items_by_key["weekly"].percent < 100, f"Expected dynamic weekly limit (< 100%), got {snap.items_by_key['weekly'].percent}%"
        assert "claude_weekly" in snap.items_by_key, "items_by_key should have 'claude_weekly'"
    print("Labels & Keys OK: weekly ('Недельные лимиты'), 5hour ('5-ти часовые'), claude_gpt ('Claude & GPT')")

    # Test limit rows customization
    widget.set_limit_rows(["weekly", "5hour"])
    h_2rows = widget.height()
    widget.set_limit_rows(["weekly", "5hour", "claude_gpt"])
    assert len(widget.limit_rows) == 3
    assert widget.height() > h_2rows, f"3 rows should be taller than 2 rows ({widget.height()} > {h_2rows})"
    widget.set_limit_rows(["5hour", "claude_gpt"])
    assert len(widget.limit_rows) == 2
    assert widget.limit_rows[0] == "5hour" and widget.limit_rows[1] == "claude_gpt"
    # Reset back to default
    widget.set_limit_rows(["weekly", "5hour"])
    assert widget.limit_rows == ["weekly", "5hour"]
    print("Limit rows customization (2-3 rows and swapping) OK")

    # Test available pets
    available_pets = ElliotPet.get_available_pets("ru")
    assert len(available_pets) >= 2, "Should find at least 2 pets (live and photo)"
    print(f"Available pets found (ru): {[p[0] for p in available_pets]}")
    assert any(p[1] == "elliot_live" for p in available_pets), "elliot_live should be available"
    assert any(p[1] == "elliot.png" for p in available_pets), "elliot.png should be available"
    
    # Test localization of pet names
    pets_en = ElliotPet.get_available_pets("en")
    assert any("Live Video" in p[0] for p in pets_en), "English label should contain 'Live Video'"
    pets_zh = ElliotPet.get_available_pets("zh")
    assert any("动态视频" in p[0] for p in pets_zh), "Chinese label should contain '动态视频'"
    print("Pet localization (ru, en, zh) OK")

    # Test live animated sequence loading
    import time
    widget.set_pet_avatar("elliot_live")
    assert widget.pet.is_animated_sequence is True, "Pet should be recognized as animated sequence"
    assert len(widget.pet.frames) == 152, f"Expected 152 frames, got {len(widget.pet.frames)}"
    print(f"Live sequence loaded with {len(widget.pet.frames)} frames")

    # Test live animation stepping
    widget.pet.last_frame_time = time.time() - 0.1
    widget.pet.update_animation()
    assert widget.pet.current_frame_idx > 0, "Current frame index should advance"
    print(f"Live frame stepped to index: {widget.pet.current_frame_idx}")

    # Switch back to photo
    widget.set_pet_avatar("elliot.png")
    assert widget.pet.is_animated_sequence is False, "Pet should switch back to static photo"
    assert not widget.pet._photo.isNull(), "Static photo should be valid"
    print("Switching between live video and photo pet OK")

    # Test Codex 8x9 Sprite Atlas (Clippy & Tux)
    widget.set_pet_avatar("clippit")
    assert widget.pet.is_atlas is True, "Clippy should be recognized as Sprite Atlas"
    assert widget.pet.atlas_cols == 8 and widget.pet.atlas_rows == 9
    assert "waving" in widget.pet.atlas_rows_def
    assert "running" in widget.pet.atlas_rows_def
    print(f"Clippy Sprite Atlas loaded: cols={widget.pet.atlas_cols}, rows={widget.pet.atlas_rows}")

    # Test Atlas state reaction
    widget.pet.trigger_random_reaction()
    assert widget.pet.atlas_state in ("waving", "jumping"), f"State should be waving or jumping, got {widget.pet.atlas_state}"
    assert widget.pet.speech_text != "", "Speech text should be populated with quote"
    print(f"Clippy reaction OK: state={widget.pet.atlas_state}, speech='{widget.pet.speech_text}'")

    # Test Atlas typing reaction
    widget.pet.on_keyboard_activity()
    assert widget.pet.atlas_state in ("running", "waving", "jumping")
    print("Clippy typing reaction OK")

    # Test Tux
    widget.set_pet_avatar("tux")
    assert widget.pet.is_atlas is True, "Tux should be recognized as Sprite Atlas"
    assert not widget.pet._spritesheet.isNull()
    print("Tux Sprite Atlas loaded OK")

    # Test Catalog functions
    assert pet_catalog.is_pet_installed("clippit") is True
    assert pet_catalog.is_pet_installed("tux") is True
    installed_cat = pet_catalog.get_installed_catalog_pets()
    assert "clippit" in installed_cat and "tux" in installed_cat
    downloadable = pet_catalog.get_downloadable_catalog_pets()
    assert len(installed_cat) >= 2
    assert isinstance(downloadable, list)
    print(f"Pet catalog checks OK (installed: {installed_cat}, downloadable: {[p['id'] for p in downloadable]})")

    # Switch to elliot_live for remainder of tests
    widget.set_pet_avatar("elliot_live")

    # Test pet scaling
    orig_scale = cfg.get("pet_scale", 1.0)
    widget.set_pet_scale(1.0)
    assert widget.pet.width() == 76
    widget.set_pet_scale(1.25)
    assert widget.pet.width() == 95, f"Pet width should be 95 on 1.25x scale, got {widget.pet.width()}"
    
    # Test docked mode width change
    widget.pet_detached = False
    widget._recalculate_size()
    docked_w_scaled = widget.width()
    widget.set_pet_scale(1.0)
    assert widget.pet.width() == 76
    assert widget.width() < docked_w_scaled, "Docked widget width should decrease on smaller pet scale"
    # Restore original config scale and detached state
    widget.set_pet_scale(orig_scale)
    widget.pet_detached = cfg.get("pet_detached", False)
    widget._recalculate_size()
    print("Pet scaling OK")

    # Test pet reactions (organic cinematic animations)
    widget.pet.reaction_adjust_hood()
    assert widget.pet.hood_adjust_active is True, "Hood adjust should be active"
    widget.pet.reaction_head_sway()
    assert widget.pet.head_sway_active is True, "Head sway should be active"
    widget.pet.reaction_double_blink()
    assert widget.pet.is_blinking is True and widget.pet.double_blink is True, "Double blink should be active"
    widget.pet.reaction_blink_glitch()
    assert widget.pet.is_blinking is True
    widget.pet.reaction_wave()
    assert widget.pet.wave_active is True
    widget.pet.reaction_side_glance()
    assert abs(widget.pet.parallax_offset_x) > 0.1
    widget.pet.trigger_random_reaction()
    print("New & legacy pet click reactions OK")

    # Test pet animation enable/disable
    widget.pet.set_animations_enabled(False)
    assert widget.pet.animations_enabled is False
    assert widget.pet.head_sway_angle == 0.0
    widget.pet.set_animations_enabled(True)
    assert widget.pet.animations_enabled is True
    print("Pet animation enable/disable toggle OK")

    # Test keyboard typing activity
    widget.pet.on_keyboard_activity()
    assert widget.pet.typing_active is True
    print("Pet typing reaction OK")

    # Test i18n module
    from src.core.i18n import t
    assert t("weekly_limit", "ru") == "Недельные лимиты"
    assert t("weekly_limit", "en") == "Weekly limits"
    assert t("weekly_limit", "zh") == "周限额"
    assert t("five_hour_limit", "en") == "5-hour limit"
    assert t("five_hour_limit", "zh") == "5小时限额"
    print("i18n translation lookup (ru, en, zh) OK")

    # Test localized provider snapshots
    snap_en = provider.fetch_status(lang="en")
    assert snap_en.items_by_key["weekly"].label == "Weekly limits"
    assert snap_en.items_by_key["5hour"].label == "5-hour limit"
    snap_zh = provider.fetch_status(lang="zh")
    assert snap_zh.items_by_key["weekly"].label == "周限额"
    assert snap_zh.items_by_key["5hour"].label == "5小时限额"
    # Restore provider lang to ru
    provider.set_language("ru")
    print("Localized provider snapshots (ru, en, zh) OK")

    # Test SettingsDialog
    from src.ui.settings_dialog import SettingsDialog
    dlg = SettingsDialog(cfg)
    assert dlg.tab_widget.count() == 4
    settings_out = dlg.get_settings()
    assert "color_bg" in settings_out
    assert "color_bar_healthy" in settings_out
    assert "font_family" in settings_out
    assert "language" in settings_out
    assert "animations_enabled" in settings_out
    print("SettingsDialog initialization, tabs, and get_settings OK")

    # Test apply_settings on widget and tray
    test_cfg = dict(cfg)
    test_cfg["language"] = "en"
    test_cfg["font_family"] = "Consolas"
    test_cfg["font_size"] = 10
    test_cfg["color_bg"] = "#1e2430"
    test_cfg["color_bar_healthy"] = "#10b981"
    test_cfg["animations_enabled"] = False
    widget.apply_settings(test_cfg)
    assert widget.language == "en"
    assert widget.font_family == "Consolas"
    assert widget.font_size == 10
    assert widget.animations_enabled is False
    assert widget.pet.animations_enabled is False

    tray = DreamagyTray(language="ru")
    tray.apply_settings(test_cfg)
    assert tray.language == "en"
    print("Dynamic apply_settings on DreamagyWidget and DreamagyTray OK")

    # Re-render widget with new settings
    pix_en = QtGui.QPixmap(widget.size())
    pix_en.fill(QtCore.Qt.transparent)
    widget.render(pix_en)
    assert not pix_en.isNull()
    print("Rendered widget with dynamic settings successfully!")

    tray_icon = create_tray_icon(snap.items[0].percent if snap.items else 100, snap.online)
    print("Tray icon created successfully!")

    print("ALL TESTS PASSED WITH 0 ERRORS!")
except Exception as e:
    traceback.print_exc()
    sys.exit(1)
