from pathlib import Path

import click

from gmail_streamer.auth import get_gmail_service
from gmail_streamer.config import load_config
from gmail_streamer.gmail_client import fetch_attachments, fetch_raw_message, search_messages
from gmail_streamer.state import State
from gmail_streamer.storage import save_attachments, save_eml


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

    state = State(profile_path / "state.json")

    click.echo(f"Searching: {config.filter}")
    msg_ids = search_messages(service, config.filter)
    new_ids = [mid for mid in msg_ids if not state.is_downloaded(mid)]
    click.echo(f"Found {len(msg_ids)} messages, {len(new_ids)} new.")

    for i, msg_id in enumerate(new_ids, 1):
        click.echo(f"[{i}/{len(new_ids)}] Downloading {msg_id}...")

        if config.mode == "full":
            raw = fetch_raw_message(service, msg_id)
            save_eml(target, msg_id, raw)
            attachments = fetch_attachments(service, msg_id)
            if attachments:
                save_attachments(target, msg_id, attachments)

        elif config.mode == "attachments_only":
            attachments = fetch_attachments(service, msg_id)
            if attachments:
                save_attachments(target, msg_id, attachments)
            else:
                click.echo(f"  No attachments for {msg_id}")

        state.mark_downloaded(msg_id)
        state.save()

    click.echo("Done.")
