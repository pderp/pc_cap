# DATA-02a permission request addendum

The final PDF cross-check found one incorrect reference in the newly created task record:
the package/harness interface is **section F.7**, not Appendix H. The relevant extracted
text begins at docs/pdf_text/plan.txt:1671. Implementation and test results are unaffected.

Because the user requires permission even to edit files created during this turn, the
record remains unchanged. The exact one-line correction is prepared in
DATA-02a-reference-correction.patch. This addendum supplies the correct reference now.

Requested approval covers these two precise patches:

1. DATA-02a-confirm-api.patch: connect the tested loader through src/pccap/data/confirm.py.
2. DATA-02a-reference-correction.patch: correct the PDF section in docs/tasks/DATA-02a.md.

All other existing files remain outside this request. No GRACE environment pin, shared
board update, freeze change, seal replacement, or commit is included.
