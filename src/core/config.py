"""
Configuration manager for Dreamagy.
Handles saving and loading user preferences such as position, opacity, and pet visibility.
"""
import os
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")

DEFAULT_CONFIG = {
    "pos_x": 100,
    "pos_y": 100,
    "opacity": 0.95,
    "always_on_top": True,
    "show_pet": True,
    "pet_detached": False,
    "pet_pos_x": 50,
    "pet_pos_y": 50,
    "pet_scale": 1.0,
    "current_pet": "elliot_live",
    "limit_rows": ["weekly", "5hour"],
    "refresh_seconds": 15,
    "primary_group": "gemini",
    "theme": "dark_obsidian",
    "language": "ru",
    "font_family": "Segoe UI",
    "font_size": 9,
    "animations_enabled": True,
    "shimmer_enabled": True,
    "particles_enabled": True,
    "pet_animations_enabled": True,
    "color_bg": "#11151b",
    "color_bar_healthy": "#34d399",
    "color_bar_warning": "#f59e0b",
    "color_bar_critical": "#ef4444"
}

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                # merge with defaults
                merged = DEFAULT_CONFIG.copy()
                merged.update(cfg)
                return merged
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg: dict):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"[Config] Error saving config: {e}")
