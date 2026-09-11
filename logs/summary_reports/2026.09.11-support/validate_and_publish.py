"""Validate the reviewed rendering and publish once, without replacing files."""

import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

SUPPORT = Path(__file__).resolve().parent
REPO = SUPPORT.parents[2]
PDF = SUPPORT / 'render-04/paper.pdf'
FINAL = SUPPORT.parent / '2026.09.11-current-status.pdf'
evidence = json.loads((SUPPORT / 'evidence_final.json').read_text())
build = json.loads((SUPPORT / 'render-04/build_checks.json').read_text())
text = subprocess.check_output(['pdftotext', '-layout', str(PDF), '-'], text=True)
info = subprocess.check_output(['pdfinfo', str(PDF)], text=True)
bbox = ET.fromstring(subprocess.check_output(['pdftotext', '-bbox', str(PDF), '-']))
ns = {'x': 'http://www.w3.org/1999/xhtml'}
pages = bbox.findall('.//x:page', ns)
assert len(pages) == build['pages'] == 17
assert build['figures'] == 9
assert all(p['remaining_flowables'] == 0 for p in build['layout'])
assert '\ufffd' not in text
for term in ['Abstract', '247,289', '4,064', '1.64%', '1,999,872', '97.5%',
             '5/210', 'S6', 'finite-iteration error credit', 'Conclusion', 'References']:
    assert term in text, term
for n in range(1, 10):
    assert re.search(r'Figure\s+' + str(n) + r'\.', text)
for n in range(1, 12):
    assert re.search(r'Table\s+' + str(n) + r'\.', text)
for n in range(1, 19):
    assert f'[{n}]' in text
word_count = 0
for page in pages:
    w, h = float(page.get('width')), float(page.get('height'))
    for word in page.findall('x:word', ns):
        x1, y1, x2, y2 = [float(word.get(k)) for k in ('xMin', 'yMin', 'xMax', 'yMax')]
        assert 0 <= x1 <= x2 <= w and 0 <= y1 <= y2 <= h, word.text
        word_count += 1
assert hashlib.sha256(PDF.read_bytes()).hexdigest() == build['pdf_sha256']
assert hashlib.sha256((SUPPORT / 'evidence_final.json').read_bytes()).hexdigest() == build['evidence_sha256']
for row in evidence['runs']:
    config = row['config']
    assert config['frozen_manifest_sha256'] == evidence['frozen_sha256']
    assert config['status'] == 'complete'
    assert config['base_hash_before'] == config['base_hash_after']
    assert config['metrics']['lm_drift_perplexity_ratio']['n'] == 4064
assert evidence['sources']['manifests/dev/lm_sets.json']['content']['files']['drift_tokens']['shape'] == [247289]
assert 'drift_sample(4096)' in evidence['sources']['src/pccap/harness/stage_s4.py']['content']
for path in SUPPORT.glob('*.py'):
    compile(path.read_text(), str(path), 'exec')
# Scientific code is read only. Report sources and figures live outside src/pccap.
scientific_source_changes = subprocess.check_output(['git', 'diff', '--name-only', '--', 'src/pccap'], cwd=REPO, text=True)
with FINAL.open('xb') as f:
    f.write(PDF.read_bytes())
result = {
    'status': 'validated_and_published',
    'published_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    'evidence_cutoff_utc': evidence['capture_finished_utc'],
    'final_pdf': str(FINAL.relative_to(REPO)), 'pdf_sha256': build['pdf_sha256'],
    'pages': len(pages), 'figures': build['figures'], 'tables': 11,
    'references': 18, 'text_word_count': word_count,
    'all_page_frames_fit': True, 'all_extracted_text_inside_page': True,
    'text_extraction_and_key_claim_checks': 'passed',
    'visual_review': 'All 17 final pages reviewed in a contact sheet; pages 9, 12, 15 and 16 additionally inspected individually; earlier full-size checks covered figures 2 and 4.',
    'git_diff_scientific_source_at_publish': scientific_source_changes,
    'gpu_seconds_used_for_report': 0,
    'existing_files_modified_by_report_work': [],
    'committed': False,
}
with (SUPPORT / 'validation.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
with (SUPPORT / 'final_pdfinfo.txt').open('x') as f:
    f.write(info)
print(json.dumps(result, indent=2))
