"""
Pet Catalog and Asynchronous Asset Downloader for Dreamagy.
Provides metadata for classic animated pets from Tomatio13/pet-companion and codex-pet-share,
and a non-blocking QThread worker to download them into assets/pets/<pet_id>/.
"""

import os
import json
import urllib.request
from typing import Dict, List, Optional
from PyQt5 import QtCore

BASE_REMOTE_URL = "https://raw.githubusercontent.com/Tomatio13/pet-companion/master/petcompanion/pet_static/assets"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PETS_DIR = os.path.join(ROOT_DIR, "assets", "pets")

CATALOG_PETS: Dict[str, dict] = {
    "clippit": {
        "id": "clippit",
        "name": "Clippy",
        "display_name_ru": "📎 Clippy (Скрепыш)",
        "display_name_en": "📎 Clippy (Paperclip)",
        "display_name_zh": "📎 Clippy (回形针)",
        "description": "Классический анимированный помощник Microsoft Office.",
        "icon": "📎",
        "pixel_art": True,
        "quotes": [
            "It looks like you're writing code!",
            "Need assistance with that prompt?",
            "Checking Antigravity quotas...",
            "Quota looks healthy! Keep hacking.",
            "Don't forget to commit your changes!"
        ]
    },
    "tux": {
        "id": "tux",
        "name": "Tux",
        "display_name_ru": "🐧 Tux (Пингвин Linux)",
        "display_name_en": "🐧 Tux (Linux Penguin)",
        "display_name_zh": "🐧 Tux (Linux 企鹅)",
        "description": "Легендарный пиксельный маскот Linux для спокойных сессий кодинга.",
        "icon": "🐧",
        "pixel_art": True,
        "quotes": [
            "Kernel compiled successfully.",
            "Keep calm and compile.",
            "sudo make install",
            "GNU/Linux rules the servers.",
            "Everything is a file."
        ]
    },
    "yorha-sit-2b": {
        "id": "yorha-sit-2b",
        "name": "YoRHa 2B",
        "display_name_ru": "⚔️ 2B (NieR:Automata)",
        "display_name_en": "⚔️ 2B (NieR:Automata)",
        "display_name_zh": "⚔️ 2B (尼尔:机械纪元)",
        "description": "Боевой андроид 2B из NieR:Automata.",
        "icon": "⚔️",
        "pixel_art": True,
        "quotes": [
            "Glory to Mankind.",
            "All things are designed to end.",
            "Pod 042: Status normal.",
            "Commencing mission."
        ]
    },
    "nyako-shigure": {
        "id": "nyako-shigure",
        "name": "Shigure Ui",
        "display_name_ru": "🐱 Shigure Ui (Nyako)",
        "display_name_en": "🐱 Shigure Ui (Nyako)",
        "display_name_zh": "🐱 时雨羽衣 (Nyako)",
        "description": "Популярный аниме-маскот Shigure Ui.",
        "icon": "🐱",
        "pixel_art": True,
        "quotes": [
            "Ui-beam! (´｡• ᵕ •｡`)",
            "Ganbare!",
            "Nyahaha~ Keep coding!"
        ]
    },
    "dario": {
        "id": "dario",
        "name": "Dario",
        "display_name_ru": "👔 Dario Amodei (Anthropic)",
        "display_name_en": "👔 Dario Amodei (Anthropic)",
        "display_name_zh": "👔 Dario Amodei (Anthropic)",
        "description": "Дарио Амодеи (CEO Anthropic / Claude).",
        "icon": "👔",
        "pixel_art": True,
        "quotes": [
            "Claude 3.7 Sonnet is ready.",
            "Constitutional AI is running.",
            "Scaling is all you need."
        ]
    },
    "slavik": {
        "id": "slavik",
        "name": "Slavik",
        "display_name_ru": "🧢 Славик (Slavik)",
        "display_name_en": "🧢 Slavik",
        "display_name_zh": "🧢 Slavik",
        "description": "Колоритный пиксельный персонаж Славик.",
        "icon": "🧢",
        "pixel_art": True,
        "quotes": [
            "Чё по квотам?",
            "Код сам себя не напишет!",
            "Всё под контролем, шеф!"
        ]
    },
    "trump": {
        "id": "trump",
        "name": "Donald Trump",
        "display_name_ru": "👱 Дональд (Trump)",
        "display_name_en": "👱 Donald Trump",
        "display_name_zh": "👱 特朗普 (Trump)",
        "description": "Анимированный пиксельный Дональд.",
        "icon": "👱",
        "pixel_art": True,
        "quotes": [
            "We have the best models, folks!",
            "Tremendous quotas. Huge!",
            "Make Code Great Again!"
        ]
    },
    "yelling-dario": {
        "id": "yelling-dario",
        "name": "Yelling Dario",
        "display_name_ru": "📢 Dario (Кричащий)",
        "display_name_en": "📢 Yelling Dario",
        "display_name_zh": "📢 呐喊的 Dario",
        "description": "Экспрессивный Дарио Амодеи.",
        "icon": "📢",
        "pixel_art": True,
        "quotes": [
            "AGI IS COMING!",
            "MORE COMPUTE!",
            "WE NEED MORE GPU CLUSTERS!",
            "SCALE IT UP!"
        ]
    }
}


def get_pet_info(pet_id: str) -> Optional[dict]:
    """Get metadata for a catalog pet."""
    return CATALOG_PETS.get(pet_id)


def is_pet_installed(pet_id: str) -> bool:
    """Checks whether a pet directory exists in assets/pets/ with pet.json and spritesheet."""
    pdir = os.path.join(PETS_DIR, pet_id)
    if not os.path.isdir(pdir):
        return False
    has_manifest = os.path.exists(os.path.join(pdir, "pet.json"))
    has_sprite = any(
        os.path.exists(os.path.join(pdir, f"spritesheet.{ext}"))
        for ext in ("webp", "png", "gif")
    )
    return has_manifest and has_sprite


def get_installed_catalog_pets() -> List[str]:
    """Returns list of catalog pet IDs that are already downloaded locally."""
    return [pid for pid in CATALOG_PETS if is_pet_installed(pid)]


def get_downloadable_catalog_pets() -> List[dict]:
    """Returns list of catalog pet info dicts that are not yet downloaded."""
    return [info for pid, info in CATALOG_PETS.items() if not is_pet_installed(pid)]


def download_pet_sync(pet_id: str) -> bool:
    """Synchronously downloads a pet from the remote repository into assets/pets/<pet_id>/."""
    if pet_id not in CATALOG_PETS:
        return False
    target_dir = os.path.join(PETS_DIR, pet_id)
    os.makedirs(target_dir, exist_ok=True)
    
    files_to_download = ["pet.json", "spritesheet.webp"]
    try:
        for fname in files_to_download:
            url = f"{BASE_REMOTE_URL}/{pet_id}/{fname}"
            dst = os.path.join(target_dir, fname)
            req = urllib.request.Request(url, headers={"User-Agent": "Dreamagy-PetDownloader/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(dst, "wb") as f:
                f.write(data)
        return True
    except Exception as e:
        print(f"[PetCatalog] Failed to download pet '{pet_id}': {e}")
        return False


class PetDownloadWorker(QtCore.QThread):
    """Asynchronous background worker to download a pet without freezing the GUI."""
    progress = QtCore.pyqtSignal(str, int)  # pet_id, percent
    finished = QtCore.pyqtSignal(str, bool, str)  # pet_id, success, error_message

    def __init__(self, pet_id: str, parent=None):
        super().__init__(parent)
        self.pet_id = pet_id

    def run(self):
        if self.pet_id not in CATALOG_PETS:
            self.finished.emit(self.pet_id, False, "Unknown pet ID")
            return

        target_dir = os.path.join(PETS_DIR, self.pet_id)
        os.makedirs(target_dir, exist_ok=True)
        files_to_download = ["pet.json", "spritesheet.webp"]

        try:
            total = len(files_to_download)
            for idx, fname in enumerate(files_to_download):
                url = f"{BASE_REMOTE_URL}/{self.pet_id}/{fname}"
                dst = os.path.join(target_dir, fname)
                req = urllib.request.Request(url, headers={"User-Agent": "Dreamagy-PetDownloader/1.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
                with open(dst, "wb") as f:
                    f.write(data)
                pct = int(((idx + 1) / total) * 100)
                self.progress.emit(self.pet_id, pct)

            self.finished.emit(self.pet_id, True, "")
        except Exception as e:
            self.finished.emit(self.pet_id, False, str(e))
