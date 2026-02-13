import json
from pathlib import Path


def _short_id(msg_id: str) -> str:
    return msg_id[:8]


def _month_dir(target_dir: Path, date: str) -> Path:
    """Return target_dir/YYYY-MM for a YYYY-MM-DD date string."""
    return target_dir / date[:7]


def save_eml(target_dir: Path, msg_id: str, date: str, raw: bytes):
    """Save .eml file with date and short ID in a YYYY-MM subfolder."""
    dest = _month_dir(target_dir, date)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{date} - {_short_id(msg_id)}.eml").write_bytes(raw)


def save_metadata(target_dir: Path, msg_id: str, date: str, metadata: dict):
    """Save metadata JSON with date and short ID in a YYYY-MM subfolder."""
    dest = _month_dir(target_dir, date)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{date} - {_short_id(msg_id)}.json"
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))


def save_attachments(target_dir: Path, msg_id: str, date: str, attachments: list[dict]):
    """Save attachments in a YYYY-MM subfolder with date and short ID."""
    dest = _month_dir(target_dir, date)
    dest.mkdir(parents=True, exist_ok=True)
    sid = _short_id(msg_id)
    for att in attachments:
        (dest / f"{date} - {sid} - {att['filename']}").write_bytes(att["data"])


def _scan_json_files(glob_iter, downloaded_ids: set[str], most_recent_date: str | None) -> str | None:
    """Parse metadata JSON files and accumulate IDs and most recent date."""
    for meta_path in glob_iter:
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
    return most_recent_date


def scan_downloaded_metadata(
    target_dir: Path, from_date: str | None = None, to_date: str | None = None
) -> tuple[set[str], str | None]:
    """Scan metadata JSON files to derive downloaded IDs and most recent date.

    Scans both flat files in target_dir (backward compat) and YYYY-MM subdirectories.
    If from_date/to_date are provided, only YYYY-MM folders overlapping the range are scanned.

    Returns (downloaded_ids, most_recent_date_or_none).
    """
    downloaded_ids: set[str] = set()
    most_recent_date: str | None = None

    # Scan flat files in root (backward compat with pre-YYYY-MM files)
    most_recent_date = _scan_json_files(target_dir.glob("* - *.json"), downloaded_ids, most_recent_date)

    # Scan YYYY-MM subdirectories
    if not target_dir.is_dir():
        return downloaded_ids, most_recent_date

    for subdir in sorted(target_dir.iterdir()):
        if not subdir.is_dir() or len(subdir.name) != 7:
            continue
        folder_month = subdir.name
        if from_date and folder_month < from_date[:7]:
            continue
        if to_date and folder_month > to_date[:7]:
            continue
        most_recent_date = _scan_json_files(subdir.glob("* - *.json"), downloaded_ids, most_recent_date)

    return downloaded_ids, most_recent_date
