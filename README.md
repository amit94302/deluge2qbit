---
gitea: none
include_toc: true
---

# deluge2qbit 🧲➡️🎯

A Dockerized script to automatically migrate torrents from **Deluge** to **qBittorrent**, applying new categories, tags, and save paths based on Deluge labels.

## 🚀 Features

- **Label-based Migration:** Automatically migrates torrents that have specific Deluge labels (e.g., `radarr-imported`, `sonarr-imported`).
- **Path & Category Mapping:** Sets qBittorrent save path, category, and tags, all configurable per-label.
- **Junk File Cleanup:** Option to remove unnecessary files (.nfo, .txt, .jpg) from the torrent content before adding to qBittorrent.
- **Flexible Configuration:** Fully configurable through environment variables, making it CI/CD friendly.
- **Stateful Migration:** Copies `.torrent` files from the Deluge state directory for a seamless import.

---

## ✅ Prerequisites

- **Docker** and **Docker Compose** installed.
- Running instances of **Deluge** and **qBittorrent**.
- The Deluge Label plugin must be enabled and used to categorize torrents.

---

## ⚙️ Usage

### Docker Compose (Recommended)

Using Docker Compose is the easiest way to run the migration script. You can use the example below as a starting point. For the complete, up-to-date configuration, please refer to the [docker-compose.yml](docker-compose.yml) file.

Create a `docker-compose.yml` file, fill in your details (especially passwords and paths), and then run `docker-compose up -d deluge2qbit`.

**Example `docker-compose.yml`:**

```yaml
---

services:
  deluge2qbit:
    image: amit94302/deluge2qbit:latest
    container_name: deluge2qbit
    environment:
      # --- Deluge Settings ---
      - DELUGE_HOST=deluge
      - DELUGE_PORT=58846
      - DELUGE_USER=admin
      - DELUGE_PASS=your_deluge_password # ⚠️ CHANGE THIS
      - DELUGE_MIGRATE_LABELS=radarr-imported,sonarr-imported
      - DELUGE_REMOVE=true
      # --- qBittorrent Settings ---
      - QBIT_HOST=qbittorrent
      - QBIT_PORT=8080
      - QBIT_USER=admin
      - QBIT_PASS=your_qbit_password # ⚠️ CHANGE THIS
      - QBIT_SET_CATEGORY=true
      - 'QBIT_CATEGORY_MAP=radarr-imported=Movies,sonarr-imported=TV Shows'
      - QBIT_ADD_TAGS=true
      - QBIT_CUSTOM_TAGS=deluge2qbit,migrated
      - QBIT_SAVE_PATH=/downloads/completed
      - QBIT_SKIP_EXTENSIONS=.nfo,.txt,.jpg
      - QBIT_RESUME=true
    volumes:
      # ⚠️ CHANGE THESE HOST PATHS
      # Path where Deluge stores its state files (e.g., torrents, logs)
      - /path/to/your/deluge/config:/deluge
      # Path where your torrent data is stored. This MUST be the same path qBittorrent uses.
      - /path/to/your/downloads:/downloads/completed
      # A temporary path to store .torrent files during migration
      - ./torrents:/torrents
    restart: unless-stopped
```

### Docker Run

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
  -v /path/to/your/deluge/config:/deluge \
  -v /path/to/your/downloads:/downloads/qbit \
  -v ./torrents:/torrents \
  amit94302/deluge2qbit
```

---

## 🤔 How It Works

The script performs the following steps:

1. **Connects** to both the Deluge and qBittorrent clients.
2. **Scans Deluge** for torrents matching the labels defined in `DELUGE_MIGRATE_LABELS`.
3. For each matching torrent, it **copies the `.torrent` file** from the Deluge state directory (`DELUGE_STATE_PATH`) to a temporary location (`TORRENT_FILE_DEST_PATH`).
4. It **adds the torrent to qBittorrent** using the copied `.torrent` file, applying the specified save path, category, and tags.
5. If `QBIT_SKIP_EXTENSIONS` is set, it identifies and **removes junk files** from the torrent content.
6. If `DELUGE_REMOVE` is `true`, it **removes the original torrent** from Deluge.

---

## 🔧 Configuration

### Environment Variables

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
| `QBIT_SKIP_EXTENSIONS`   | Extensions to delete from disk + skip downloading in qBittorrent   | `.nfo,.info,.txt,.jpg,.png,.exe,.sfv` |
| `QBIT_RESUME`            | Whether to resume torrents after adding                            | `true`                                |
| `DELUGE_REMOVE`          | Whether to remove torrent from Deluge                              | `true`                                |
| `DELUGE_STATE_PATH`      | Deluge state path inside the container                             | `/deluge/state`                       |
| `TORRENT_FILE_DEST_PATH` | Temp path inside the container to store `.torrent` files           | `/torrents`                           |

### Volume Mappings

- `-v /path/to/deluge/config:/deluge`: This maps your Deluge configuration directory into the container. The script needs this to find the `.torrent` files in the `state` sub-directory.
- `-v /path/to/downloads:/downloads/completed`: This maps your main downloads folder. **Crucially, the host path (`/path/to/downloads`) should be the same one that both Deluge and qBittorrent use.** This allows qBittorrent to find the data and re-check it without re-downloading.
- `-v ./torrents:/torrents`: A temporary folder on the host to store `.torrent` files during the migration process. You can create an empty `torrents` directory in the same folder as your `docker-compose.yml`.

---

## 🏗️ Development

To run the script locally for development:

1. Clone the repository:

   ```bash
   git clone https://git.sharez.vip/me/deluge2qbit.git
   cd deluge2qbit
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set the environment variables (e.g., by creating a `.env` file and using `python-dotenv`).
4. Run the script:

   ```bash
   python main.py
   ```

---

## 🚢 CI/CD

Image is built and pushed to:

- Docker Hub: [`amit94302/deluge2qbit`](https://hub.docker.com/r/amit94302/deluge2qbit)
- GitHub Container Registry: [`ghcr.io/amit94302/deluge2qbit`](https://github.com/users/amit94302/packages/container/package/deluge2qbit)

Trigger: On push to `main`

---

## 📄 License

[MIT](LICENSE)
