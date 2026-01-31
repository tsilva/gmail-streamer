from pathlib import Path

import click

from gmail_streamer.auth import get_gmail_service
from gmail_streamer.config import load_config
from gmail_streamer.gmail_client import (
    fetch_attachments,
    fetch_message_metadata,
    fetch_raw_message,
    search_messages,
)
from gmail_streamer.storage import save_attachments, save_eml, save_metadata, scan_downloaded_metadata


@click.command()
@click.option("--profile", required=True, help="Profile name")
@click.option("--profile-dir", default="./profiles", help="Base directory for profiles")
def main(profile: str, profile_dir: str):
    """Download Gmail messages matching a profile's filter."""
    profile_path = Path(profile_dir) / profile
    if not profile_path.is_dir():
        raise click.ClickException(f"Profile directory not found: {profile_path}")

    config = load_config(profile_path)
    target = Path(config.target_directory)
    target.mkdir(parents=True, exist_ok=True)

    click.echo(f"Authenticating profile '{profile}'...")
    service = get_gmail_service(profile_path)

    downloaded_ids, most_recent_date = scan_downloaded_metadata(target)
    if most_recent_date:
        click.echo(f"Resuming from {most_recent_date} ({len(downloaded_ids)} already downloaded)")

    click.echo(f"Searching: {config.filter}")
    msg_ids = search_messages(service, config.filter, after_date=most_recent_date)
    new_ids = [mid for mid in msg_ids if mid not in downloaded_ids]
    click.echo(f"Found {len(msg_ids)} messages, {len(new_ids)} new.")

    for i, msg_id in enumerate(new_ids, 1):
        click.echo(f"[{i}/{len(new_ids)}] Downloading {msg_id}...")

        metadata = fetch_message_metadata(service, msg_id)
        date = metadata["date"]

        if config.mode == "full":
            raw = fetch_raw_message(service, msg_id)
            save_eml(target, msg_id, date, raw)
            attachments = fetch_attachments(service, msg_id)
            if attachments:
                save_attachments(target, msg_id, date, attachments)

        elif config.mode == "attachments_only":
            attachments = fetch_attachments(service, msg_id)
            if attachments:
                save_attachments(target, msg_id, date, attachments)
            else:
                click.echo(f"  No attachments for {msg_id}")

        save_metadata(target, msg_id, date, metadata)

    click.echo("Done.")
