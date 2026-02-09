# CLAUDE.md

## Project Overview

gmail-streamer is a Python CLI tool that downloads Gmail messages matching configurable filters via OAuth2, organized by profiles.

## Build & Run

```bash
uv sync                                          # Install dependencies
gmail-streamer run <profile>                     # Download messages
gmail-streamer --profile-dir /path run <profile> # Custom profile dir
gmail-streamer profiles list                     # List available profiles
gmail-streamer profiles init <name>              # Scaffold new profile
gmail-streamer profiles show <name>              # Show profile config
```

## Architecture

- `src/gmail_streamer/cli.py` — Click CLI entry point (group with `run` and `profiles` subcommands)
- `src/gmail_streamer/paths.py` — Profile directory resolution and discovery
- `src/gmail_streamer/config.py` — Loads and validates `config.yaml` into a `ProfileConfig` dataclass
- `src/gmail_streamer/auth.py` — OAuth2 flow using google-auth-oauthlib, token caching
- `src/gmail_streamer/gmail_client.py` — Gmail API wrapper: search, fetch raw messages, fetch attachments
- `src/gmail_streamer/storage.py` — Saves `.eml` files and attachment files to disk

## Profile Resolution

Profiles directory is resolved in this order:
1. `--profile-dir` flag or `GMAIL_STREAMER_PROFILE_DIR` env var
2. `./profiles/` in current working directory (if it exists)
3. `~/.gmail-streamer/profiles/` (fallback)

The `profile` argument to `run` can be a name (looked up in the profiles dir) or a path to an existing directory.

## Profile Structure

Each profile lives in its own directory with:
- `config.yaml` — filter query, target directory, mode (full/attachments_only)
- `credentials.json` — user-provided OAuth client credentials
- `token.json` — auto-generated after first OAuth flow

## Key Conventions

- Python 3.12+, uses hatchling build backend with uv
- No tests yet
- Sensitive files (token.json, credentials.json) are gitignored
- README.md must be kept up to date with any significant project changes
