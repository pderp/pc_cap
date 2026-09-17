"""R1-D9 clearance producer: inspect by default; owner-authorized writes explicitly."""

from scripts.r1_d9_receipts import main

if __name__ == "__main__":
    raise SystemExit(main("clearance"))
