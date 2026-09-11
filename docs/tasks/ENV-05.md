# ENV-05 — environment recreation

Status: **done**. Agent: Codex. Completed under the user's approval of
`updated_plan6.md` section 5, **D-F only**, on 2026-09-11.
CPU/network validation; GPU seconds: **0**.

## Inputs and outputs

Inputs: unchanged `requirements.lock` (150 pinned packages plus the private editable
pccap entry), Python 3.12.14, local checkout
`af98eab218ef55308be333615c9a228a0b0eb5ef` with the approved D-F patches applied.

Outputs: existing `scripts/setup_venv.{sh,py}` exercised in real-install mode;
`docs/environment.md` recreation section applied and refreshed; a new environment
at `/home/derp/cap/assets/envs/venv-check-plan6-df`; logs and verification records in
`results/ENV05/plan6_df_install/`. Caches and temporary build resources stay under
`assets/tmp/env05-20260911T103227534139Z/`.

## Verify command

The completed invocation was:

```bash
PCCAP_SETUP_PYTHON=/home/derp/cap/venv/bin/python \
  PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 \
  GIT_OPTIONAL_LOCKS=0 scripts/setup_venv.sh \
  --venv /home/derp/cap/assets/envs/venv-check-plan6-df \
  --out results/ENV05/plan6_df_install
```

Those destinations now exist and intentionally cannot be reused. A reproduction
must select new environment and evidence paths. Network access was approved for
this install. The helper runs pip against a scratch copy of the lock with only the
private editable line removed, then installs `pccap` from the local checkout with
`--no-deps --no-build-isolation -e`.

## Verify output and done-when check

| Check | Result | Evidence under `results/ENV05/plan6_df_install/` |
| --- | --- | --- |
| Create fresh environment | exit 0 | `create_venv.txt` |
| Install locked dependencies | exit 0 | `install_lock.txt` |
| Install local editable pccap | exit 0; pccap 0.0.1 | `install_checkout.txt` |
| Dependency consistency | No broken requirements found; exit 0 | `pip_check.txt` |
| CPU determinism report | JAX 0.11.1, CPU, highest matmul precision, x64 off, partitionable Threefry off | `determinism.txt` |
| Compare installed versions to lock | **150/150 exact matches** | `installed_packages.json`, `verification.json` |
| Editable provenance | `file:///home/derp/cap/pc_cap`, editable true | `installed_packages.json` |
| Preserve active package inventory and lock | unchanged | `verification.json` |
| Document recreation | section applied and updated | `docs/environment.md` |

All required ENV-05 completion checks pass. The two additional distributions beyond
the retained pins are local `pccap==0.0.1` and bootstrap `pip==26.0.1`; pip is not
pinned by this freeze output. Package identity is verified at the version level;
this is not a claim of bit-identical rebuilt wheels. The setup record identifies
the dirty checkout used at installation, rather than claiming a clean-revision build.

The helper did not modify the active venv or the lock. The authorized local editable
installation can update ignored `src/pccap.egg-info` metadata in the shared checkout.
The package is editable, so future source changes remain visible to this scratch env.
No files in FabricPC or the other reference repository were changed.

## Cost, CUDA and previous evidence

The real setup took approximately **158.58 seconds**, measured from the setup record's
start timestamp to its completion file timestamp. This is additional to the previously
recorded development work; GPU use was zero. CUDA 13 JAX plugins and libraries are
installed from the lock. `CUDA_VISIBLE_DEVICES=''` and `JAX_PLATFORMS=cpu` apply only
to the verification processes. GPU execution in this scratch environment has not
been validated and is not required by D-F's CPU check.

The earlier resolution-only evidence is preserved: the sandbox-DNS failure in
`results/ENV05/venv-check/`, followed by the successful approved network dry run in
`results/ENV05/network_check/`. Those historical records remain accurate for their
respective attempts. `docs/tasks/ENV-05-environment.patch` is the original approved
proposal; the live environment document now includes the real-install result.

The approved review scripts/helper pass Ruff, and 14 related CPU controls pass;
see `results/PLAN6/DF/validation.json`. No threshold, baseline parity rule, production
freeze, GPU allowance, S6 decision or grammar-promotion decision was changed.
Unresolved ENV-05 tasks: none within the approved scope.
