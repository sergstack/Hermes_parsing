# Herm Finance monthly exporter

Python + Playwright exporter for Herm Finance reports. The project keeps report
definitions in code, writes downloaded files to local runtime folders, and
supports a dry-run mode for reviewer-friendly validation without opening a
browser or starting a live export.

## Quick reviewer setup

```bash
git clone https://github.com/sergstack/Hermes_parsing.git
cd Hermes_parsing

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

python -m pytest -q
```

## Installation

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install development dependencies if you plan to run tests or lint:

```bash
pip install -r requirements-dev.txt
```

4. Install Playwright browsers for live exports:

```bash
playwright install
```

## Configuration

Create a local config from the public example:

```bash
cp config/config.example.txt config/config.local.txt
```

`config/config.local.txt` or `config/config.txt` can be used as the local
runtime configuration file:

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
| `repeat_each_month` | Повторять непомесячные отчёты каждый месяц | `false` |

**Конечная дата** вычисляется автоматически: текущий месяц − 1.  
При `overwrite=false` скрипт проверяет наличие файлов и скачивает только пропуски.

Do not commit private runtime files:

- `config/config.txt`
- `config/config.local.txt`
- `state/`
- `exports/`
- `logs/`
- `.env` and `.env.*`

## Run

Dry-run without a browser or live Herm Finance export:

```bash
python -m app.main --config config/config.local.txt --dry-run --reports dds --headless true
```

Run the configured live export:

```bash
python -m app.main --config config/config.local.txt
```

Live export requires manual Herm Finance login and must not be run in CI. Do not
run a live export unless you intend to use the configured Herm Finance account.

### CLI options

- `--config config/config.txt` to use a different config file.
- `--reports applications,dds` to limit the run to selected report codes.
- `--dry-run` to plan exports without opening a browser.
- `--headless true|false` to override the config value.
- `--overwrite true|false` to override the config value.

Dry-run writes a machine-readable plan to `logs/summary.json`.

## Tests

```bash
python -m pytest -q
```

## First login

При первом запуске или если сохранённая сессия устарела — откроется видимый браузер. Войдите вручную на `https://herm.finance`, затем вернитесь в терминал и нажмите Enter. Сессия сохраняется в `session_file`.

## Output

Файлы сохраняются в `./exports/<папка_отчёта>/<префикс>_YYYY-MM.xlsx`.

Runtime output directories:

- `exports/` — downloaded report files.
- `logs/` — run logs and dry-run summary output.
- `state/` — browser session state.

Completed one-off task artifacts are archived under `docs/tasks/`.

## Supported reports

| Код | Папка | Префикс файла | Метод выгрузки |
|---|---|---|---|
| `applications` | `demands` | `demands` | UI: кнопка «Скачать» → popover с именем файла → история выгрузок |
| `dds_expenses` | `dds` | `dds` | UI: «Показать» → «Экспортировать всё» → история выгрузок |
| `p-fact` | `p-fact` | `p-fact` | UI: «Показать» → «Экспортировать всё» → история выгрузок |
| `dds` | `dds` | `dds` | UI: фильтр «Дата начисления» → кнопка поиска → «Скачать .xlsx» |
| `budget_rows` | `budget_rows` | `raw` | UI: «Скачать .xlsx» → popover с именем файла → история выгрузок |
| `contractors` | `contractors` | `contractors` | UI: кнопка «Скачать» → popover с именем файла → история выгрузок |
| `account_balances` | `account_balances` | `acc_balance` | UI: «Показать» → «Скачать» → перенос свежего `.xlsx` из `Downloads` |
| `cons_budget` | `cons_budget` | `cons_budget` | UI: полный год → «Показать» → «Экспортировать всё» → прямое скачивание |

## Фильтры отчёта account_balances

| Параметр | Значение |
|---|---|
| Дата | последняя дата месяца |
| Отчётная валюта | EUR |
| Нулевые остатки | исключить |
| Заблокированные | исключить |
| Закрытые счета | исключить |
| Счета-кошельки | исключить |
| Архивные счета | исключить |
| Мои счета | выключено |

## Фильтры отчёта p-fact

| Параметр | Значение |
|---|---|
| Вид отчёта | за период (`by_month`) |
| Статусы | Отправлено, Проверено, На согласовании, Бюджет принят, Возвращено |
| Уровень | 3 |
| Отчётная валюта | EUR |
| ВГО / Учредители / Биллинги / Фин. агенты / Резервы | исключить |

> Дропдаун «Резервы» не подхватывает URL-параметр `excludeReserve=2` автоматически —
> скрипт программно кликает опцию «исключить» после загрузки страницы.

## Фильтры отчёта cons_budget

| Параметр | Значение |
|---|---|
| Период | полный год из `dates_period[0]` и `dates_period[1]` |
| Статусы | все выбранные в URL |
| Уровень | 3 |
| ЦФО | пусто |
| Проекты | `Azp_admin` |
| ВГО | исключить |
| Отображать столбцы | `План-факт` |
| Отображать отклонение | выключено |
| План/факт / IN-OUT(текущий) | пусто |
| План/факт / IN-OUT(предыдущий) | пусто |
| Отчётная валюта | EUR |

## Методы выгрузки

### UI-метод с popover (`applications`)

Применяется для отчёта «Заявки».

1. Открыть страницу с фильтром по дате создания.
2. Нажать кнопку поиска — дождаться загрузки грида (`.dx-loadpanel-content`).
3. Нажать кнопку «Скачать» — появляется popover с полем имени файла.
4. Ввести имя `demands_YYYY-MM` → нажать «Загрузить».
5. Выдержать паузу 5 секунд (формирование файла на сервере).
6. Нажать кнопку истории выгрузок (`files-button` в шапке).
7. В появившемся списке кликнуть первую кнопку скачивания (`download-button`).

> **Важно:** DevExtreme рендерит каждую строку грида дважды — видимая копия находится
> в фиксированной колонке, а дубликат в прокручиваемой области скрыт классом
> `dx-hidden-cell`. Для поиска кнопки используется селектор
> `td:not(.dx-hidden-cell) button.download-button`.

### UI-метод через историю (`dds_expenses` / p-fact)

Применяется для отчёта «План-Факт по ДДС (траты)».

1. Открыть страницу с фильтрами периода.
2. Подождать 2 секунды, чтобы Vue применил URL-параметры к дропдаунам.
3. Программно выбрать «исключить» в дропдауне «Резервы» (индекс 8 среди `.el-select`).
4. Нажать «Показать» — ждать `networkidle`.
5. Нажать кнопку «Экспортировать всё» (`.dx-datagrid-export-button`).
6. Выдержать паузу 3 секунды (формирование файла на сервере).
7. Нажать кнопку истории выгрузок (`files-button`) и скачать первый файл.

### UI-метод через popover (`dds`)

Применяется для отчёта «Список ДДС» (`/bank_and_cashbox/operations`).

1. Открыть страницу с фильтрами периода.
2. Программно заполнить диапазон в поле «Дата начисления».
3. Нажать кнопку поиска у формы фильтров.
4. Нажать кнопку «Скачать .xlsx» — появляется popover с полем имени файла.
5. Ввести имя `dds_YYYY-MM` → нажать «Загрузить».
6. Выдержать паузу 5 секунд (формирование файла на сервере).
7. Нажать кнопку истории выгрузок (`files-button`) и скачать первый файл.

> **Важно:** на странице `DDS` есть несколько кнопок с иконкой поиска. Первая search-кнопка
> относится к полю «Банковский счет» и открывает модальное окно «Банковские счета».
> Для запуска поиска нужно нажимать кнопку формы фильтров, а не `input-button search-button`.

### Прямое скачивание (`account_balances`)

1. Открыть страницу отчёта с фильтрами периода.
2. Установить дату на последний день месяца и применить фильтры.
3. Нажать «Показать».
4. Нажать «Скачать» и дождаться появления свежего `.xlsx` в `~/Downloads`.
5. Переместить найденный файл в `./exports/account_balances/` и переименовать его в `acc_balance_YYYY-MM-DD.xlsx`.

### UI-метод с прямым скачиванием (`cons_budget`)

Применяется для отчёта «План-факт по конс. бюджету (за период)».

1. Открыть страницу отчёта с полным годовым периодом и фильтрами из URL.
2. Подождать 2 секунды, чтобы страница применила параметры.
3. Нажать «Показать» — ждать `networkidle`.
4. Нажать кнопку «Экспортировать всё».
5. Дождаться появления браузерной загрузки и сохранить файл напрямую.

### API-метод (остальные отчёты)

1. Открыть нужную страницу отчёта (устанавливает cookies/контекст).
2. Зафиксировать текущий максимальный `id` в очереди экспортов.
3. POST на endpoint экспорта с именем файла `{prefix}_YYYY-MM.xlsx`.
4. Polling `/api/resources/export-file/all` — ждать строку со статусом `ready`
   и `id` выше зафиксированного.
5. POST `/api/export_files/download/{id}` — получить бинарный файл и сохранить.

> Некоторые отчёты возвращают `500` на шаге 3 — это ожидаемое поведение.
> Скрипт логирует предупреждение и переходит к polling, который всё равно
> обнаруживает готовую строку.

## Known behavior

- Некоторые отчёты возвращают `500` на trigger-endpoint — polling всё равно
  находит готовый файл в `/api/resources/export-file/all`.
- `contractors` скачивается один раз за весь прогон (не повторяется помесячно),
  т.к. справочник не зависит от периода.
- `account_balances` скачивается через кнопку «Скачать» и сохраняется как
  `acc_balance_YYYY-MM-DD.xlsx`, где дата в имени файла соответствует
  последнему дню месяца.
- `cons_budget` скачивается через кнопку «Экспортировать всё» и сохраняется как
  `cons_budget.xlsx` в `exports/cons_budget/`.
- `logs/summary.json` is written after dry-run and after a normal run.
