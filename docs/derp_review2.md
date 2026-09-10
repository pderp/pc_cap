# DERP Review 2 -- Follow-up Assessment of /home/derp/cap/ Project

## Overview
This review follows up on derp_review1.md, checking whether the five recommendations were addressed effectively and identifying new issues. The project has progressed through stages S0-S3 as of 2026-09-10.

## Status of Review 1 Recommendations

### 1. Consolidate ongoing logs -- NOT ADDRESSED, worsened
Original: Three ongoing files made it hard to track current state.
Current: A fourth ongoing file, ongoing.md, now exists. No archival performed.
Assessment: Not addressed. Recommend archive directory, keep only current ongoing.md.

### 2. Document venv setup -- ADDRESSED
environment.md contains detailed spec: Python version, JAX version, dependencies, lock file reference, verify command.

### 3. Review spec defects -- PARTIALLY ADDRESSED
Spec defects resolved via decisions log, but spec_defects.md itself has no status markers. Recommend adding open/resolved/superseded tags.

### 4. Add CONTRIBUTING.md -- ADDRESSED
CONTRIBUTING.md exists, 2749 bytes, dated 2026-09-10.

### 5. Consider README expansion -- ADDRESSED
README.md exists, 3773 bytes, dated 2026-09-10.

## Summary
| # | Recommendation | Status |
|---|---|---|
| 1 | Consolidate ongoing logs | Not addressed, worsened |
| 2 | Document venv setup | Addressed |
| 3 | Review spec defects | Partially addressed |
| 4 | Add CONTRIBUTING.md | Addressed |
| 5 | Expand README.md | Addressed |

## New Issues
1. Ongoing log proliferation: Four ongoing files, no archival policy. Most pressing doc issue.
2. Frozen venv reproducibility gap: requirements.lock at venv root, not in repo. Consider symlinking into pc_cap/.
3. Decision log growth without indexing: 18 decisions in decisions.md, no summary index.
4. Multi-lane orchestration complexity: ongoing.md references Lane A-F plus orchestrator.
5. ePC checkpoint regeneration risk: REG-02 is 9766 steps, up to 120 GPU-hours on RTX 5070. Verify resumability tested with forced interruption.
6. D1/D2 scope fragility: DEC-013 has 1.6h margin, fallback significantly reduces scope.
7. Test coverage visibility: No coverage report. Recommend pytest-cov with .coveragerc.
8. Determinism config implicit: Flags applied by import pccap before JAX. Fragile. Add runtime assertion in pccap.__init__.

## Recommendations
1. Archive old ongoing logs immediately. Move ongoing.md-ongoing3.md to docs/archive/, rename ongoing.md to ongoing.md.
2. Triage spec_defects.md with status tags.
3. Add decisions summary categorizing by type.
4. Test checkpoint resumability with forced interruption before full REG-02.
5. Add coverage tracking via pytest-cov.
6. Guard determinism initialization with runtime check in pccap.__init__.

## Conclusion
Three of five original recommendations addressed, one partially, one worsened. New issues center on documentation organization and risk management for REG-02. Project is well-positioned for S4/S5 if ongoing log and determinism issues are resolved.
