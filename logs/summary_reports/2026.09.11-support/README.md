# Research status paper, 11 September 2026

The delivered report is [2026.09.11-current-status.pdf](../2026.09.11-current-status.pdf): 17 pages, nine figures, eleven tables and eighteen local primary-source references. It covers research questions, apparatus, all six substrate properties, development results, the confirmatory snapshot, verification, timeline, resources, risks and remaining concurrent work.

The research snapshot ends at **2026-09-11 12:39:45 EDT / 16:39:45 UTC**. The active queue continued afterward. All five captured completed jobs are zsRE/C0, realization 0; they are not a C2 comparison.

## Authoritative supporting files

- `evidence_final.json`: parsed JSON and full text source contents, original-file SHA-256 hashes, five completed v2 run aggregates, queue progress and the historical full P1 artifact. DATA-04 and P5 supplements were retrieved from the same Git HEAD as the original snapshot, preserving its cutoff.
- `build_status_paper_v4.py`: final renderer and manuscript source.
- `render-04/manuscript.md`: readable text companion. The delivered PDF is the layout authority.
- `render-04/fig*.png` and `render-04/fig*.pdf`: all nine figures, with vector PDF exports for reuse.
- `render-04/build_checks.json`: layout measurements, figure arithmetic and hashes.
- `validation.json` and `final_pdfinfo.txt`: publication checks, page/text verification and visual-review record.

The PDF SHA-256 is `790b2eba518ca11f6b933a54b67b6eb5b68ba1792fecded49836c6357d07ebfd`.

## Material finding

PDF section 8 distinguishes the original million-token request from **SD-3's approved full-validation substitute of 247,289 unique tokens**. The actual S4/S5 evaluator selects only 4,096 tokens and the completed S4 records score 4,064 prediction positions. No authorization for that further reduction was found in the reviewed decisions. The report recommends lead assessment of a versioned remedy or an explicitly approved checkpoint evaluation, with its resource implications recorded. This reporting work did not edit or stop the queue.

The paper also separates the historical 1,999,872-position P1 audit from its smaller 199,680-position follow-up, labels learned CR correctly, keeps B4 unavailable, and distinguishes obsolete B4 projection terms from scheduled work.

## Rebuild this dated paper

Run from the pc_cap root. Choose a destination that does not exist:

```bash
PYTHONDONTWRITEBYTECODE=1 \
MPLCONFIGDIR=/home/derp/cap/assets/tmp/status-paper-mpl \
/home/derp/cap/assets/envs/status-paper-20260911/bin/python \
  logs/summary_reports/2026.09.11-support/build_status_paper_v4.py \
  logs/summary_reports/2026.09.11-support/evidence_final.json \
  logs/summary_reports/2026.09.11-support/rebuild-new
```

The isolated publishing environment uses ReportLab 5.0.1, Matplotlib 3.11.1, NumPy 2.5.3 and Pillow 12.3.0. Dependencies and plotting caches live under `assets/`; JAX and the research execution environment were not modified. Font assets come from Matplotlib's bundled DejaVu fonts. Rebuilding can change PDF timestamp metadata and thus its byte hash.

`capture_status_evidence_v2.py` can capture a later snapshot to a new file. The manuscript is intentionally specific to this dated evidence and must be reviewed before use with a later snapshot. `validate_and_publish.py` is a one-time publisher: it refuses to replace the delivered PDF.

## Intermediate files

Earlier capture/render versions and `render-01` through `render-03` are **superseded publishing drafts**, retained under the user's new-files-only protocol. In particular, the first draft had not yet reconciled SD-3's approved validation shortfall. Do not cite those drafts as research conclusions. `render-02` failed a page-fit check before a PDF was written. The final version above incorporates that reconciliation, complete table numbering and the additional property scorecard.

No existing repository files were edited, no scientific experiments were run, no GPU time was used and no commit was made for this report.
