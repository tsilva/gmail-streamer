from pathlib import Path


def save_eml(target_dir: Path, msg_id: str, raw: bytes):
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / f"{msg_id}.eml").write_bytes(raw)


def save_attachments(target_dir: Path, msg_id: str, attachments: list[dict]):
    att_dir = target_dir / msg_id
    att_dir.mkdir(parents=True, exist_ok=True)
    for att in attachments:
        (att_dir / att["filename"]).write_bytes(att["data"])
