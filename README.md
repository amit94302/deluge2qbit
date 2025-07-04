# deluge2qbit 🧲➡️🎯

Migrate torrents from **Deluge** (with labels) to **qBittorrent**, using Dockerized automation.

## 🚀 Features
- Auto-migrate torrents by label (e.g., `radarr-imported`, `sonarr-imported`)
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
  -e DELUGE_MIGRATE_LABELS=radarr-imported,sonarr-imported \
  -e QBIT_HOST=qbittorrent \
  -e QBIT_PORT=8080 \
  -e QBIT_USER=admin \
  -e QBIT_PASS=QbittorrentPass \
  -e QBIT_SET_CATEGORY=true \
  -e QBIT_CATEGORY_MAP="radarr-imported=Movies,sonarr-imported=TV Shows" \
  -e QBIT_ADD_TAGS=true \
  -e QBIT_CUSTOM_TAGS=deluge2qbit,torrent-migrator \
  -e QBIT_SAVE_PATH=/downloads/qbit \
  -e QBIT_SKIP_EXTENSIONS=.nfo,.info,.txt,.jpg,.png,.exe,.sfv \
  -e QBIT_RESUME=true \
  -e DELUGE_REMOVE=true \
  -e DELUGE_STATE_PATH=/deluge/state \
  -e TORRENT_FILE_DEST_PATH=/torrents \
  -v <torrent-download-path>:/media/downloads/torrents \
  -v <deluge-config-path>:/deluge \
  -v <torrent-file-save-path>:/torrents \
  amit94302/deluge2qbit
```

Or use with Docker Compose.

---

## ⚙️ Environment Variables

| Variable                 | Description                                                        | Example (defaults, if applicable)     |
|--------------------------|--------------------------------------------------------------------|---------------------------------------|
| `DELUGE_HOST`            | Deluge hostname                                                    | `deluge`                              |
| `DELUGE_PORT`            | Deluge port                                                        | `58846`                               |
| `DELUGE_USER`            | Deluge username                                                    | `admin`                               |
| `DELUGE_PASS`            | Deluge password                                                    | `DelugePass`                          |
| `DELUGE_MIGRATE_LABELS`  | Comma-separated Deluge labels to migrate                           | `radarr-imported,sonarr-imported`     |
| `QBIT_HOST`              | qBittorrent hostname                                               | `qbittorrent`                         |
| `QBIT_PORT`              | qBittorrent port                                                   | `8080`                                |
| `QBIT_USER`              | qBittorrent username                                               | `admin`                               |
| `QBIT_PASS`              | qBittorrent password                                               | `QbittorrentPass`                     |
| `QBIT_SET_CATEGORY`      | Enable setting qBittorrent category                                | `true`                                |
| `QBIT_CATEGORY_MAP`      | Map Deluge migrate labels to qBittorrent categories                | `radarr-imported=movies,...`          |
| `QBIT_ADD_TAGS`          | Enable tagging in qBittorrent                                      | `true`                                |
| `QBIT_CUSTOM_TAGS`       | Comma-separated custom tags (deluge label will be used if not set) | `true`                                |
| `QBIT_SAVE_PATH`         | Override default save path                                         | `/downloads/qbit`                     |
| `QBIT_SKIP_EXTENSIONS`   | Extensions to delete + skip (by label)                             | `.nfo,.info,.txt,.jpg,.png,.exe,.sfv` |
| `QBIT_RESUME`            | Whether to resume torrents after adding                            | `true`                                |
| `DELUGE_REMOVE`          | Whether to remove torrent from Deluge                              | `true`                                |
| `DELUGE_STATE_PATH`      | Deluge state path                                                  | `/deluge/state`                       |
| `TORRENT_FILE_DEST_PATH` | Torrent file copy path from `DELUGE_STATE_PATH`                    | `/torrents`                           |

---

## 🏗 CI/CD Setup

Image is built and pushed to:
- Docker Hub: [`amit94302/deluge2qbit`](https://hub.docker.com/r/amit94302/deluge2qbit)
- GitHub Container Registry: `ghcr.io/amit94302/deluge2qbit`

Trigger: On push to `main`

---

## 📄 License
[MIT](LICENSE)