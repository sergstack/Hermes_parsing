# Continue Safe Offline Refactor Prompt

```markdown
Продолжай автономно по обновлённому `REFACTOR_PLAN.md` и доведи safe offline refactor до конца.

`REFACTOR_PLAN.md` — это roadmap и task contract, а не финальный результат.  
Не создавай новый план вместо выполнения.  
Не останавливайся после анализа.  
Не останавливайся после одного batch-а.  
Не возвращай только recommendations, checklist или next steps.

## Mission

Выполни все безопасные offline refactor batches из обновлённого `REFACTOR_PLAN.md`.

Продолжай работать, пока не будет достигнуто одно из двух состояний:

A. Все безопасные offline-batch-и из `REFACTOR_PLAN.md` выполнены, протестированы и задокументированы.

ИЛИ

B. Все оставшиеся batch-и явно заблокированы конкретной причиной: safety restriction, missing permission, missing dependency, failing validation that cannot be fixed safely, или необходимость доступа к live/sensitive resources.

Если safe work остаётся — не возвращай final report, продолжай выполнять.

## Execution Loop

Повторяй цикл до достижения Definition of Done:

1. Прочитай обновлённый `REFACTOR_PLAN.md`.
2. Найди следующий невыполненный safe batch.
3. Проверь, что batch не нарушает safety rules.
4. Перед изменением кода добавь или обнови characterization tests для поведения, которое будет затронуто.
5. Выполни behavior-preserving refactor.
6. Запусти validation.
7. Проверь protected paths.
8. Если validation failed — исправь batch или откати его.
9. Если validation passed — отметь batch как completed в `REFACTOR_PLAN.md` или progress section.
10. Перейди к следующему safe batch.

Не спрашивай подтверждения между safe batch-ами.

## Hard Safety Rules

Не открывай:

- `state/herm_session.json`
- `config/config.txt`
- любые файлы с tokens, cookies, credentials, session/auth state или personal sensitive data.

Не запускай:

- live exporter;
- production exporter;
- команды, которые контактируют с live systems;
- команды, которым нужны credentials/session;
- команды, которые пишут в runtime/generated paths.

Не изменяй:

- `exports`
- `logs`
- `output`
- `state`
- `config/config.txt`

Не делай:

- изменение output schemas;
- изменение live/exporter behavior;
- изменение credentials/session handling;
- broad formatting-only diffs;
- unrelated refactor;
- новые dependencies без явной необходимости;
- large risky restructuring without tests.

## Allowed Work

Разрешено:

- добавлять и улучшать characterization tests;
- выделять pure helper functions;
- уменьшать дублирование;
- изолировать path/config/output boundary logic без чтения sensitive files;
- улучшать внутренние имена;
- добавлять type hints, если поведение не меняется;
- делать маленькие behavior-preserving refactor batches;
- обновлять `REFACTOR_PLAN.md` только как progress tracker после реального выполненного batch-а.

## Required Validation

В начале выполни:

```bash
git status --short
git diff --name-only
.venv/bin/python -m pytest --collect-only -q
git status --short exports logs output state config/config.txt
```

После каждого batch-а выполни:

```bash
.venv/bin/python -m pytest -q
git status --short exports logs output state config/config.txt
```

Если full pytest unsafe или blocked, запусти самый широкий безопасный subset и объясни, почему full pytest не был запущен.

В конце выполни:

```bash
git diff --name-only
git status --short
.venv/bin/python -m pytest --collect-only -q
git status --short exports logs output state config/config.txt
```

## Definition of Done

Ты завершил задачу только если достигнуто A или B.

A: все безопасные offline-batch-и из обновлённого `REFACTOR_PLAN.md` выполнены, протестированы и задокументированы.

B: все оставшиеся batch-и заблокированы, и для каждого указан конкретный blocker.

Ты НЕ завершил задачу, если:

* только прочитал или обновил `REFACTOR_PLAN.md`;
* только добавил next steps;
* сделал один batch, но есть ещё безопасные batch-и;
* не добавил/обновил tests для затронутого поведения;
* не запустил validation;
* не проверил protected paths;
* final report содержит “Next safe step: continue refactor / add tests / run next batch” без named blocker.

## Acceptance Criteria

Работа принимается только если:

1. Обновлённый `REFACTOR_PLAN.md` прочитан и использован как roadmap.
2. Все safe batches из `REFACTOR_PLAN.md` либо completed, либо blocked с конкретной причиной.
3. Для каждого выполненного refactor batch-а добавлены или обновлены characterization tests, если batch затрагивает поведение.
4. Выполнен behavior-preserving refactor, если есть хотя бы один safe source-change batch.
5. Validation выполнена после каждого batch-а.
6. Failed validation исправлена или batch откачен.
7. Protected paths не изменились.
8. Live exporter не запускался.
9. `state/herm_session.json` не открывался и не изменялся.
10. `config/config.txt` не открывался и не изменялся.
11. Final report явно доказывает, что достигнуто состояние A или B.

## Final Self-Check Before Reporting

Перед тем как вернуть final report, проверь:

* Остался ли в `REFACTOR_PLAN.md` хотя бы один safe batch, который можно выполнить сейчас?
* Есть ли в final report “next step: add tests / continue refactor / run next batch”?

Если да — final report запрещён. Продолжай выполнять.

Final report разрешён только если нет remaining executable safe batch-ей.

## Forbidden Output

Не возвращай только:

* план;
* checklist;
* recommendations;
* “next safe step”;
* “нужно добавить тесты”;
* “создан/обновлён REFACTOR_PLAN.md”;
* один batch без доказательства, что остальные batch-и completed или blocked.

## Final Report Format

# Final Implementation Report

## Definition of Done Reached

A: all safe offline batches completed / B: blocked

Explain why.

## Batches Completed

| Batch | Files Changed | Tests Added/Updated | Validation |
| ----- | ------------- | ------------------- | ---------- |

## Batches Blocked

| Batch | Blocker | Evidence |
| ----- | ------- | -------- |

## Files Changed

* ...

## Tests Added or Updated

* ...

## Commands Run

| Command | Result |
| ------- | ------ |

## Validation Results

* Initial validation:
* Per-batch validation:
* Final validation:
* Protected paths status:

## Safety Confirmation

* Live exporter run:
* `state/herm_session.json` opened:
* `config/config.txt` opened:
* Runtime/generated files changed:

## Acceptance Criteria Check

* [x] ...
* [ ] ...

## Residual Risks

* ...

## Next Safe Step

Only allowed if it is blocked or intentionally deferred with explicit reason.
```

Главная фраза, которая не даёт ему остановиться раньше:

```text
Если safe work остаётся — не возвращай final report, продолжай выполнять.
```
