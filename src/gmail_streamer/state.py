import json
from pathlib import Path


class State:
    def __init__(self, path: Path):
        self.path = path
        self.downloaded_ids: set[str] = set()
        self._load()

    def _load(self):
        if self.path.exists():
            with open(self.path) as f:
                self.downloaded_ids = set(json.load(f))

    def save(self):
        with open(self.path, "w") as f:
            json.dump(sorted(self.downloaded_ids), f, indent=2)

    def is_downloaded(self, msg_id: str) -> bool:
        return msg_id in self.downloaded_ids

    def mark_downloaded(self, msg_id: str):
        self.downloaded_ids.add(msg_id)
