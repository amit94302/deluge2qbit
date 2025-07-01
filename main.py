import os
import shutil
from pathlib import Path
import time
from deluge_client import DelugeRPCClient
import qbittorrentapi

def decode_bytes(d):
  if isinstance(d, dict):
    return {k.decode() if isinstance(k, bytes) else k: decode_bytes(v) for k, v in d.items()}
  elif isinstance(d, list):
    return [decode_bytes(i) for i in d]
  elif isinstance(d, bytes):
    return d.decode()
  else:
    return d

def getenv_bool(name: str, default: str = "true") -> bool:
  return os.getenv(name, default).strip().lower() in ["1", "true", "yes"]

def parse_label_map(var: str) -> dict:
  raw = os.getenv(var, "")
  lines = raw.splitlines() if "\n" in raw else raw.split(",")
  return {
    k.strip().lower(): v.strip()
    for line in lines if "=" in line
    for k, v in [line.strip().split("=", 1)]
  }

# === Config from environment ===
DELUGE_HOST = os.getenv("DELUGE_HOST", "deluge")
DELUGE_PORT = int(os.getenv("DELUGE_PORT", 58846))
DELUGE_USER = os.getenv("DELUGE_USER", "admin")
DELUGE_PASS = os.getenv("DELUGE_PASS", "delugepass")
MIGRATE_LABELS = [label.strip().lower() for label in os.getenv("MIGRATE_LABELS", "").split(",") if label.strip()]

QBIT_HOST = os.getenv("QBIT_HOST", "qbittorrent")
QBIT_PORT = int(os.getenv("QBIT_PORT", 8080))
QBIT_USER = os.getenv("QBIT_USER", "admin")
QBIT_PASS = os.getenv("QBIT_PASS", "adminadmin")
QBIT_SKIP_EXTENSIONS = os.getenv("QBIT_SKIP_EXTENSIONS", ".nfo,.info,.txt,.jpg,.png,.exe").split(",")

QBIT_SKIP_EXTENSIONS = [ext.strip().lower() for ext in QBIT_SKIP_EXTENSIONS if ext.strip()]

QBIT_SET_CATEGORY = getenv_bool("QBIT_SET_CATEGORY", "true")
QBIT_ADD_TAGS = getenv_bool("QBIT_ADD_TAGS", "true")
QBIT_RESUME = getenv_bool("QBIT_RESUME", "true")
DELUGE_REMOVE = getenv_bool("DELUGE_REMOVE", "true")

TORRENT_FILE_DEST_PATH = os.getenv("TORRENT_FILE_DEST_PATH", "/torrents")
DELUGE_STATE_PATH = os.getenv("DELUGE_STATE_PATH", "/deluge/state")
os.makedirs(TORRENT_FILE_DEST_PATH, exist_ok=True)

CATEGORY_MAP = parse_label_map("QBIT_CATEGORY_MAP")

print("🔌 Connecting to Deluge...")
deluge = DelugeRPCClient(DELUGE_HOST, DELUGE_PORT, DELUGE_USER, DELUGE_PASS)
deluge.connect()

fields = ['name', 'label', 'save_path']
raw_torrents = deluge.call('core.get_torrents_status', {}, fields)
torrents = {k.decode(): decode_bytes(v) for k, v in raw_torrents.items()}

print("🔐 Connecting to qBittorrent...")
qbt = qbittorrentapi.Client(host=f"http://{QBIT_HOST}:{QBIT_PORT}", username=QBIT_USER, password=QBIT_PASS)
qbt.auth_log_in()

print(f"🔍 Filtering torrents in Deluge with label(s): {MIGRATE_LABELS}")
for torrent_id, data in torrents.items():
  name = data.get("name", "unknown")
  deluge_label = data.get("label", "").strip().lower()
  deluge_save_path = data.get("save_path", "/downloads").strip()

  # print(f"🧾 Checking: {name} (deluge_label={deluge_label})")

  if deluge_label not in MIGRATE_LABELS:
    continue

  # === Step 1: Copy .torrent file from Deluge config ===
  deluge_torrent_file_path = os.path.join(DELUGE_STATE_PATH, f"{torrent_id}.torrent")
  if not os.path.isfile(deluge_torrent_file_path):
    print(f"⚠️  Torrent file missing: {deluge_torrent_file_path}")
    continue

  qbit_torrent_file_path = os.path.join(TORRENT_FILE_DEST_PATH, f"{name}.torrent")
  shutil.copyfile(deluge_torrent_file_path, qbit_torrent_file_path)

  qbit_save_path = os.getenv("QBIT_SAVE_PATH", deluge_save_path).strip()
  actual_path = Path(qbit_save_path) / name

  # === Make sure actual_path exists ===
  if not actual_path.exists():
    print(f"⚠️ Path does not exist: {actual_path}")
    continue

  # === Step 2: Delete unwanted files from Deluge download folder ===
  for item in Path(actual_path).glob("*"):
    if item.suffix.lower() in QBIT_SKIP_EXTENSIONS:
      try:
        print(f"🗑️ Deleting skipped file from disk: {item}")
        item.unlink()
      except Exception as e:
        print(f"⚠️ Failed to delete {item}: {e}")
  
  # === Step 3: Add to qBittorrent (paused) ===
  print(f"➡️  Adding {name} to qBittorrent...")
  add_args = {
    "torrent_files": str(qbit_torrent_file_path),
    "save_path": str(actual_path),
    "is_paused": True,
    "autoTMM": False,
  }

  if QBIT_ADD_TAGS:
    add_args["tags"] = os.getenv("QBIT_CUSTOM_TAG", deluge_label).strip()
    # add_args["tags"] = deluge_label
  
  if QBIT_SET_CATEGORY:
    qbit_category = CATEGORY_MAP.get(deluge_label, deluge_label)  # fallback to label if not mapped
    add_args["category"] = qbit_category
    print(f"🏷️ Setting category '{qbit_category}' for label '{deluge_label}'")

  qbt.torrents_add(**add_args)

  # === Wait for qBittorrent to register the torrent ===
  time.sleep(2)  # Important: Wait for metadata to load

  # === Find the added torrent by hash or name ===
  torrent = next(
    (t for t in qbt.torrents_info() if name in t.name),
    None
  )

  if not torrent:
    print(f"⚠️ Torrent {name} not found in qBittorrent!")
    sys.exit(1)

  # === Get file list ===
  files = qbt.torrents_files(torrent.hash)

  # === Unselect files with unwanted extensions ===
  for f in files:
    file_name = f.name.lower()
    if any(file_name.endswith(ext) for ext in QBIT_SKIP_EXTENSIONS):
      print(f"❌ Skipping: {f.name}")
      qbt.torrents_file_priority(torrent.hash, file_ids=[f.index], priority=0)
    else:
      print(f"✅ Keeping: {f.name}")

  # === Resume torrent ===
  if QBIT_RESUME:
    qbt.torrents_resume(torrent.hash)
    print(f"🚀 Resumed in qBittorrent: {name}")
  else:
    print(f"⏸️  Skipped resume (QBIT_RESUME=false): {name}")

  print(f"✅ Added: {name}")

  # === Remove from Deluge ===
  if DELUGE_REMOVE:
    deluge.call("core.remove_torrent", torrent_id, True)
    print(f"🗑️ Removed from Deluge: {name}")
  else:
    print(f"🔁 Kept in Deluge (DELUGE_REMOVE=false): {name}")
