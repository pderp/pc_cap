# HT-1 empirical survival plot correction

Change where="post" to where="pre" in scripts/ht_plot_audit.py. The plotted ordinate is P(H >= threshold); between adjacent observed values it must use the next observed value's count. With post stepping the sparse gap before the maximum is drawn at2/n rather than1/n. Numerical audit.json statistics and paired comparisons are unaffected.

Corrected preview: logs/heavy_tail/audit-20260915-round15/mean_vs_tail-corrected-preview.pdf (and SVG). The exact one-line source patch is HT-1-plot-step-correction.patch. Approval requested to apply it and regenerate the existing mean_vs_tail.pdf, mean_vs_tail.svg and mean_vs_tail-preview.png from the corrected source. No source results or assay numbers change.
