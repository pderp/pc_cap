# DATA-02a: permission to connect the confirmation loader

Status: awaiting lead permission. Agent: codex. No existing file has been edited.

The latest user instruction says: “waiting for my permission if you need to make changes
to any existing file.” This overrides `docs/ongoing4.md` §1 rule 7's permission to
replace lane-owned placeholders.

## Exact proposed edit

Apply `docs/tasks/DATA-02a-confirm-api.patch` to **only**
`src/pccap/data/confirm.py`. It replaces the one-line ENV-03 placeholder with the public
`load(manifest_path, frozen=ROOT / "manifests" / "frozen.json")` wrapper, delegating to
the new, tested `load_frozen_manifest` implementation. S4 already imports this API.

The original file's SHA-256 is recorded in `DATA-02a.claim.json`. Git's
`apply --check` passes, and the proposed code was also compiled in memory and exercised
against a synthetic valid manifest and a missing freeze. The actual public file remains
unchanged.

## Prepared and verified

- New integrity helper and sealing CLI; 90 targeted tests pass, including the firewall.
- Six new metadata-only sidecars, copied from the existing aggregate and checked against
  the recorded index and draft bindings without opening confirmation payloads.
- New metadata README, task record, and verification logs under `results/data02a/`.
- Ruff passes for all three new Python files.

Approval of this request authorizes only the public API patch. After applying it, run
CPU checks with fresh test/log paths and add a completion record. It does not authorize
editing the shared board, modifying a freeze or any existing seal, changing dependencies,
or using the GPU.

The separate GRACE environment pin in `S2-05a-environment-edit-request.md` remains
unapproved and has not been performed.
