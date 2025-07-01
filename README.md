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
  -v /path/to/deluge/config:/deluge \
  -v /downloads:/downloads \
  -e DELUGE_HOST=deluge \
  -e QBIT_HOST=qbittorrent \
  -e MIGRATE_LABELS=radarr,sonarr \
  -e SKIP_EXTENSIONS_RADARR=".nfo,.txt,.jpg" \
  -e SKIP_EXTENSIONS_SONARR=".nfo,.srt" \
  -e QBIT_SET_CATEGORY=true \
  -e QBIT_CATEGORY_MAP="radarr=movies,sonarr=tv" \
  amit94302/deluge2qbit
```

Or use with Docker Compose.

---

## ⚙️ Environment Variables

| Variable                | Description                                       | Example                    |
|-------------------------|---------------------------------------------------|----------------------------|
| `MIGRATE_LABELS`        | Comma-separated labels to migrate                 | `radarr,sonarr`           |
| `QBIT_SKIP_EXTENSIONS`  | Extensions to delete + skip (by label)            | `.nfo,.srt`                |
| `QBIT_SAVE_PATH`        | Override default save path                        | `/downloads/qbit`         |
| `QBIT_SET_CATEGORY`     | Enable setting qBittorrent category               | `true`                     |
| `QBIT_CATEGORY_MAP`     | Map labels to qBittorrent categories              | `radarr=movies,...`       |
| `QBIT_ADD_TAGS`         | Enable tagging in qBittorrent                     | `true`                     |
| `QBIT_RESUME`           | Whether to resume torrents after adding           | `true`                     |
| `DELUGE_REMOVE`         | Whether to remove torrent from Deluge             | `true`                     |

---

## 🏗 CI/CD Setup

Image is built and pushed to:
- Docker Hub: [`amit94302/deluge2qbit`](https://hub.docker.com/r/amit94302/deluge2qbit)
- GitHub Container Registry: `ghcr.io/amit94302/deluge2qbit`

Trigger: On push to `main`

---

## 📄 License
[MIT](LICENSE)