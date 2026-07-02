SHELL := /bin/bash

PY_FILES := scripts

# Cyclomatic Complexity Number 한도. 이 값을 초과한 함수는 warning으로 잡힌다.
MAX_CCN ?= 15
# Non-comment Lines Of Code 한도. 주석/빈 줄을 제외한 함수 실제 코드 줄 수 기준이다.
MAX_NLOC ?= 50
# 함수 parameter 개수 한도. 이 값을 초과한 함수는 warning으로 잡힌다.
MAX_PARAMETERS ?= 8
# lizard 공통 옵션. -V는 verbose location 출력, -T nloc=...은 NLOC threshold다.
LIZARD_OPTS := -l python -V -C $(MAX_CCN) -T nloc=$(MAX_NLOC) -a $(MAX_PARAMETERS)

.PHONY: lint format complexity complexity-file complexity-func complexity-check complexity-file-check test check

lint:
	uv run ruff check .

format:
	uv run ruff format .

complexity:
	uv run lizard $(PY_FILES) $(LIZARD_OPTS)
	uv run complexipy $(PY_FILES) --plain --ignore-complexity

complexity-check:
	uv run lizard $(PY_FILES) $(LIZARD_OPTS) -w
	uv run complexipy $(PY_FILES) --plain --ignore-complexity

test:
	uv run python -m unittest discover -s scripts/tests

check: lint complexity-check test
