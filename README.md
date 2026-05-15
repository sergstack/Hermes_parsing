# Herm Finance monthly exporter

## Project scope

This repository currently implements a Herm Finance Excel exporter.

Current responsibility:

- authenticate to Herm Finance with Playwright;
- open configured report UI/API endpoints;
- export Excel files;
- save outputs under `exports/`;
- write run logs under `logs/`.

Not current responsibility:

- stage/mart/report transformation;
- financial reconciliation;
- dashboarding;
- database loading.

Current data flow:

```text
config/config.txt
-> login/session
-> report definitions
-> Playwright UI/API download
-> exports/
-> logs/
```

## Runtime folders and sensitive files

| Path | Purpose | Git / safety note |
|---|---|---|
| `exports/` | Generated Excel exports | Runtime output; do not commit |
| `logs/` | Run logs and debug logs | Runtime output |
| `output/` | Debug/output artifacts such as screenshots | Runtime output |
| `state/` | Browser/session runtime state | Runtime state |
| `state/herm_session.json` | Browser session storage | Sensitive; do not open, print, share, or commit |
| `config/config.txt` | Local runtime configuration | Sensitive/local; do not print, share, or commit |

## Safe operating rules

- Run a full export only intentionally; it can touch Herm Finance, session state, logs, and `exports/`.
- Check `overwrite` in `config/config.txt` before reruns.
- Do not open, print, or share session/config contents.
- Treat `exports/` as raw source material for downstream analytics, not as Mart output.
- If downstream Mart or analytics work is needed, create a separate SPEC before implementation.

## Future Mart / analytics layer

Planning artifacts may describe a future analytics layer, but that layer is not currently implemented unless matching `src/pipeline/...` and `data/...` folders exist.

The current exporter remains separate from any future stage/mart/report pipeline. Mart implementation, financial reconciliation, report generation, or dashboarding requires a separate scoped task.

## Installation

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install
```

## Configuration

`config/config.txt` — основной конфигурационный файл:

| Параметр | Описание | Пример |
|---|---|---|
| `start_date` | Начало периода выгрузки | `2025-01-01` |
| `base_url` | URL сайта | `https://herm.finance` |
| `download_dir` | Папка для файлов | `./exports` |
| `session_file` | Файл сессии браузера | `./state/herm_session.json` |
| `headless` | Скрытый браузер | `false` |
| `overwrite` | Перезаписывать существующие файлы | `false` |
| `timeout_ms` | Таймаут операций (мс) | `60000` |
| `slow_mo` | Замедление Playwright (мс) | `0` |

Относительные пути в `config/config.txt` разрешаются от корня репозитория, а не от текущей папки запуска. Абсолютные пути остаются абсолютными.

**Конечная дата** вычисляется автоматически: текущий месяц − 1.  
При `overwrite=false` скрипт проверяет наличие файлов и скачивает только пропуски.

## Run

```bash
python -m app.main
```

На macOS можно запускать готовый wrapper:

```bash
./run_hermes.command
```

## First login

При первом запуске или если сохранённая сессия устарела — откроется видимый браузер. Войдите вручную на `https://herm.finance`, затем вернитесь в терминал и нажмите Enter. Сессия сохраняется в `session_file`.

## Output

Файлы сохраняются в `./exports/<папка_отчёта>/<префикс>_YYYY-MM.xlsx`.

Исключения:

- `contractors` сохраняется один раз: `./exports/contractors/contractors.xlsx`.
- `account_balances` сохраняется по дате конца месяца: `./exports/account_balances/acc_balance_YYYY-MM-DD.xlsx`.
- `cons_budget` сохраняется один раз: `./exports/cons_budget/cons_budget.xlsx`.

## Successful path

Проверенный успешный запуск:

```bash
.venv/bin/python -m pytest tests/test_downloaders.py tests/test_urls.py tests/test_paths.py
./run_hermes.command
```

Ожидаемый итог полного запуска: `summary | success=90 | error=0 | failed=none`.

Проверенный набор выгрузок:

- `applications`: 2025-01 ... 2026-04.
- `dds_expenses`: 2025-01 ... 2026-04.
- `dds`: 2025-01 ... 2026-04.
- `budget_rows`: 2025-01 ... 2026-12.
- `cons_budget`: с 01.01 прошлого года до 31.12 текущего года.
- `contractors`: один файл справочника.
- `account_balances`: 2025-01 ... 2026-04.

## Move notes

- `.venv/` and `venv/` are disposable local environments; recreate the virtual environment after moving the repository.
- `config/config.txt`, `state/`, `exports/`, and `logs/` are runtime state. Decide explicitly whether to migrate them before moving.
- `.claude/worktrees` contains linked worktree state and must be handled separately before moving.
- Target-specific validation remains pending until the target path is known.

## Supported reports

| Код | Папка | Префикс файла | Метод выгрузки |
|---|---|---|---|
| `applications` | `demands` | `demands` | UI: кнопка «Скачать» → popover с именем файла → история выгрузок |
| `dds_expenses` | `p-fact` | `p-fact` | UI: «Показать» → «Экспортировать всё» |
| `dds` | `dds` | `dds` | UI: фильтр «Дата начисления» → кнопка поиска → «Скачать .xlsx» |
| `budget_rows` | `budget_rows` | `raw` | UI: «Скачать .xlsx» → popover с именем файла → история выгрузок |
| `cons_budget` | `cons_budget` | `cons_budget` | UI: фильтры → «Показать» → «Экспортировать всё» |
| `contractors` | `contractors` | `contractors` | API: POST `/api/resources/contractor/export` → polling (один раз) |
| `account_balances` | `account_balances` | `acc_balance` | UI: «Показать» → «Экспортировать всё» |

## Фильтры отчёта p-fact (dds_expenses)

| Параметр | Значение |
|---|---|
| Вид отчёта | за период (`by_month`) |
| Статусы | Отправлено, Проверено, На согласовании, Бюджет принят, Возвращено |
| Уровень | 3 |
| Отчётная валюта | EUR |
| ВГО / Учредители / Биллинги / Фин. агенты / Резервы | исключить |

> Дропдаун «Резервы» не подхватывает URL-параметр `excludeReserve=1` автоматически —
> скрипт программно кликает опцию «исключить» после загрузки страницы.

## Методы выгрузки

### Используемые UI-элементы

| Назначение | Название в UI | Селектор / метод |
|---|---|---|
| Показать отчёт | `Показать` | `button:has-text('Показать')`; fallback: `button.el-button--primary.el-button--small` |
| Экспортировать весь грид | `Экспортировать всё` | `page.get_by_role("button", name="Экспортировать всё")`; fallback: `div.dx-datagrid-export-button[aria-label='Экспортировать всё']`, `.dx-datagrid-export-button`, `[title='Экспортировать всё']` |
| Скачать / открыть popover имени файла | `Скачать` / `Скачать .xlsx` | `button:has-text('Скачать')`, `a:has-text('Скачать')` |
| Поле имени файла в popover | `Имя файла можно изменить` | `.el-popover.export-popper-class` + `input.el-input__inner` |
| Подтвердить имя файла | `Загрузить` | `button.el-button:has-text('Загрузить')` |
| История выгрузок | иконка в шапке | `button.files-button` |
| Скачать файл из истории | кнопка скачивания в строке | `td:not(.dx-hidden-cell) button.download-button` |
| Фильтр «Резервы» | `Резервы` | 9-й `.el-select`, то есть `.el-select.nth(8)`, затем `.el-select-dropdown__item` с текстом `исключить` |

### UI-метод с popover (`applications`)

Применяется для отчёта «Заявки».

1. Открыть страницу с фильтром по дате создания.
2. Нажать кнопку поиска — дождаться загрузки грида (`.dx-loadpanel-content`).
3. Нажать кнопку «Скачать» — появляется popover с полем имени файла.
4. Ввести имя `demands_YYYY-MM` → нажать «Загрузить».
5. Выдержать паузу 5 секунд (формирование файла на сервере).
6. Нажать кнопку истории выгрузок (`files-button` в шапке).
7. В появившемся списке кликнуть первую кнопку скачивания (`download-button`).
8. Сохранить браузерный download через `download.save_as(...)`, затем перенести временный файл в `exports/demands/demands_YYYY-MM.xlsx`.

> **Важно:** DevExtreme рендерит каждую строку грида дважды — видимая копия находится
> в фиксированной колонке, а дубликат в прокручиваемой области скрыт классом
> `dx-hidden-cell`. Для поиска кнопки используется селектор
> `td:not(.dx-hidden-cell) button.download-button`.

### UI-метод прямого скачивания (`dds_expenses` / p-fact)

Применяется для отчёта «План-Факт по ДДС (траты)».

1. Открыть страницу с фильтрами периода.
2. Подождать 2 секунды, чтобы Vue применил URL-параметры к дропдаунам.
3. Программно выбрать «исключить» в дропдауне «Резервы» (индекс 8 среди `.el-select`).
4. Нажать «Показать» — ждать `networkidle`.
5. Нажать кнопку «Экспортировать всё» в самом гриде: основной метод `page.get_by_role("button", name="Экспортировать всё")`, fallback-селектор `.dx-datagrid-export-button`.
6. Принять прямое браузерное скачивание через `page.expect_download(...)`.
7. Сохранить файл через `download.save_as(...)` в `exports/p-fact/p-fact_YYYY-MM.xlsx`.

> Для `p-fact` не используется кнопка истории выгрузок `files-button` в верхней панели.
> Скачивание должно идти только через кнопку `Экспортировать всё` внутри грида отчёта.

### UI-метод через popover (`dds`)

Применяется для отчёта «Список ДДС» (`/bank_and_cashbox/operations`).

1. Открыть страницу с фильтрами периода.
2. Программно заполнить диапазон в поле «Дата начисления».
3. Нажать кнопку поиска у формы фильтров.
4. Нажать кнопку «Скачать .xlsx» — появляется popover с полем имени файла.
5. Ввести имя `dds_YYYY-MM` → нажать «Загрузить».
6. Выдержать паузу 5 секунд (формирование файла на сервере).
7. Нажать кнопку истории выгрузок (`files-button`) и скачать первый файл.
8. Сохранить браузерный download через `download.save_as(...)`, затем перенести временный файл в `exports/dds/dds_YYYY-MM.xlsx`.

> **Важно:** на странице `DDS` есть несколько кнопок с иконкой поиска. Первая search-кнопка
> относится к полю «Банковский счет» и открывает модальное окно «Банковские счета».
> Для запуска поиска нужно нажимать кнопку формы фильтров, а не `input-button search-button`.

### UI-метод (`cons_budget`)

Применяется для отчёта «План-факт по конс. бюджету (за период)».

1. Открыть страницу `/budgeting/reports/consolidated_plan_fact_monthly_report`.
2. Установить период с 01.01 прошлого года до 31.12 текущего года.
3. Применить фильтры: статусы `На согласовании +4`, уровень `3`, проект `Azp_admin`, ВГО `исключить`, отчётная валюта `EUR`.
4. Снять чекбоксы: «Отображать отклонения», «План|факт / IN-OUT(текущий)», «План|факт / IN-OUT(предыдущий)».
5. Нажать «Показать».
6. Нажать кнопку `Экспортировать всё` и принять прямое браузерное скачивание через `page.expect_download(...)`.
7. Сохранить файл через `download.save_as(...)` в `exports/cons_budget/cons_budget.xlsx`.

### API-метод (остальные отчёты)

1. Открыть нужную страницу отчёта (устанавливает cookies/контекст).
2. Зафиксировать текущий максимальный `id` в очереди экспортов.
3. POST на endpoint экспорта с именем файла `{prefix}_YYYY-MM.xlsx`.
4. Polling `/api/resources/export-file/all` — ждать строку со статусом `ready`
   и `id` выше зафиксированного.
5. POST `/api/export_files/download/{id}` — получить бинарный файл и сохранить.
6. Записать ответ в целевой файл через `Path.write_bytes(...)`.

> Некоторые отчёты возвращают `500` на шаге 3 — это ожидаемое поведение.
> Скрипт логирует предупреждение и переходит к polling, который всё равно
> обнаруживает готовую строку.

## Known behavior

- Некоторые отчёты возвращают `500` на trigger-endpoint — polling всё равно
  находит готовый файл в `/api/resources/export-file/all`.
- `contractors` скачивается один раз за весь прогон (не повторяется помесячно),
  т.к. справочник не зависит от периода.
