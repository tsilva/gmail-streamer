import json
from pathlib import Path


def _short_id(msg_id: str) -> str:
    return msg_id[:8]


def save_eml(target_dir: Path, msg_id: str, date: str, raw: bytes):
    """Save .eml file with date and short ID."""
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / f"{date} - {_short_id(msg_id)}.eml").write_bytes(raw)


def save_metadata(target_dir: Path, msg_id: str, date: str, metadata: dict):
    """Save metadata JSON with date and short ID."""
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{date} - {_short_id(msg_id)}.json"
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))


def save_attachments(target_dir: Path, msg_id: str, date: str, attachments: list[dict]):
    """Save attachments flat in target_dir with date and short ID."""
    target_dir.mkdir(parents=True, exist_ok=True)
    sid = _short_id(msg_id)
    for att in attachments:
        (target_dir / f"{date} - {sid} - {att['filename']}").write_bytes(att["data"])


def scan_downloaded_metadata(target_dir: Path) -> tuple[set[str], str | None]:
    """Scan metadata JSON files to derive downloaded IDs and most recent date.

    Returns (downloaded_ids, most_recent_date_or_none).
    """
    downloaded_ids: set[str] = set()
    most_recent_date: str | None = None

    for meta_path in target_dir.glob("* - *.json"):
        try:
            meta = json.loads(meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        msg_id = meta.get("id")
        date = meta.get("date")
        if msg_id:
            downloaded_ids.add(msg_id)
        if date and (most_recent_date is None or date > most_recent_date):
            most_recent_date = date

    return downloaded_ids, most_recent_date
