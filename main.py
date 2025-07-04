import os
import sys
import shutil
import time
import logging
from pathlib import Path
from deluge_client import DelugeRPCClient
import qbittorrentapi
from qbittorrentapi.exceptions import APIConnectionError, NotFound404Error
import config

# --- Setup Logging ---
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(levelname)s - %(message)s",
  stream=sys.stdout,
)

def decode_bytes(d):
  """
  Recursively decodes bytes to strings in a dictionary or list.
  """
  if isinstance(d, dict):
    return {k.decode() if isinstance(k, bytes) else k: decode_bytes(v) for k, v in d.items()}
  elif isinstance(d, list):
    return [decode_bytes(i) for i in d]
  elif isinstance(d, bytes):
    return d.decode()
  else:
    return d

def connect_deluge():
  """
  Connects to the Deluge RPC server.
  """
  logging.info("🔌 Connecting to Deluge...")
  try:
    client = DelugeRPCClient(config.DELUGE_HOST, config.DELUGE_PORT, config.DELUGE_USER, config.DELUGE_PASS)
    client.connect()
    logging.info("✅ Connected to Deluge.")
    return client
  except Exception as e:
    logging.error(f"🔥 Failed to connect to Deluge: {e}")
    sys.exit(1)

def connect_qbittorrent():
  """
  Connects to the qBittorrent Web API.
  """
  logging.info("🔐 Connecting to qBittorrent...")
  try:
    client = qbittorrentapi.Client(
      host=f"http://{config.QBIT_HOST}:{config.QBIT_PORT}",
      username=config.QBIT_USER,
      password=config.QBIT_PASS,
      REQUESTS_ARGS={"timeout": 30}
    )
    client.auth_log_in()
    logging.info("✅ Connected to qBittorrent.")
    return client
  except APIConnectionError as e:
    logging.error(f"🔥 Failed to connect to qBittorrent: {e}")
    sys.exit(1)

def add_torrent_to_qbit(qbt, torrent_file, save_path, deluge_label, name):
  """
  Adds a torrent to qBittorrent with the specified settings.
  """
  logging.info(f"➡️ Adding {name} to qBittorrent...")
  add_args = {
    "torrent_files": str(torrent_file),
    "save_path": str(save_path),
    "is_paused": True,
    "autoTMM": False,
  }

  if config.QBIT_ADD_TAGS:
    tags = config.QBIT_CUSTOM_TAGS or deluge_label
    add_args["tags"] = [tag.strip() for tag in tags.split(",")]

  if config.QBIT_SET_CATEGORY:
    qbit_category = config.QBIT_CATEGORY_MAP.get(deluge_label, deluge_label)
    add_args["category"] = qbit_category
    logging.info(f"🏷️ Setting category '{qbit_category}' for label '{deluge_label}'")

  qbt.torrents_add(**add_args)

  # --- Wait for torrent to appear in qBittorrent ---
  torrent = wait_for_torrent(qbt, name)
  if not torrent:
    logging.error(f"⚠️ Torrent {name} not found in qBittorrent after adding!")
    return

  # --- Unselect unwanted files ---
  files = qbt.torrents_files(torrent.hash)
  file_ids_to_skip = [f.index for f in files if any(f.name.lower().endswith(ext) for ext in config.QBIT_SKIP_EXTENSIONS)]
  if file_ids_to_skip:
    logging.info(f"❌ Skipping {len(file_ids_to_skip)} files with unwanted extensions.")
    qbt.torrents_file_priority(torrent.hash, file_ids=file_ids_to_skip, priority=0)

  # --- Resume torrent ---
  if config.QBIT_RESUME:
    qbt.torrents_resume(torrent.hash)
    logging.info(f"🚀 Resumed in qBittorrent: {name}")
  else:
    logging.info(f"⏸️ Skipped resume (QBIT_RESUME=false): {name}")

  logging.info(f"✅ Added: {name}")

def wait_for_torrent(qbt, name, timeout=30):
  """
  Waits for a torrent to appear in qBittorrent by name.
  """
  start_time = time.time()
  while time.time() - start_time < timeout:
    try:
      torrent = next((t for t in qbt.torrents_info() if name in t.name), None)
      if torrent:
        return torrent
    except NotFound404Error:
      # Torrent might not be registered yet
      pass
    time.sleep(1)
  return None

def process_torrents(deluge, qbt):
  """
  Fetches torrents from Deluge and migrates them to qBittorrent based on labels.
  """
  fields = ['name', 'label', 'save_path']
  try:
    raw_torrents = deluge.call('core.get_torrents_status', {}, fields)
    torrents = {k.decode(): decode_bytes(v) for k, v in raw_torrents.items()}
  except Exception as e:
    logging.error(f"🔥 Failed to get torrents from Deluge: {e}")
    return

  logging.info(f"🔍 Filtering torrents in Deluge with label(s): {config.DELUGE_MIGRATE_LABELS}")

  for torrent_id, data in torrents.items():
    name = data.get("name", "unknown")
    deluge_label = data.get("label", "").strip().lower()
    deluge_save_path = data.get("save_path", "/downloads").strip()

    if deluge_label not in config.DELUGE_MIGRATE_LABELS:
      continue

    logging.info(f"Processing torrent: {name}")

    # --- Step 1: Copy .torrent file ---
    deluge_torrent_file_path = os.path.join(config.DELUGE_STATE_PATH, f"{torrent_id}.torrent")
    if not os.path.isfile(deluge_torrent_file_path):
      logging.warning(f"⚠️ Torrent file missing, skipping: {deluge_torrent_file_path}")
      continue

    qbit_torrent_file_path = os.path.join(config.TORRENT_FILE_DEST_PATH, f"{name}.torrent")
    shutil.copyfile(deluge_torrent_file_path, qbit_torrent_file_path)

    # --- Step 2: Determine save path and delete unwanted files ---
    qbit_save_path = config.QBIT_SAVE_PATH or deluge_save_path
    actual_path = Path(qbit_save_path) / name
    if not actual_path.is_dir():
      actual_path = Path(qbit_save_path)

    # if not actual_path.exists():
    #   logging.warning(f"⚠️ Path does not exist, skipping: {actual_path}")
    #   continue

    for item in Path(actual_path).glob("*"):
      if item.suffix.lower() in config.QBIT_SKIP_EXTENSIONS:
        try:
          logging.info(f"🗑️ Deleting skipped file from disk: {item}")
          item.unlink()
        except Exception as e:
          logging.warning(f"⚠️ Failed to delete {item}: {e}")

    # --- Step 3: Add to qBittorrent ---
    try:
      add_torrent_to_qbit(qbt, qbit_torrent_file_path, actual_path, deluge_label, name)
    except Exception as e:
      logging.error(f"🔥 Failed to add torrent {name} to qBittorrent: {e}")
      continue

    # --- Step 4: Remove from Deluge ---
    if config.DELUGE_REMOVE:
      try:
        deluge.call("core.remove_torrent", torrent_id, False)
        logging.info(f"🗑️ Removed from Deluge: {name}")
      except Exception as e:
        logging.error(f"🔥 Failed to remove torrent {name} from Deluge: {e}")
    else:
      logging.info(f"🔁 Kept in Deluge (DELUGE_REMOVE=false): {name}")


def main():
  """
  Main function to run the torrent migration script.
  """
  os.makedirs(config.TORRENT_FILE_DEST_PATH, exist_ok=True)
  deluge_client = connect_deluge()
  qbt_client = connect_qbittorrent()
  process_torrents(deluge_client, qbt_client)
  logging.info("🎉 Migration complete.")

if __name__ == "__main__":
  main()
