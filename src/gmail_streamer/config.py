from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ProfileConfig:
    filter: str
    target_directory: str
    mode: str = "full"  # "full" or "attachments_only"

    def __post_init__(self):
        if self.mode not in ("full", "attachments_only"):
            raise ValueError(f"Invalid mode: {self.mode!r}. Must be 'full' or 'attachments_only'.")


def load_config(profile_dir: Path) -> ProfileConfig:
    config_path = profile_dir / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path) as f:
        data = yaml.safe_load(f)
    config = ProfileConfig(**data)
    target = Path(config.target_directory)
    if not target.is_absolute():
        config.target_directory = str((profile_dir / target).resolve())
    return config
