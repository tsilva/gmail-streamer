from pathlib import Path

import click
import yaml

from gmail_streamer.auth import get_gmail_service
from gmail_streamer.config import load_config
from gmail_streamer.gmail_client import (
    fetch_attachments,
    fetch_message_metadata,
    fetch_raw_message,
    search_messages,
)
from gmail_streamer.paths import get_profiles_dir, list_profiles, resolve_profile
from gmail_streamer.storage import save_attachments, save_eml, save_metadata, scan_downloaded_metadata


@click.group()
@click.option(
    "--profile-dir",
    envvar="GMAIL_STREAMER_PROFILE_DIR",
    default=None,
    type=click.Path(file_okay=False),
    help="Override profiles directory.",
)
@click.pass_context
def main(ctx, profile_dir):
    """Download Gmail messages matching configurable filters."""
    ctx.ensure_object(dict)
    ctx.obj["profiles_dir"] = get_profiles_dir(profile_dir)


@main.command()
@click.argument("profile")
@click.option("--from", "from_date", default=None, type=str, help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", default=None, type=str, help="End date (YYYY-MM-DD)")
@click.pass_context
def run(ctx, profile, from_date, to_date):
    """Download messages for a profile."""
    profiles_dir = ctx.obj["profiles_dir"]
    profile_path = resolve_profile(profile, profiles_dir)

    if not profile_path.is_dir():
        raise click.ClickException(f"Profile directory not found: {profile_path}")

    config = load_config(profile_path)
    target = Path(config.target_directory)
    target.mkdir(parents=True, exist_ok=True)

    click.echo(f"Authenticating profile '{profile_path.name}'...")
    service = get_gmail_service(profile_path)

    if from_date or to_date:
        # Explicit date range mode — ignore incremental tracking
        downloaded_ids, _ = scan_downloaded_metadata(target, from_date=from_date, to_date=to_date)
        click.echo(f"Date range: {from_date or 'beginning'} to {to_date or 'now'} ({len(downloaded_ids)} already downloaded)")
        click.echo(f"Searching: {config.filter}")
        msg_ids = search_messages(service, config.filter, after_date=from_date, before_date=to_date)
    else:
        # Incremental mode (existing behavior)
        downloaded_ids, most_recent_date = scan_downloaded_metadata(target)
        if most_recent_date:
            click.echo(f"Resuming from {most_recent_date} ({len(downloaded_ids)} already downloaded)")
        click.echo(f"Searching: {config.filter}")
        msg_ids = search_messages(service, config.filter, after_date=most_recent_date)

    new_ids = [mid for mid in msg_ids if mid[:8] not in downloaded_ids]
    click.echo(f"Found {len(msg_ids)} messages, {len(new_ids)} new.")

    for i, msg_id in enumerate(new_ids, 1):
        click.echo(f"[{i}/{len(new_ids)}] Downloading {msg_id}...")

        metadata = fetch_message_metadata(service, msg_id)
        date = metadata["date"]
        subject = metadata.get("subject", "")

        if config.mode == "full":
            raw = fetch_raw_message(service, msg_id)
            save_eml(target, msg_id, date, subject, raw)
            attachments = fetch_attachments(service, msg_id)
            if attachments:
                save_attachments(target, msg_id, date, subject, attachments)

        elif config.mode == "attachments_only":
            attachments = fetch_attachments(service, msg_id)
            if attachments:
                save_attachments(target, msg_id, date, subject, attachments)
            else:
                click.echo(f"  No attachments for {msg_id}")

        save_metadata(target, msg_id, date, subject, metadata)

    click.echo("Done.")


@main.group("profiles")
def profiles_group():
    """Manage profiles."""


@profiles_group.command("list")
@click.pass_context
def profiles_list(ctx):
    """List available profiles."""
    profiles_dir = ctx.obj["profiles_dir"]
    names = list_profiles(profiles_dir)
    if not names:
        click.echo(f"No profiles found in {profiles_dir}")
        return
    click.echo(f"Profiles in {profiles_dir}:\n")
    for name in names:
        click.echo(f"  {name}")


@profiles_group.command("init")
@click.argument("name")
@click.pass_context
def profiles_init(ctx, name):
    """Scaffold a new profile directory with a template config."""
    profiles_dir = ctx.obj["profiles_dir"]
    profile_dir = profiles_dir / name

    if profile_dir.exists():
        raise click.ClickException(f"Profile already exists: {profile_dir}")

    profile_dir.mkdir(parents=True)
    config = {
        "filter": 'from:example@gmail.com has:attachment',
        "target_directory": "./downloads",
        "mode": "full",
    }
    (profile_dir / "config.yaml").write_text(yaml.dump(config, default_flow_style=False))
    click.echo(f"Created profile at {profile_dir}")
    click.echo("Next steps:")
    click.echo(f"  1. Edit {profile_dir / 'config.yaml'} with your filter")
    click.echo(f"  2. Copy your credentials.json into {profile_dir}")
    click.echo(f"  3. Run: gmail-streamer run {name}")


@profiles_group.command("show")
@click.argument("name")
@click.pass_context
def profiles_show(ctx, name):
    """Show a profile's configuration."""
    profiles_dir = ctx.obj["profiles_dir"]
    profile_path = resolve_profile(name, profiles_dir)

    if not profile_path.is_dir():
        raise click.ClickException(f"Profile not found: {profile_path}")

    config_file = profile_path / "config.yaml"
    if not config_file.exists():
        raise click.ClickException(f"No config.yaml in {profile_path}")

    click.echo(f"Profile: {profile_path.name} ({profile_path})\n")
    click.echo(config_file.read_text())
