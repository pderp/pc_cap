import hashlib
import json

from aw.supplemental_audit import Audit, bindings


def test_byte_mutation_and_missing_source_fail(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text('recorded')
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    audit = Audit()
    assert audit.check(source, expected)['status'] == 'PASS'
    source.write_text('changed')
    assert audit.check(source, expected)['status'] == 'FAIL'
    assert audit.check(tmp_path / 'absent', expected)['status'] == 'FAIL'


def test_nested_file_binding_excludes_parameter_identity():
    h = '0' * 64
    value = {'nested': [{'path': '/tmp/reader.npz', 'sha256': h}],
             'sources_sha256': {'aw/producer.py': h}, 'reader_params_sha256': h}
    assert set(bindings(value)) == {('/tmp/reader.npz', h), ('aw/producer.py', h)}


def test_completion_requires_time_and_item_coverage(tmp_path):
    receipt = tmp_path / 'finish.json'
    receipt.write_text(json.dumps({'status': 'complete', 'items_completed': 2, 'items_planned': 3}))
    report = Audit().report('fixture', receipt)
    assert report['status'] == 'FAIL'
    assert len(report['receipts'][0]['errors']) == 2
    receipt.write_text(json.dumps({'status': 'resource_stop', 'items_completed': 2, 'items_planned': 3}))
    report = Audit().report('fixture', receipt)
    assert report['status'] == 'PASS'
    assert report['receipts'][0]['status'] == 'resource_stop'


def test_option_r_charges_enclosing_process_once(tmp_path):
    finish = tmp_path / 'finish.json'
    finish.write_text(json.dumps({'cell_id': 'cell-a', 'returncode': 0,
                                  'charged_process_wall_seconds': 3.0}))
    report = tmp_path / 'report.json'
    data = {'task': 'R-3', 'cells': [{'cell_id': 'cell-a', 'artifact_complete': True}],
            'charged_process_seconds': 3.0,
            'sources_sha256': {str(finish): hashlib.sha256(finish.read_bytes()).hexdigest()}}
    report.write_text(json.dumps(data))
    assert Audit().report('Option R fixture', report)['status'] == 'PASS'
    data['charged_process_seconds'] = 4.0
    report.write_text(json.dumps(data))
    assert Audit().report('Option R fixture', report)['status'] == 'FAIL'


def test_profile_checkpoint_list_is_not_a_report_dict(tmp_path):
    path = tmp_path / 'checkpoints.json'
    path.write_text('[{"items": 100}]')
    assert Audit().report('profile', path)['status'] == 'PASS'
