"""A second publication refresh must not hide earlier exact source versions."""

import json

import pytest

from aw.reporting_sources import Sources, sha


def test_two_versions_of_one_reporter_and_unknown_drift(tmp_path):
    stage = tmp_path / 'stage'
    stage.mkdir()
    for name in ('sources.json', 'reporting-sources.json'):
        (stage / name).write_text('{}')
    live = tmp_path / 'aw/reporter.py'
    live.parent.mkdir()
    live.write_text('current')
    originals = []
    for name, text in [('round61-source-archive', 'first'), ('round63-source-archive', 'second')]:
        folder = tmp_path / 'docs/tasks' / name
        folder.mkdir(parents=True)
        archived = folder / live.name
        archived.write_text(text)
        (folder / 'manifest.json').write_text(json.dumps({'aw/reporter.py': {
            'sha256': sha(archived), 'archive': str(archived.relative_to(tmp_path))}}))
        originals.append(archived)
    reader = Sources(root=tmp_path, stage=stage)
    for original in originals:
        assert reader.resolve(live, sha(original)) == original
    with pytest.raises(ValueError, match='unapproved source drift'):
        reader.resolve(live, '0' * 64)
    originals[0].write_text('tampered')
    with pytest.raises(ValueError, match='preserved source differs'):
        reader.resolve(live, next(k[1] for k in reader.archives if k[1] != sha(originals[1])))
