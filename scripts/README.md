# Scripts — Loginom Assistant

Автоматизация для работы с `.lgp`, `.lgd`, подготовкой данных и offline-проверкой LOF.  
Полная справка по каждому файлу: **[SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md)**.

---

## Требования

| Зависимость | Скрипты |
|-------------|---------|
| Python 3.10+ | все |
| stdlib (`zipfile`, `xml.etree`) | `loginom_pack.py`, правки XML |
| `pandas` | export, compare, probe, validate |
| `numpy`, `scikit-learn` | validate, analyze, build_unit1_python |

```bash
pip install pandas numpy scikit-learn
```

---

## Быстрые команды

```bash
cd .cursor/skills/loginom-assistant/scripts

# Распаковка / сборка пакета
python loginom_pack.py unpack "path/to/project.lgp" ./_work/pkg
python loginom_pack.py pack ./_work/pkg ./_work/out.lgp
python loginom_pack.py verify ./_work/out.lgp

# Карта узлов из эталонных .lgp (пути — в paths.py)
python extract_node_maps.py

# Offline LOF: сетка k×c (пути к данным — в начале validate_lof_metrics.py)
python validate_lof_metrics.py
```

---

## Смысловые блоки

```text
┌─────────────────────────────────────────────────────────────┐
│  ЯДРО: loginom_pack, loginom_lgd, extract_node_maps         │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ДАННЫЕ: export_*, compare_*, probe_*, match_*                │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  СБОРКА ПАКЕТА LOF: build_* → merge_* → fix_* → patch_*      │
│  Модуль XML: lof_native_nodes.py                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ОФОРМЛЕНИЕ: number_*, differentiate_* (только Guid)      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ПРОВЕРКА: validate_*, analyze_*                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Рекомендуемый порядок (референс LOF / ECG)

| Шаг | Скрипт | Когда |
|-----|--------|-------|
| 1 | `build_lof_project.py` | Собрать Unit_0 (split) с нуля |
| 2 | `merge_lof_unit1_from_template.py` | Подтянуть Unit_1 из эталона kits |
| 3 | `rebuild_lof_unit1.py` | metrics + wiring одной командой |
| 4 | `fix_lof_unit1_metrics.py` | Только метки / beta / model path |
| 5 | `patch_lof_unit1_wiring.py` | Только valid/test → скоринг-порт |
| 6 | `number_workflow_blocks.py` | Нумерация узлов на схеме |
| 7 | `loginom_pack.py verify` | Перед открытием в Loginom |
| 8 | `validate_lof_metrics.py` | Сверка метрик с sklearn |

Альтернатива Unit_1 без kits: `build_lof_unit1_python_metrics.py`.

---

## Адаптация под новый проект

1. Скопировать нужные скрипты или вызывать из skill.
2. Пути — в **`paths.py`** и [PROJECT_LAYOUT.md](../PROJECT_LAYOUT.md). Задайте `LOGINOM_PROJECT_ROOT` или `paths.local.py`.
   - LOF Unit_1: `packages/lof/LOF_reference.lgp`
   - Данные ECG: `data/lof/`
3. В скриптах при необходимости — `WORK`, GUID, пути к `ecg_*.txt` / export.
4. GUID узлов — **уникальны в каждом пакете**; для правок использовать `extract_node_maps.py` или grep по `Unit.xml`.
5. Не копировать `Unit.bin` из чужого шаблона (`DROP_UNIT_BIN` в сборщиках).

Подробно: [SCRIPTS_REFERENCE.md § Адаптация](SCRIPTS_REFERENCE.md#адаптация-скриптов).

---

## Служебные / отладочные

| Файл | Назначение |
|------|------------|
| `_work/` | временные распаковки (не коммитить) |
| `inspect_lgp_pair.py` | сравнение двух .lgp |
| `_analyze_user_lof.py` | разовый расчёт метрик по export |
| `_work/` (в .gitignore) | временные распаковки; пересоздаются скриптами |

---

## Правила для агента

1. **Loginom закрыт** перед `pack`.
2. **Backup** `.lgp.bak` создаётся автоматически в `loginom_pack.py pack`.
3. После правки XML — `verify` + баланс `<Items>` (см. `number_workflow_blocks.py` → отчёт).
4. **Запрещено** удаление узлов через regex `.*?` — см. [lgp-xml-workflow-structure.md](../lgp-xml-workflow-structure.md).
5. `differentiate_unit1_layout.py` — только rename/position по Guid.

---

## Связанные документы

- [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) — полное описание каждого скрипта
- [../workflows/unsupervised-anomaly-lof.md](../workflows/unsupervised-anomaly-lof.md) — логика LOF в Loginom
- [../lgp-xml-workflow-structure.md](../lgp-xml-workflow-structure.md) — границы XML
