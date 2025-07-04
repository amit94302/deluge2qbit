import os
from typing import List, Dict

def getenv_bool(name: str, default: str = "true") -> bool:
  """
  Gets a boolean value from an environment variable.
  """
  return os.getenv(name, default).strip().lower() in ["1", "true", "yes"]

def parse_label_map(var: str) -> Dict[str, str]:
  """
  Parses a comma or newline-separated string of key-value pairs from an environment variable.
  Example: "radarr-imported=Movies,sonarr-imported=TV Shows"
  """
  raw = os.getenv(var, "")
  lines = raw.splitlines() if "\n" in raw else raw.split(",")
  return {
    k.strip().lower(): v.strip()
    for line in lines if "=" in line
    for k, v in [line.strip().split("=", 1)]
  }

# --- Deluge Config ---
DELUGE_HOST: str = os.getenv("DELUGE_HOST", "deluge")
DELUGE_PORT: int = int(os.getenv("DELUGE_PORT", 58846))
DELUGE_USER: str = os.getenv("DELUGE_USER", "admin")
DELUGE_PASS: str = os.getenv("DELUGE_PASS", "delugepass")
DELUGE_MIGRATE_LABELS: List[str] = [
  label.strip().lower() for label in os.getenv("DELUGE_MIGRATE_LABELS", "").split(",") if label.strip()
]
DELUGE_STATE_PATH: str = os.getenv("DELUGE_STATE_PATH", "/deluge/state")
DELUGE_REMOVE: bool = getenv_bool("DELUGE_REMOVE", "true")

# --- qBittorrent Config ---
QBIT_HOST: str = os.getenv("QBIT_HOST", "qbittorrent")
QBIT_PORT: int = int(os.getenv("QBIT_PORT", 8080))
QBIT_USER: str = os.getenv("QBIT_USER", "admin")
QBIT_PASS: str = os.getenv("QBIT_PASS", "adminadmin")
QBIT_SKIP_EXTENSIONS: List[str] = [
  ext.strip().lower() for ext in os.getenv("QBIT_SKIP_EXTENSIONS", ".nfo,.info,.txt,.jpg,.png,.exe").split(",") if ext.strip()
]
QBIT_SET_CATEGORY: bool = getenv_bool("QBIT_SET_CATEGORY", "true")
QBIT_ADD_TAGS: bool = getenv_bool("QBIT_ADD_TAGS", "true")
QBIT_RESUME: bool = getenv_bool("QBIT_RESUME", "true")
QBIT_SAVE_PATH: str = os.getenv("QBIT_SAVE_PATH", "").strip()
QBIT_CATEGORY_MAP: Dict[str, str] = parse_label_map("QBIT_CATEGORY_MAP")
QBIT_CUSTOM_TAGS: str = os.getenv("QBIT_CUSTOM_TAGS", "").strip()

# --- App Config ---
TORRENT_FILE_DEST_PATH: str = os.getenv("TORRENT_FILE_DEST_PATH", "/torrents")
