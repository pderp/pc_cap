"""Read-only archival resolution for publication updates and the R-2 repair.

Runtime PC source resolution is unchanged. Only exact hashes in the reviewed
archive manifest can resolve to preserved original bytes.
"""
from __future__ import annotations

import json
from pathlib import Path

from aw.pc_historical import Sources as PCSources
from aw.pc_historical import sha


class Sources(PCSources):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archives = {}
        for name in ('round58-source-archive', 'round61-source-archive'):
            manifest = self.root / 'docs/tasks' / name / 'manifest.json'
            if manifest.exists():
                self.archives.update(json.loads(manifest.read_bytes()))
                self.bindings[str(manifest)] = sha(manifest)

    def resolve(self, name, expected):
        path = Path(name)
        path = path if path.is_absolute() else self.root / path
        try:
            return super().resolve(path, expected)
        except ValueError:
            if not path.is_relative_to(self.root):
                raise
            record = self.archives.get(str(path.relative_to(self.root)))
            if record is None or record['sha256'] != expected:
                raise
            archived = self.root / record['archive']
            if sha(archived) != expected:
                raise ValueError(f'preserved source differs: {archived}') from None
            self.bindings[str(archived)] = expected
            self.substitutions[str(path)] = dict(path=str(archived), sha256=expected)
            return archived
