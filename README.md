<div align="center">
  <img src="logo.png" alt="gmail-streamer" width="512"/>

  [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

  **📧 Download Gmail messages matching your filters to local files 📥**

</div>

## ✨ Features

- **🗂️ Profile-based configuration** — run multiple independent download profiles, each with its own filters, credentials, and output directory
- **🔐 OAuth2 authentication** — secure Google sign-in with automatic token caching
- **📧 Full message download** — save complete `.eml` files for archival
- **📎 Attachments-only mode** — grab just the attachments, skip the rest
- **🧠 Incremental downloads** — remembers what's already been downloaded, no duplicates across runs
- **🔍 Gmail search filters** — use any Gmail search query (`from:`, `has:attachment`, `after:`, label filters, etc.)
- **🏠 Works from anywhere** — install with `pipx` and run from any directory

## 🚀 Quick Start

### 1. Install

```bash
pipx install gmail-streamer
# or
uv tool install gmail-streamer
```

### 2. Create a profile

```bash
gmail-streamer profiles init my-profile
```

This creates `~/.gmail-streamer/profiles/my-profile/` with a template `config.yaml`.

### 3. Add your Gmail OAuth credentials

Place your `credentials.json` (from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)) into the profile directory.

### 4. Configure the profile

Edit `~/.gmail-streamer/profiles/my-profile/config.yaml`:

```yaml
filter: "from:example@gmail.com has:attachment"
target_directory: "./downloads"
mode: "full"  # or "attachments_only"
```

### 5. Run

```bash
gmail-streamer run my-profile
```

On first run, a browser window opens for OAuth authorization. Subsequent runs reuse the cached token.

## 📁 Profile Resolution

The profiles directory is resolved in this order:

1. `--profile-dir` flag or `GMAIL_STREAMER_PROFILE_DIR` env var
2. `./profiles/` in the current working directory (if it exists)
3. `~/.gmail-streamer/profiles/` (default)

The `profile` argument can be a **name** (looked up in the profiles directory) or a **path** to an existing directory (backward compatible).

## 🛠️ CLI Reference

```bash
gmail-streamer run <profile>                     # Download messages
gmail-streamer --profile-dir /path run <profile>  # Custom profiles directory
gmail-streamer profiles list                      # List available profiles
gmail-streamer profiles init <name>               # Scaffold a new profile
gmail-streamer profiles show <name>               # Show profile config
```

## ⚙️ Profile Structure

Each profile lives in its own directory with:

| File | Purpose |
|------|---------|
| `config.yaml` | Filter query, target directory, download mode |
| `credentials.json` | OAuth client credentials (you provide this) |
| `token.json` | Auto-generated after first OAuth flow |

## 🏗️ Architecture

| Module | Responsibility |
|--------|---------------|
| `cli.py` | Click CLI entry point (group with `run` and `profiles` subcommands) |
| `paths.py` | Profile directory resolution and discovery |
| `config.py` | Loads and validates `config.yaml` into a `ProfileConfig` dataclass |
| `auth.py` | OAuth2 flow with token caching |
| `gmail_client.py` | Gmail API wrapper: search, fetch messages, fetch attachments |
| `storage.py` | Saves `.eml` files and attachments to disk |

## 📄 License

[MIT](LICENSE)
