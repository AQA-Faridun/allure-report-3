# Thin wrappers around uv / pytest / Allure 3. Extra pytest args: make test ARGS="-k cart -n 4"
ARGS ?=
FULL ?=
CLEAN_DIRS := allure-results allure-report test-results
ALLURE := npx allure
PYTEST := uv run pytest

.PHONY: install test test-open smoke api web e2e demo all report open run-summary clean lint

install:            ## Python deps, Chromium, Allure 3 CLI
	uv sync
	uv run playwright install chromium
	npm ci

test:               ## Default run (everything except demo_failures) + report + quality gate
	$(ALLURE) run -- $(PYTEST) $(ARGS)

# `;` instead of `&&`: the report opens even when tests or the quality gate fail.
test-open:          ## Default run, then open the report (opens even if tests fail)
	$(ALLURE) run -- $(PYTEST) $(ARGS); $(ALLURE) open ./allure-report

smoke:              ## Smoke tests only
	$(ALLURE) run -- $(PYTEST) -m smoke $(ARGS)

api:                ## API tests only
	$(ALLURE) run -- $(PYTEST) -m api $(ARGS)

web:                ## Web UI tests (incl. e2e)
	$(ALLURE) run -- $(PYTEST) -m web $(ARGS)

e2e:                ## End-to-end flows only
	$(ALLURE) run -- $(PYTEST) -m e2e $(ARGS)

demo:               ## Intentionally red tests: failed / broken / flaky / known issues
	$(ALLURE) run -- $(PYTEST) -m demo_failures $(ARGS)

all:                ## Main suite + demo failures in one report
	$(ALLURE) run -- $(PYTEST) -m "" $(ARGS)

report:             ## Rebuild the report from ./allure-results (appends to history)
	$(ALLURE) generate ./allure-results

open:               ## Serve the built report in the browser
	$(ALLURE) open ./allure-report

run-summary:        ## Summary of the last run from ./allure-results -> docs/run-summary.md
	uv run python scripts/make_run_summary.py

lint:               ## ruff + mypy
	uv run ruff check src tests
	uv run ruff format --check src tests
	uv run mypy src tests

clean:              ## Empty results/report folders; FULL=1 removes the folders too (.allure/ history is kept)
ifeq ($(FULL),1)
	rm -rf $(CLEAN_DIRS)
else
	for dir in $(CLEAN_DIRS); do [ ! -d "$$dir" ] || find "$$dir" -mindepth 1 -delete; done
endif
