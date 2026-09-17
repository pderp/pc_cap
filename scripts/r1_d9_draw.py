"""R1-D9 draw: independent by default; family mode requires DEC-062 admission."""

from scripts.r1_d9_receipts import main
from scripts.r1_d9f_allocation import admitted_mode, allocate  # noqa: F401

if __name__ == "__main__":
    raise SystemExit(main("draw"))
