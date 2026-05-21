# Справочник скриптов Loginom Assistant

Подробное описание каждого Python-скрипта в `scripts/`.  
Скрипты `build_lof_*`, `patch_lof_*`, `lof_*` — **референс-реализация** пайплайна LOF на табличных данных ЭКГ.

**Пути:** [`paths.py`](paths.py) + [PROJECT_LAYOUT.md](../PROJECT_LAYOUT.md). Эталон Unit_1: `packages/lof/LOF_reference.lgp`. В git не коммитится `scripts/_work/`.

---

## Содержание

1. [Ядро](#1-ядро)
2. [Карта узлов и XML-билдеры](#2-карта-узлов-и-xml-билдеры)
3. [Данные и split](#3-данные-и-split)
4. [Сборка пакета LOF (Unit_0)](#4-сборка-пакета-lof-unit_0)
5. [Сборка и правка LOF (Unit_1)](#5-сборка-и-правка-lof-unit_1)
6. [Оформление схемы](#6-оформление-схемы)
7. [Offline-метрики LOF](#7-offline-метрики-lof)
8. [Сборки других задач](#8-сборки-других-задач)
9. [Отладочные скрипты](#9-отладочные-скрипты)
10. [Адаптация скриптов](#10-адаптация-скриптов)

---

## 1. Ядро

### `loginom_pack.py`

**Назначение:** единая точка работы с контейнером `.lgp` (ZIP + XML).

| Команда | Действие |
|---------|----------|
| `unpack <file.lgp> <dir>` | распаковать в папку |
| `pack <dir> <file.lgp>` | собрать ZIP; перед записью парсит все `*.xml` |
| `verify <file.lgp>` | проверить наличие `PackageInfo.xml`, парсинг `Unit.xml` |

**Поведение pack:**
- автоматический backup → `*.lgp.bak`;
- `ZIP_DEFLATED`;
- при невалидном XML — `SystemExit` с путём к файлу.

**Когда использовать:** любая правка `Unit.xml` агентом или вручную.

**Выход:** распакованная структура `PackageInfo.xml`, `References.xml`, `Unit_N/Unit.xml`, …

---

### `loginom_lgd.py`

**Назначение:** проверить, что файл — контейнер Loginom `BGDATA`, а не ZIP.

**Использование:**
```bash
python loginom_lgd.py path/to/data.lgd
```

**Вывод:** первые байты, размер, предупреждение если похоже на ZIP.

**Связь:** [lgd-format.md](../lgd-format.md) — `.lgd` не распаковывается переименованием в `.zip`.

---

## 2. Карта узлов и XML-билдеры

### `extract_node_maps.py`

**Назначение:** построить JSON-каталог узлов из набора эталонных `.lgp`.

**Выход:** `scripts/_node_maps.json`:
```json
{
  "ETL": { "version": "7.3.1", "units": [{ "unit": "Unit_0/Unit.xml", "nodes": [
    { "display": "Импорт", "engine": "TBGImportTextFile" }
  ]}]}
}
```

**Настройка:** в `main()` список `files = { "ETL": Path(...), "LOF": Path(...), ... }` — пути к **вашим** эталонам.

**Когда использовать:** перед правкой XML — узнать типичный `Engine` и `DisplayName` для задачи.

---

### `lof_native_nodes.py`

**Назначение:** библиотека генерации XML-фрагментов для **нативной** цепочки подготовки данных (не kits).

**Экспортируемые функции:**

| Функция | Узел Loginom |
|---------|--------------|
| `partition_node_xml()` | Разбиение на множества (70/30, 50/50, seed, stratify) |
| `calc_sample_xml()` | Калькулятор `SAMPLE = train|valid|test` |
| `calc_istest_from_sample_xml()` | `IsTestSet = SAMPLE <> "train"` |
| `union_node_xml()` | Объединение с сопоставлением колонок |
| `replace_union_links()` | Исправить Items в Union (без дублей OBJECT/IsTestSet) |
| `link_xml()` | Связь SourcePort → TargetPort |
| `export_txt_node_xml()` | Экспорт TSV |
| `public_passthrough_xml()` | Публичный узел датасета |

**VendorGuid (стабильные в Loginom 7.3):**
- Калькулятор `c7b69712-…`
- Фильтр `a0e49d86-…`
- Разбиение `b2161dca-…`
- Объединение `f5aa91d2-…`

**Импортируется из:** `build_lof_project.py`, `patch_lof_fix_unions.py`.

---

## 3. Данные и split

### `export_lof_dataset.py`

**Назначение:** собрать TSV в формате выгрузки Loginom (tab, decimal `,`).

**Вход:**
- `ecg_train.txt`, `ecg_test.txt` (без CLASS=2);
- `sample_by_object.tsv` — метки SAMPLE по OBJECT.

**Выход:** `export_out.txt` (по умолчанию), колонки:
`CLASS, SAMPLE, IsTestSet, OBJECT, VAR2…VAR141`.

**CLI:**
```bash
python export_lof_dataset.py -o path/out.txt --reference path/ref.txt
```

**Зависимость:** `sample_by_object.tsv` должен существовать (из эталонного export или `match_lof_split.py`).

---

### `compare_lof_export.py`

**Назначение:** построчное сравнение двух export TSV.

**Проверяет:**
- число строк;
- `CLASS`, `SAMPLE`, `IsTestSet`, `OBJECT` — точное совпадение;
- `VAR2…VAR141` — с допуском `atol=1e-9`.

**Возврат:** exit 0 / 1; печатает число расхождений по колонкам.

**Когда использовать:** после изменения split или объединений в Unit_0.

---

### `probe_lof_partition.py`

**Назначение:** диагностика разбиения train/valid/test.

**Выводит:**
- доли SAMPLE;
- распределение CLASS по выборкам;
- долю совпадения с `sample_by_object.tsv` для разных логик split (последовательный vs случайный 70% норм).

**Когда использовать:** метрики LOF «плавают», подозрение на неверный split.

---

### `match_lof_split.py`

**Назначение:** перебор вариантов split в Python и поиск максимального совпадения с эталонным `sample_by_object.tsv`.

**Логика по умолчанию (methodology):**
1. 70% нормальных (CLASS=1) → train, seed=42;
2. остаток нормальных + аномалии → stratified 50/50 → valid/test.

**Выход:** accuracy по OBJECT, рекомендация random vs sequential для 70%.

---

## 4. Сборка пакета LOF (Unit_0)

### `build_lof_project.py`

**Назначение:** полная пересборка пакета LOF из шаблона `LOF_template.lgp`.

**Создаёт Unit_0:**
1. Импорт train/test TXT;
2. Объединение;
3. OBJECT;
4. Фильтр CLASS=1 на ветке 70%;
5. Разбиение 70/30, seed=42, sequential;
6. Объединение остаток + аномалии;
7. Разбиение 50/50, stratified, seed=42;
8. SAMPLE train/valid/test;
9. IsTestSet;
10. Публичный узел + экспорт TSV.

**Ожидаемые объёмы:** 3233 / 2043 / 595 / 595.

**Особенности:**
- не копирует `Unit.bin` из шаблона (`DROP_UNIT_BIN`);
- обновляет `References.xml` на python_kits;
- фиксированные GUID для ключевых узлов Unit_0.

**Выход:** `packages/lof/lof_package.lgp` (`LOF_PACKAGE_LGP`).

**Запуск:**
```bash
python build_lof_project.py
```

---

### `patch_lof_fix_unions.py`

**Назначение:** точечный патч уже сохранённого `.lgp` — связи Union, разбиение 50/50, публичный узел.

**Когда:** после ручных правок в Loginom, когда сломались сопоставления колонок в Объединении.

---

### `patch_lof_user_lgp.py`

**Назначение:** исправить порядок веток Python/импорта (train перед test) в сохранённом пакете.

---

## 5. Сборка и правка LOF (Unit_1)

### `merge_lof_unit1_from_template.py`

**Назначение:** вставить Unit_1 из эталонного пакета (цепочка sklearn kits) в пользовательский `.lgp`.

**Действия:**
- копирует `Unit_1/Unit.xml` из эталона;
- перепривязывает ссылку на публичный датасет (GUID пользователя);
- сохраняет `References.xml` пользователя (пути к libs).

**Вход:** `LOF_REFERENCE_LGP`, `LOF_PACKAGE_LGP` из `paths.py`.

---

### `rebuild_lof_unit1.py`

**Назначение:** оркестратор — merge + `fix_lof_unit1_metrics` + `patch_lof_unit1_wiring`.

**Создаёт каталоги моделей:** `C:\model\k15_c05`, `k20_c05`, …

**Запуск одной командой** после изменения Unit_0 или эталона.

---

### `fix_lof_unit1_metrics.py`

**Назначение:** исправить цепочку метрик в Unit_1.

| Правка | Смысл |
|--------|--------|
| CLASS replace | 1→0 (норма), 2,3,4,5→1 (аномалия) |
| outlier_label | 1→0, -1→1 |
| classification metrics | `beta=2` |
| model filepath | `C:\model\k15_c05` |
| Убрать дублирующую замену CLASS | после бинаризации |

**GUID узлов:** `NODE_CLASS_BINARY`, `NODE_OUTLIER` — константы в файле (при смене пакета — обновить grep по DisplayName в Unit.xml).

**Побочный эффект:** `fix_broken_items_wrappers` — баланс вложенных `<Items>`.

---

### `patch_lof_unit1_wiring.py`

**Назначение:** подключить valid/test к **скоринговому** порту `model.fitter`.

**Ключевые GUID:**
- `PORT_SCORE` = `dd84ef4f-…` (тестовая/скоринговая выборка);
- `IS_VALID`, `IS_TEST` — фильтры SAMPLE;
- `FITTER_VALID`, `FITTER_TEST` — узлы model.fitter на ветках.

**Удаляет** старые неверные связи из `REMOVE_LINKS`.

**Симптом без патча:** recall≈0 или metrics на полном датасете.

---

### `fix_lof_model_path.py`

**Назначение:** только замена `filepath` / `params` в переменных LOF и model.fitter.

**Когда:** смена k/c без полного rebuild.

---

### `build_lof_unit1_python_metrics.py`

**Назначение:** альтернативный Unit_1 — метрики через `TBGPythonEngine` (sklearn LOF в коде), без цепочки kits.

**Плюсы:** предсказуемые метрики, проще отладка.  
**Минусы:** не демонстрирует нативные компоненты Loginom kits.

**Встроенная логика:** тот же split, StandardScaler, LOF novelty, grid k×c, classification_report.

---

## 6. Оформление схемы

### `number_workflow_blocks.py`

**Назначение:** пронумеровать **все** узлы на каждом листе (Unit).

**Охват:**
- `WorkFlow/Nodes` — рабочие узлы;
- `ModelViews/Nodes` — таблицы, статистика на схеме.

**Порядок:** сверху вниз, слева направо по `Position Left/Top`.

**Не трогает:** `Links` (там нет DisplayName для нумерации).

**Выход:**
- обновлённый `.lgp`;
- отчёт `check_methodology_numbering.txt` (список узлов по листам).

**Параметры:** `DROP_UNIT_BIN` — не упаковывать устаревшие `.bin`.

---

### `differentiate_unit1_layout.py`

**Назначение:** визуальное отличие схемы **без смены логики**.

**Разрешено:** `RENAME` dict Guid→DisplayName, `POSITION` Guid→(Left, Top).  
**Запрещено (в текущей версии):** вставка/удаление узлов, regex `.*?` по XML.

**Исторически:** старая версия с `remove_node()` ломала пакет — не использовать.

---

## 7. Offline-метрики LOF

### `validate_lof_metrics.py`

**Назначение:** эталон sklearn для сравнения с Loginom.

**Алгоритм:**
1. `prepare()` — split 70/15/15, seed=42, без CLASS=2;
2. для каждой пары (k,c) из сетки: fit LOF на train (только норма), predict valid;
3. Fbeta (β=2), F1;
4. лучшая модель → predict test, `classification_report`.

**Константы:** `LOF_DATA`, `FEATURES = VAR2…VAR141`.

**Вывод в консоль:** таблица Fbeta на valid, best k/c, test metrics.

**Когда:** проверка «цифры Loginom сходятся с sklearn на том же export».

---

### `analyze_lof_metrics.py`

**Назначение:** сравнить метрики Loginom (из скриншота/заметок) с sklearn на `Выход-скрипта.txt` или `export_reference.txt`.

**Печатает:** fn, recall, precision на valid/test для k=15,c=0.05.

**Подсказка:** если в Loginom таблица на 2638 строк — не применён фильтр SAMPLE.

---

### `_analyze_user_lof.py`

**Назначение:** разовый скрипт — grid метрик по одному export-файлу. Шаблон для копирования.

---

## 8. Сборки других задач

### `build_regression_project.py`

**Назначение:** собрать пакет регрессии из эталона — только нужные Unit и пути к xlsx.

**Паттерн:** unpack template → filter units → rewrite `FileName` → pack.

---

### `build_scoring_project.py`

**Назначение:** пакет скоринга OTP — пути к `otp_train.lgd`, `otp_test.lgd`, локальные kits.

---

### `map_package_units.py`

**Назначение:** вывести список Unit и DisplayName узлов из пакета регрессии → JSON для навигации.

---

## 9. Отладочные скрипты

| Файл | Действие |
|------|----------|
| `inspect_lgp_pair.py` | сравнить структуру двух .lgp (число узлов, имена) |
| `inspect_lgp_pair.py` | сравнить узлы reference vs user .lgp |
| `_work/find_lof.py` | grep по Unit.xml: neighbors, LOF, fitter |

Папка `_work/` — артефакты распаковки; в `.gitignore` репозитория пользователя.

---

## 10. Адаптация скриптов

### Минимальный набор для нового LOF-проекта

| Задача | Скрипт |
|--------|--------|
| Правка пакета | `loginom_pack.py` |
| Проверка split | `probe_lof_partition.py` |
| Offline метрики | скопировать `validate_lof_metrics.py` → поменять `prepare()` и пути |
| Нумерация схемы | скопировать `number_workflow_blocks.py` → `LGP`, `REPORT` |

### Что обязательно менять

```python
REPO = Path(__file__).resolve().parents[N]  # уровень до корня проекта
LGP = REPO / "projects" / "my_lof.lgp"
WORK = Path(__file__).parent / "_work" / "my_project"
```

### GUID

- Не копировать GUID из референс-пакета в новый с нуля.
- Для патчей (`fix_*`, `patch_*`) — извлечь Guid из **вашего** `Unit.xml` (grep DisplayName).
- `extract_node_maps.py` — для справки по Engine, не по Guid.

### Зависимости между скриптами

```text
lof_native_nodes.py  ← build_lof_project.py, patch_lof_fix_unions.py
fix_lof_unit1_metrics.py  ← rebuild_lof_unit1.py, patch_lof_unit1_wiring.py
compare_lof_export.py  ← export_lof_dataset.py (опционально)
```

### Типичные ошибки при запуске

| Ошибка | Решение |
|--------|---------|
| `FileNotFoundError` LOF_template | указать свой template .lgp |
| `ModuleNotFoundError` sklearn | `pip install scikit-learn` |
| `Invalid XML` при pack | откат .bak, проверить баланс `<Items>` |
| Permission denied .lgp | закрыть Loginom |

---

## Таблица всех скриптов (кратко)

| Скрипт | Блок | Вход → Выход |
|--------|------|----------------|
| `loginom_pack.py` | ядро | .lgp ↔ папка |
| `loginom_lgd.py` | ядро | .lgd → диагностика |
| `extract_node_maps.py` | ядро | эталоны .lgp → `_node_maps.json` |
| `lof_native_nodes.py` | XML lib | функции → XML строки |
| `build_lof_project.py` | сборка | template → полный .lgp |
| `merge_lof_unit1_from_template.py` | сборка | эталон Unit_1 → user .lgp |
| `rebuild_lof_unit1.py` | сборка | оркестратор Unit_1 |
| `fix_lof_unit1_metrics.py` | патч | Unit.xml метки, beta |
| `patch_lof_unit1_wiring.py` | патч | Links valid/test |
| `fix_lof_model_path.py` | патч | filepath params |
| `patch_lof_fix_unions.py` | патч | Union/split |
| `patch_lof_user_lgp.py` | патч | порядок импорта |
| `build_lof_unit1_python_metrics.py` | альтернатива | Python Unit_1 |
| `number_workflow_blocks.py` | UI | нумерация + отчёт |
| `differentiate_unit1_layout.py` | UI | rename/position |
| `export_lof_dataset.py` | данные | txt+tsv → export TSV |
| `compare_lof_export.py` | данные | 2 TSV → diff |
| `probe_lof_partition.py` | данные | диагностика split |
| `match_lof_split.py` | данные | поиск логики split |
| `validate_lof_metrics.py` | метрики | sklearn grid |
| `analyze_lof_metrics.py` | метрики | Loginom vs sklearn |
| `build_regression_project.py` | регрессия | template → .lgp |
| `build_scoring_project.py` | скоринг | template → .lgp |
| `map_package_units.py` | регрессия | .lgp → JSON units |
