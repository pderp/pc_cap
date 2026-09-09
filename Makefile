PY ?= /home/derp/cap/venv/bin/python
export HF_HOME ?= /home/derp/cap/assets/hf_cache

.PHONY: test-fast test test-gpu lint status install

install:
	$(PY) -m pip install -e . --no-deps -q

test-fast:
	$(PY) -m pytest -q -m "not gpu and not slow"

test:
	$(PY) -m pytest -q

test-gpu:
	$(PY) -m pytest -q -m gpu

lint:
	$(PY) -m ruff check src tests scripts

status:
	$(PY) -m pccap.harness.status
