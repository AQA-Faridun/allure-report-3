# CLAUDE.md

## Project

A demo test automation project for the public e-shop https://intershop6.skillbox.ru/ (WordPress 5.5 +
WooCommerce), with API and Web tests. The goal is to show as many **Allure Report 3** features as
possible in a report that reads like one from a real team. README.md (in Russian) is the user-facing
doc and has the "Allure feature → where it is shown" table. Keep both files in sync with the code.

## Stack

| Area | Tool | Notes |
|---|---|---|
| Language | Python 3.12 (`.python-version`) | all test code is Python; Node is only for the Allure CLI |
| Dependencies | uv: `pyproject.toml` + `uv.lock` | `package = false`, the code is imported via `pythonpath = ["src", "."]` |
| Runner | **pytest 8.4** (pinned `<9`) | pytest 9 + allure-pytest 2.16 adds a `<lambda>` teardown entry with status unknown for every fixture |
| API | httpx, **sync** | pytest and the Playwright sync API are sync; parallelism comes from xdist, so async adds nothing |
| Web | Playwright + pytest-playwright (sync), Chromium | |
| Data | mimesis | via factories only |
| Models / settings | pydantic v2, pydantic-settings | |
| Parallel / retries | pytest-xdist, pytest-rerunfailures | |
| Report | allure-pytest 2.16 + **Allure 3.21** (npm `allure`, pinned in `package-lock.json`) | Node.js required |
| Lint | ruff (lint + format), mypy strict | `make lint` must pass |

## Structure

```
allurerc.mjs                 # the only Allure 3 config: plugins, charts, history, categories, resolutions, quality gate
Makefile                     # install / test / api / web / e2e / smoke / demo / all / report / open / lint
.github/workflows/tests.yml  # CI: run tests, keep .allure history in cache, upload report
src/intershop/
  config.py                  # Settings (INTERSHOP_* env vars / .env), get_settings() is cached
  api/base_client.py         # BaseApiClient: every request = Allure step + HTTP exchange + curl attachments
  api/schema.py              # parse_response(): pydantic validation wrapped in an Allure step
  api/clients/               # ProductsClient, CartClient, WordPressClient, AccountClient
  models/store.py            # pydantic models of Store API / WP REST responses
  pages/                     # Page Objects (BasePage + pages) and components/ (header, product grid)
  data/factories.py          # CustomerFactory, BillingAddressFactory (mimesis)
  data/catalog.py            # stable reference data of the live catalog (ids, names, slugs)
  utils/attachments.py       # Allure helpers incl. Allure 3 types: http exchange, playwright trace, mermaid
  utils/money.py             # "34990,00₽" -> Decimal
tests/
  conftest.py                # hooks (reports in stash, environment.properties), auto labels, clients, data fixtures
  fixtures/web.py            # Playwright plugin: context with trace/video/HAR, logged_in_page (HTTP login -> cookies)
  fixtures/stash_keys.py     # pytest StashKeys shared by conftest and plugins
  api/  web/  e2e/           # tests by layer
  demo/                      # intentionally red tests, marker demo_failures
scripts/make_run_summary.py  # allure-results -> docs/run-summary.md (stdlib only, run by hand)
docs/run-summary.md          # generated summary of the last run, overwritten every time
.allure/                     # local Allure state (gitignored): history.jsonl, known-issues.json
```

## Discovered API (checked with real requests, 2026-10-20)

- `GET /wp-json/` lists namespaces: `wc/store` (Store API, **no** `/v1` prefix), `wc/v3` (needs auth → 401),
  `wp/v2`.
- Store API, read-only, no auth: `products` (+`search`, `category`, `on_sale`, `orderby/order`, `per_page`
  0..100, `X-WP-Total(Pages)` headers), `products/{id}`, `products/categories[/{id}]`, `products/reviews`,
  `products/collection-data`, `cart` (GET).
- Store API cart **writes need `X-WC-Store-API-Nonce`**, and the site never exposes it → 401
  `woocommerce_rest_missing_nonce`. The cart is changed via classic `POST /?wc-ajax=add_to_cart`
  (`product_id`, `quantity`) and `/?wc-ajax=remove_from_cart` (`cart_item_key`). The cart is bound to the
  session cookie of the httpx client.
- `wp/v2/search`, `wp/v2/users` (public, a real info leak, tracked as fake `SEC-17`).
- Accounts: there is no REST API. `/register/` and `/my-account/` HTML forms need a nonce scraped from the
  page. Registration fields are limited to **20 chars** (email included). Registration logs the user in.
- Checkout needs a logged-in user; empty `/checkout/` redirects to `/cart/`. Payment: "Прямой банковский
  перевод", "Оплата при доставке". The order page is `/checkout/order-received/{id}/`.
- Site links use `http://`. The base URL is `https://`; both work.

## Allure 3 notes (verified against installed allure 3.21, not just the docs)

- CLI: `allure run -- <cmd>` (runs tests, builds report, applies quality gate, exit 1 on violation),
  `allure generate <results>`, `allure open <report|results>`, `allure watch`, `allure quality-gate`,
  `allure testplan`, `allure history`, `allure known-issue`, per-plugin `allure awesome|allure2|dashboard|csv|log`.
  Run `npx allure <cmd> --help` before using a flag.
- Config is `allurerc.mjs` with `defineConfig` from `allure`. Its options: `historyPath` (JSONL),
  `historyLimit`, `flakyDetection`, `variables`, `defaultLabels`, `categories.rules`, `resolutions`,
  `qualityGate.rules`, `plugins`.
- **Known issues** live in `resolutions.rules` (`resolution: "issue" | "muted" | "accepted"`, matched by
  `messageRegexp` / `testCaseId` / ...). Issue rules need `resolutions.links.<type>.urlTemplate` with exactly
  one `%s`. The top-level `knownIssuesPath` from the website docs is outdated.
- Allure 3 content types: `application/vnd.allure.http+json` (ext `httpexchange`, rendered as a request/response
  viewer), `application/vnd.allure.playwright-trace` (embedded Trace Viewer),
  `application/vnd.allure.diagrams.mermaid`.
- Charts: `currentStatus`, `statusDynamics`, `statusTransitions`, `testingPyramid` (uses the `layer` label),
  `testResultSeverities`, `durations`, `durationDynamics`, `stabilityDistribution`, `testBaseGrowthDynamics`,
  `statusAgePyramid`, `coverageDiff`, `successRateDistribution`, `problemsDistribution`. The `dashboard`
  plugin takes them as `layout`, `awesome` as `charts`.
- `environment.properties` is read, but awesome does not show it. The `classic` plugin is unfinished in 3.21
  ("Coming soon"); the `allure2` plugin is used instead. Its Environment widget is also empty in 3.21. Use
  `variables` in the config for overview facts.
- `allure.step` titles format **repr strings** of the args: `{customer.username}` fails. Use
  `with allure.step(f"...")` for attribute access. `**kwargs` can't be used in a title either.
- allure-python has no `allure.owner`. Use `allure.label("owner", ...)`.

## Commands

```bash
make install                  # uv sync + playwright chromium + npm ci
make test ARGS="-n 4"         # default suite (all but demo_failures) + report + quality gate
make test-open ARGS="tests/api/test_availability.py"   # run, then open the report even if tests fail
make api | web | e2e | smoke  # by marker (web includes e2e)
make demo                     # red demo tests only;  make all = everything in one report
make test ARGS="-k cart --headed"   # any pytest args
make report && make open      # rebuild report from allure-results / serve it
make lint                     # ruff + mypy
make clean [FULL=1]           # empty results/report/test-results; FULL=1 removes the folders (.allure kept)
make run-summary              # allure-results -> docs/run-summary.md (script options: see below)
uv run pytest -m api          # plain pytest; results go to allure-results/ (cleaned every run)
ALLURE_TESTPLAN_PATH=allure-report/testplan/testplan.json uv run pytest -m ""   # rerun last failures
```

## Run summary

- After a run, when the user asks to analyze it, run `make run-summary` (or `uv run python scripts/make_run_summary.py
  [--command "..."] [--scope "..."] [--env "..."]`) from the project root and read `docs/run-summary.md`. Don't read raw `allure-results/` instead.
- The script reads only `allure-results/*-result.json`. It overwrites the whole file every time, so the file
  always describes only the last run. `--clean-alluredir` already empties the results dir before each pytest
  run. If the header has a "mixed runs" warning, say so before drawing conclusions.
- Retries are merged by `historyId` (the last attempt wins). With `--tb=line` the JSON has no `file:line` for
  failures, so the location column only shows up when some result has it.
- Exit code 2 means no results. It is not hooked into pytest or make; run it only on request.

## Code conventions

- Full type hints. `ruff check`, `ruff format`, `mypy` (strict) must pass. Line length is 110.
- Names: `test_<what>_<expected_result>`. Pages are `<Name>Page`, components `<Name>Component`, clients
  `<Domain>Client`, factories `<Entity>Factory`.
- Comment only a non-obvious *why*.
- Tests use AAA, one behavior per test, DAMP over DRY. Assertions live in tests, never in Page Objects or
  clients.
- Positive tests assert 2xx, negative ones 4xx. Exception: wc-ajax returns 200 with `{"error": true}`
  (documented in the test).
- Locators: role → label/placeholder → test-id → CSS (CSS only where WooCommerce markup has no role, like
  `tr.cart_item`, `.woocommerce-error`). Scope locators to `#content` so they don't hit the header/footer.
- Clients return `httpx.Response`. Tests parse it with `parse_response(response, Model | list[Model])`.

## Allure rules (every test)

- `epic` / `feature` / `story`, `title` (with `{param}` placeholders when parametrized), `severity`,
  `label("owner", ...)`, `suite`. Put shared ones in module `pytestmark` or on the class.
- `layer` and `parent_suite` are set automatically from the `api` / `web` / `e2e` markers
  (`_allure_layer_labels` in `tests/conftest.py`). Every test needs exactly one layer marker, except
  demo tests, which set `allure.label("layer", ...)` by hand on purpose.
- Use `allure.testcase("ID")` / `allure.issue("ID")`. URL patterns come from `--allure-link-pattern` in
  pyproject.
- Steps: public client/page methods have `@allure.step`. Use `with allure.step()` for multi-action blocks
  in tests.
- Attachments are automatic: API via `BaseApiClient`, web artifacts in the `context` fixture (on failure,
  always for `e2e`, or when `INTERSHOP_WEB_ARTIFACTS=always`). Don't attach them by hand in tests.
- A dynamic value that changes per run (order number) → `allure.dynamic.parameter(..., excluded=True)`, so
  history ids stay stable.
- Retries: `@pytest.mark.flaky(reruns=N)` only with a comment on why. There are no global `--reruns`.
- skip/skipif/xfail always have `reason=`. xfail is strict (`xfail_strict = true`).

## Test data

- Generated data only from `CustomerFactory` / `BillingAddressFactory`. `INTERSHOP_DATA_SEED` makes it
  reproducible.
- Stable site data only in `src/intershop/data/catalog.py`.
- Isolation: a fresh httpx client (= own session and cart) and a fresh browser context per test.
  `registered_customer` creates a new account per test. The site has no way to delete accounts or orders,
  so they stay on the stand.

## Don't

- `time.sleep` / `wait_for_timeout` in tests or pages. Use Playwright auto-waits and `expect`
  (timeout from settings).
- Hardcoded URLs, credentials, or generated data in tests. No dependency between tests.
- Secrets in the repo (`.env` is gitignored, `.env.example` documents vars).
- Made-up endpoints or Allure options. Verify with a request or `npx allure ... --help` and record them
  above.
- **Git:** don't init, stage, or commit. The user does all git work. Only suggest a commit message when
  asked.
