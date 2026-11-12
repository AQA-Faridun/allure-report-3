# Intershop: автотесты API + Web с отчётом Allure Report 3

Демонстрационный проект автотестов для учебного интернет-магазина https://intershop6.skillbox.ru/
(WordPress + WooCommerce). Главная цель — показать возможности **Allure Report 3** на «боевом» отчёте:
иерархия тестов, шаги, HTTP-вложения, Playwright trace и видео, история и тренды, категории, known issues,
quality gate, дашборды.

- **83 теста**: 44 API, 28 Web, 2 E2E и 9 демонстрационных «красных».
- **Стек:** Python 3.12 · pytest · httpx · Playwright · mimesis · pydantic · allure-pytest · Allure 3 (Node.js).

## Требования

| Что | Версия | Установка |
|---|---|---|
| Python | 3.12 | ставится через uv автоматически |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.9 | `brew install uv` или `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | ≥ 20 | `brew install node` |
| Chromium для Playwright | — | см. ниже |

## Установка

```bash
make install
# что эквивалентно:
uv sync                                   # Python-зависимости из uv.lock
uv run playwright install chromium        # браузер (в CI: --with-deps)
npm ci                                    # Allure 3 CLI из package-lock.json
cp .env.example .env                      # необязательно: у всех переменных есть значения по умолчанию
```

## Запуск

`make`-цели оборачивают `npx allure run -- uv run pytest ...`: тесты запускаются, отчёт собирается
и проверяется quality gate. Любые аргументы pytest передаются через `ARGS`.

| Команда | Что запускает |
|---|---|
| `make test` | весь основной набор (всё, кроме `demo_failures`) |
| `make test-open` | то же + сразу открыть отчёт в браузере (открывается и при упавших тестах) |
| `make test-open ARGS="tests/api/test_availability.py"` | один файл → отчёт → браузер |
| `make api` / `make web` / `make e2e` / `make smoke` | по маркерам (`web` включает e2e) |
| `make demo` | только демонстрационные падающие тесты |
| `make all` | основной набор и демо в одном отчёте |
| `make test ARGS="-n 4"` | параллельно в 4 воркера (pytest-xdist) |
| `make web ARGS="--headed"` | с видимым браузером (`--slowmo 300` для наглядности) |
| `make test ARGS="-k cart"` | по подстроке имени |
| `make test ARGS="-m 'api and smoke'"` | любое выражение маркеров |
| `make lint` | ruff + mypy |
| `make clean` | очистить содержимое `allure-results/`, `allure-report/`, `test-results/` (папки остаются) |
| `make clean FULL=1` | удалить эти папки целиком; история в `.allure/` не трогается в обоих случаях |

Без Allure CLI тесты запускаются обычным pytest, результаты всё равно пишутся в `allure-results/`:

```bash
uv run pytest                      # основной набор
uv run pytest -m regression -n auto
uv run pytest tests/web/test_cart.py::test_remove_product
```

Маркеры: `api`, `web`, `e2e`, `smoke`, `regression`, `demo_failures`. Включён `--strict-markers`.
`-m "not demo_failures"` стоит в `addopts`, а явный `-m` в командной строке его перекрывает.

## Отчёт Allure 3

```bash
make test           # тесты + отчёт в ./allure-report
make test-open      # тесты + отчёт + сразу открыть его в браузере
make open           # npx allure open ./allure-report — открыть в браузере
make report         # пересобрать отчёт из ./allure-results без запуска тестов
```

Отчёт собирается из `allurerc.mjs` (единый конфиг в репозитории). `allure-report/index.html` — сводная
страница со ссылками на отчёты плагинов:

| Плагин | Где | Что даёт |
|---|---|---|
| `awesome` | `allure-report/awesome/` | основной современный UI: дерево epic → feature → story, фильтры, поиск, шаги, вложения, история, ретраи, категории, resolutions, quality gate, графики |
| `dashboard` | `allure-report/dashboard/` | отдельный дашборд с графиками и трендами |
| `allure2` | `allure-report/allure2/` | привычный UI Allure 2: Suites, Behaviors, Graphs, Timeline |
| `csv` | `allure-report/csv/allure-results.csv` | плоская выгрузка результатов |
| `testplan` | `allure-report/testplan/testplan.json` | список упавших тестов для перезапуска |
| `log` | консоль | сводка по упавшим тестам сразу после прогона |

### История между запусками

`historyPath: "./.allure/history.jsonl"`. Каждая генерация отчёта дописывает в файл строку с итогами
прогона. Благодаря этому работают вкладка **History** у теста, графики *Status dynamics*,
*Status transitions*, *Duration dynamics*, *Test base growth*, а также пометки New, Fixed, Regressed
и детекция flaky. Папка `.allure/` не попадает в git. В CI она сохраняется в `actions/cache`.
Для чистого старта удалите `.allure/`.

### Перезапуск только упавших тестов

```bash
ALLURE_TESTPLAN_PATH=allure-report/testplan/testplan.json uv run pytest -m ""
```

## Возможности Allure → где показано

| Возможность | Где в проекте |
|---|---|
| epic / feature / story | все тесты; в отчёте дерево `groupBy: [epic, feature, story]` (`allurerc.mjs`) |
| parent_suite / suite / sub_suite | `parent_suite` (API / Web UI / End-to-end) ставится автоматически в `tests/conftest.py::_allure_layer_labels`; `suite` задан в `pytestmark` модулей; `sub_suite` берётся из имени класса (`TestProductList` и др.) |
| label `layer` → график *Testing pyramid* | `tests/conftest.py::_allure_layer_labels` по маркерам api / web / e2e |
| owner, tags | `allure.label("owner", ...)`, `@allure.tag(...)` во всех модулях; `defaultLabels` в конфиге |
| severity (все 5 уровней) | blocker `test_cart.py::test_add_product_to_cart`, critical `test_categories.py`, normal, minor `test_products.py::test_pagination_headers_are_consistent`, trivial `test_platform.py::test_rest_index_exposes_store_namespace` |
| title, динамический title с параметрами | `@allure.title("... {quantity} ...")` в параметризованных тестах |
| description (markdown) / description_html | `tests/e2e/test_order_flow.py`, `tests/api/test_cart.py::test_store_api_write_requires_nonce` / `tests/web/test_navigation.py::test_home_page_header` |
| шаги: декоратор, вложенные, с параметрами, контекстный менеджер | `@allure.step` на всех методах клиентов и Page Objects; клиент → HTTP-запрос (`BaseApiClient.request`) даёт вложенные шаги; `with allure.step(...)` в E2E |
| HTTP-вложение Allure 3 (`application/vnd.allure.http+json`) + curl | `src/intershop/utils/attachments.py::attach_http_exchange`, автоматически на каждый запрос |
| JSON / text / HTML вложения | `attach_json` / `attach_text` (curl, консоль браузера) / `attach_html` (HTML страницы при падении) |
| скриншот, Playwright trace (встроенный Trace Viewer), видео, HAR | фикстура `context` в `tests/fixtures/web.py`: при падении, для всех e2e или при `INTERSHOP_WEB_ARTIFACTS=always` |
| Mermaid-диаграмма | `tests/e2e/test_order_flow.py::test_customer_places_order` (схема сценария) |
| параметризация, исключённый из historyId параметр | `@pytest.mark.parametrize` повсюду; `allure.dynamic.parameter(..., excluded=True)` для номера заказа |
| link / issue / testcase | `@allure.link` в `test_cart.py`; `@allure.issue` в `test_platform.py` и демо; `@allure.testcase` (CAT-101, CART-201, ORD-401…); шаблоны URL заданы в `--allure-link-pattern` (pyproject) |
| статусы passed / failed / broken / skipped | `tests/demo/test_demo_statuses.py` (+ xfail в `test_platform.py`) |
| flaky и ретраи | `test_demo_flaky_passes_on_retry` (падает на 1-й попытке), `pytest.mark.flaky` на E2E; вкладка *Retries*, метрики *Retried tests* / *Changed on retry* |
| known issue / muted (resolutions) | `resolutions.rules` в `allurerc.mjs`: SEC-17 → issue, `ConnectError` → muted; тесты `test_demo_known_issue`, `test_demo_broken_in_setup` |
| категории дефектов | `categories.rules` в `allurerc.mjs` (known issues, сеть, UI-таймауты, product / test defects, flaky) |
| quality gate | `qualityGate.rules` в `allurerc.mjs`: `fail-fast` (maxFailures 10, fastFail) и `release` (maxFailures 0, minTestsCount, successRate 0.9, maxDuration 120 s); `make demo` его роняет |
| окружение | `variables` в конфиге (вкладка Variables); `environment.properties` (Python, ОС, браузер, base URL) пишет `pytest_sessionfinish` |
| история и тренды | `historyPath` + `historyLimit` + `flakyDetection` |
| графики | общий список `charts` в `allurerc.mjs` (awesome + dashboard) |
| global attachments | `allure run` сам прикладывает stdout прогона |
| авто-вложения через pytest-хуки | `pytest_runtest_makereport` в `tests/conftest.py` сохраняет отчёты фаз в `item.stash`, фикстура `context` по ним решает, что прикладывать |

## Демонстрационные «красные» тесты

`tests/demo/test_demo_statuses.py`, маркер `demo_failures`. В основной прогон они не попадают.
Запуск: `make demo` или `make all`.

| Тест | Итог в отчёте |
|---|---|
| `test_demo_failed_assertion` | **failed**: цена не совпала, есть ссылка на issue |
| `test_demo_broken_by_test_code` | **broken**: `KeyError` в коде теста |
| `test_demo_broken_in_setup` | **broken** в setup (сервис недоступен), помечен как **muted** |
| `test_demo_web_failure` | **failed** UI: скриншот, HTML, trace, видео, HAR |
| `test_demo_flaky_passes_on_retry` | **passed** со второй попытки, первая видна в *Retries* |
| `test_demo_strict_xpass` | **failed**: XPASS(strict), баг починили, а xfail остался |
| `test_demo_known_issue` | **failed**, но распознан как **known issue SEC-17** и не считается в quality gate |
| `test_demo_skipped`, `test_demo_skipped_by_platform` | **skipped** с причиной (skip / skipif) |

## Конфигурация

Переменные окружения (или `.env`, образец в `.env.example`):

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `INTERSHOP_BASE_URL` | `https://intershop6.skillbox.ru` | стенд |
| `INTERSHOP_STAND_NAME` | `intershop6 (public demo)` | имя стенда в environment |
| `INTERSHOP_API_TIMEOUT_S` | `20` | таймаут httpx |
| `INTERSHOP_UI_TIMEOUT_MS` | `15000` | таймаут Playwright и `expect` |
| `INTERSHOP_WEB_ARTIFACTS` | `on-failure` | `always`: прикладывать trace, видео и HAR ко всем web-тестам |
| `INTERSHOP_DATA_SEED` | пусто | фиксирует seed mimesis |

Браузер и режим задаются опциями pytest-playwright: `--browser firefox`, `--headed`, `--slowmo 300`.

## Структура

```
allurerc.mjs              конфиг Allure 3
Makefile                  команды запуска
src/intershop/
  config.py               настройки (pydantic-settings)
  api/                    base_client (шаги + HTTP-вложения), clients/ по доменам, schema (pydantic-валидация)
  models/                 pydantic-модели ответов
  pages/                  Page Objects + components/ (header, сетка товаров)
  data/                   фабрики mimesis, справочные данные каталога
  utils/                  вложения Allure, парсинг цен
tests/
  conftest.py             хуки, авто-лейблы, фикстуры клиентов и данных
  fixtures/web.py         Playwright: контекст с артефактами, логин через HTTP
  api/ web/ e2e/ demo/    тесты по слоям
.github/workflows/        CI
```

## CI (GitHub Actions)

`.github/workflows/tests.yml` устанавливает uv, Node, Chromium и запускает `allure run`. История
`.allure/` переживает прогоны через `actions/cache`. Отчёт выкладывается артефактом `allure-report`.
При ручном запуске (`workflow_dispatch`) можно передать выражение маркеров, например `demo_failures`.
Если упал quality gate, job красный, но отчёт всё равно загружается (`if: always()`).

## Известные ограничения

- **Публичный стенд.** Сайт общий и иногда отвечает медленно. На E2E стоит `flaky(reruns=1)`, глобальных
  ретраев нет. Тесты создают аккаунты и заказы: удалить их через сайт нельзя, а уникальные данные
  из mimesis не дают тестам зависеть друг от друга.
- **Store API корзины только на чтение.** Запись (`/wc/store/cart/add-item` и др.) требует
  `X-WC-Store-API-Nonce`, а сайт его гостям не отдаёт. Корзина меняется через `?wc-ajax=add_to_cart`
  и `remove_from_cart`, а отказ Store API без nonce проверяется отдельным тестом.
  `wc/v3` закрыт авторизацией (401), ключей нет.
- **Аккаунты.** REST API для регистрации и логина нет, работа идёт через HTML-формы с nonce.
  Сайт ограничивает поля регистрации 20 символами, включая email.
- **Allure 3.21:**
  - Плагин `classic` ещё не доделан (Graphs и Timeline помечены «Coming soon»), поэтому подключён `allure2`.
  - `environment.properties` читается, но не показывается ни в awesome, ни в виджете Environment
    плагина `allure2`, поэтому сводные данные выведены через `variables`.
  - Known issues настраиваются через `resolutions` (issue / muted / accepted). Документация на сайте
    ещё описывает старый `knownIssuesPath`.
- **pytest закреплён на 8.4.** С pytest 9 allure-pytest 2.16 добавляет в teardown каждой фикстуры
  мусорный шаг `<lambda>` со статусом unknown.
- В отчёте видны служебные setup-фикстуры pytest-playwright (`delete_output_dir` и др.). Так работает
  allure-pytest, скрыть их нельзя.
