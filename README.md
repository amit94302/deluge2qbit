# deluge2qbit 🧲➡️🎯

Migrate torrents from **Deluge** (with labels) to **qBittorrent**, using Dockerized automation.

## 🚀 Features
- Auto-migrate torrents by label (e.g., `radarr`, `sonarr`)
- Remove already-downloaded junk files (.nfo, .txt, .jpg, etc.)
- Set qBittorrent save path, category, tags — per-label configurable
- Environment-driven configuration (CI-friendly)

---

## 🐳 Docker Usage

```bash
docker run --rm \
  -e DELUGE_HOST=deluge \
  -e DELUGE_PORT=58846 \
  -e DELUGE_USER=admin \
  -e DELUGE_PASS=DelugePass \
  -e MIGRATE_LABELS=radarr-imported,sonarr-imported \
  -e QBIT_HOST=qbittorrent \
  -e QBIT_PORT=8090 \
  -e QBIT_USER=admin \
  -e QBIT_PASS=QbittorrentPass \
  -e QBIT_SET_CATEGORY=true \
  -e QBIT_CATEGORY_MAP="radarr-imported=Movies,sonarr-imported=TV Shows" \
  -e QBIT_ADD_TAGS=true \
  -e QBIT_CUSTOM_TAG=deluge2qbit \
  -e QBIT_SAVE_PATH=/wd/extras/Downloads/Torrent_Downloads \
  -e QBIT_SKIP_EXTENSIONS=.nfo,.info,.txt,.jpg,.png,.exe,.sfv \
  -e QBIT_RESUME=true \
  -e DELUGE_REMOVE=true \
  -e TORRENT_FILE_DEST_PATH=/torrents \
  -e DELUGE_STATE_PATH=/deluge/state \
  -v <torrent-download-path>:/wd/extras/Downloads/Torrent_Downloads \
  -v <deluge-config-path>:/deluge \
  -v <torrent-file-save-path>:/torrents \
  amit94302/deluge2qbit
```

Or use with Docker Compose.

---

## ⚙️ Environment Variables

| Variable                | Description                                       | Example                            |
|-------------------------|---------------------------------------------------|------------------------------------|
| `MIGRATE_LABELS`        | Comma-separated labels to migrate                 | `radarr-imported,sonarr-imported`  |
| `QBIT_SKIP_EXTENSIONS`  | Extensions to delete + skip (by label)            | `.nfo,.srt`                        |
| `QBIT_SAVE_PATH`        | Override default save path                        | `/downloads/qbit`                  |
| `QBIT_SET_CATEGORY`     | Enable setting qBittorrent category               | `true`                             |
| `QBIT_CATEGORY_MAP`     | Map labels to qBittorrent categories              | `radarr-imported=movies,...`       |
| `QBIT_ADD_TAGS`         | Enable tagging in qBittorrent                     | `true`                             |
| `QBIT_RESUME`           | Whether to resume torrents after adding           | `true`                             |
| `DELUGE_REMOVE`         | Whether to remove torrent from Deluge             | `true`                             |

---

## 🏗 CI/CD Setup

Image is built and pushed to:
- Docker Hub: [`amit94302/deluge2qbit`](https://hub.docker.com/r/amit94302/deluge2qbit)
- GitHub Container Registry: `ghcr.io/amit94302/deluge2qbit`

Trigger: On push to `main`

---

## 📄 License
[MIT](LICENSE)