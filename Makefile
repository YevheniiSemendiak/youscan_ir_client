setup:
	pip install -U pip
	pip install -e .[dev]
	pre-commit install

lint: format
	mypy youscan_ir_client tests

format:
ifdef CI_LINT_RUN
	pre-commit run --all-files --show-diff-on-failure
else
	pre-commit run --all-files
endif

test:
	pytest -vv tests
