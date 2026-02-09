<div align="center">
  <img src="logo.png" alt="gmail-streamer" width="512"/>

  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

  **📧 Download Gmail messages matching your filters to local files 📥**

</div>

## ✨ Features

- **🗂️ Profile-based configuration** — run multiple independent download profiles, each with its own filters, credentials, and output directory
- **🔐 OAuth2 authentication** — secure Google sign-in with automatic token caching
- **📧 Full message download** — save complete `.eml` files for archival
- **📎 Attachments-only mode** — grab just the attachments, skip the rest
- **🧠 State tracking** — remembers what's already been downloaded, no duplicates across runs
- **🔍 Gmail search filters** — use any Gmail search query (`from:`, `has:attachment`, `after:`, label filters, etc.)

## 🚀 Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Create a profile

```
profiles/
  my-profile/
    config.yaml
    credentials.json
```

### 3. Add your Gmail OAuth credentials

Place your `credentials.json` (from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)) into the profile directory.

### 4. Configure the profile

Create `config.yaml`:

```yaml
filter: "from:example@gmail.com has:attachment"
target_directory: "./downloads"
mode: "full"  # or "attachments_only"
```

### 5. Run

```bash
gmail-streamer --profile my-profile
```

On first run, a browser window opens for OAuth authorization. Subsequent runs reuse the cached token.

## ⚙️ Profile Structure

Each profile lives in `profiles/<name>/` with:

| File | Purpose |
|------|---------|
| `config.yaml` | Filter query, target directory, download mode |
| `credentials.json` | OAuth client credentials (you provide this) |
| `token.json` | Auto-generated after first OAuth flow |
| `state.json` | Auto-generated set of downloaded message IDs |

## 🏗️ Architecture

| Module | Responsibility |
|--------|---------------|
| `cli.py` | Click CLI entry point |
| `config.py` | Loads and validates `config.yaml` into a `ProfileConfig` dataclass |
| `auth.py` | OAuth2 flow with token caching |
| `gmail_client.py` | Gmail API wrapper: search, fetch messages, fetch attachments |
| `storage.py` | Saves `.eml` files and attachments to disk |
| `state.py` | Tracks downloaded message IDs in `state.json` |

## 📄 License

[MIT](LICENSE)
