# CLAUDE.md

## Project Overview

gmail-streamer is a Python CLI tool that downloads Gmail messages matching configurable filters via OAuth2, organized by profiles.

## Build & Run

```bash
uv sync                                  # Install dependencies
gmail-streamer --profile <name>          # Run with a profile
gmail-streamer --profile <name> --profile-dir ./profiles  # Custom profile dir
```

## Architecture

- `src/gmail_streamer/cli.py` — Click CLI entry point, wires all modules together
- `src/gmail_streamer/config.py` — Loads and validates `config.yaml` into a `ProfileConfig` dataclass
- `src/gmail_streamer/auth.py` — OAuth2 flow using google-auth-oauthlib, token caching
- `src/gmail_streamer/gmail_client.py` — Gmail API wrapper: search, fetch raw messages, fetch attachments
- `src/gmail_streamer/storage.py` — Saves `.eml` files and attachment files to disk
- `src/gmail_streamer/state.py` — Tracks downloaded message IDs in `state.json`

## Profile Structure

Each profile lives in `profiles/<name>/` with:
- `config.yaml` — filter query, target directory, mode (full/attachments_only)
- `credentials.json` — user-provided OAuth client credentials
- `token.json` — auto-generated after first OAuth flow
- `state.json` — auto-generated set of downloaded message IDs

## Key Conventions

- Python 3.10+, uses hatchling build backend with uv
- No tests yet
- Sensitive files (token.json, state.json, credentials.json) are gitignored
