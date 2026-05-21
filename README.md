---
name: loginom-assistant
description: >-
  Loginom 7.3.x: ETL, feature engineering, clustering, regression, scoring (WOE),
  association rules, anomaly detection (LOF + sklearn kits). Safe .lgp unpack/pack
  and XML workflow editing. Use for .lgp, .lgd, python_kits, silver_kit, splits, metrics.
---

# Loginom Assistant

Независимый skill для проектов **Loginom 7.3.x**.  
Фокус: цепочки узлов, kits, безопасная правка `.lgp`. Отчёты Word/PDF — вне scope.

---

## 1. Быстрый старт

1. Уточнить задачу, пути к данным, целевую переменную, метрику успеха.
2. Открыть workflow по типу задачи → [workflows/catalog.md](workflows/catalog.md).
3. Выдать план узлов (тип, порядок, проверки на промежуточных таблицах).
4. При правке пакета: backup → unpack → XML → validate → pack → проверка в Loginom.

| Расширение | Формат | Инструмент |
|------------|--------|------------|
| `.lgp` | ZIP + XML | [scripts/loginom_pack.py](scripts/loginom_pack.py) |
| `.lgd` | `BGDATA` | [lgd-format.md](lgd-format.md) |

---

## 2. Маршрутизация по типу задачи

| Задача | Документ |
|--------|----------|
| Сломался / правка `.lgp`, XML | [lgp-xml-workflow-structure.md](lgp-xml-workflow-structure.md) |
| Структура пакета, Engine, колонки | [lgp-xml-guide.md](lgp-xml-guide.md) |
| ETL, фильтры, разбиения, `.lgd` | [workflows/etl-native.md](workflows/etl-native.md) |
| Подготовка признаков | [workflows/feature-engineering.md](workflows/feature-engineering.md) |
| Ассоциативные правила | [workflows/association-rules.md](workflows/association-rules.md) |
| Кластеризация | [workflows/clustering.md](workflows/clustering.md) |
| ABC-анализ | [workflows/abc-analysis.md](workflows/abc-analysis.md) |
| Регрессия (линейная / логистическая) | [workflows/regression.md](workflows/regression.md) |
| Скоринг, WOE, IV | [workflows/scoring-woe.md](workflows/scoring-woe.md) |
| Аномалии, LOF, novelty | [workflows/unsupervised-anomaly-lof.md](workflows/unsupervised-anomaly-lof.md) |
| python_kits / silver_kit | [external-modules.md](external-modules.md) |
| Полный каталог workflow | [workflows/catalog.md](workflows/catalog.md) |

---

## 3. Пакеты и XML

```bash
python .cursor/skills/loginom-assistant/scripts/loginom_pack.py unpack "path/to/project.lgp" ./_work/pkg
# правки Unit_*/Unit.xml (Loginom закрыт)
python .cursor/skills/loginom-assistant/scripts/loginom_pack.py pack ./_work/pkg ./_work/out.lgp
python .cursor/skills/loginom-assistant/scripts/loginom_pack.py verify ./_work/out.lgp
```

Обязательно: [lgp-xml-workflow-structure.md](lgp-xml-workflow-structure.md) — границы `Nodes`/`Links`, запрет опасных regex, `ModelViews`.

Архитектура пакета и чеклисты: [REFERENCE.md](REFERENCE.md).

---

## 4. Внешние модули

`loginom_sklearn_kit`, `loginom_sklearn_meta`, `loginom_silver_kit`, `loginom_category_kit` — [external-modules.md](external-modules.md).

Документация API kits: `libs/python_kits/docs/*.md` в проекте пользователя (путь уточнять у пользователя).

---

## 5. Автоматизация (скрипты)

| Документ | Содержание |
|----------|------------|
| [scripts/README.md](scripts/README.md) | обзор, порядок запуска, зависимости |
| [scripts/SCRIPTS_REFERENCE.md](scripts/SCRIPTS_REFERENCE.md) | **полный справочник** — каждый скрипт, GUID, вход/выход, ошибки |

Блоки: **ядро** (`loginom_pack`) → **данные/split** → **сборка LOF** → **патчи XML** → **offline sklearn**.  
Скрипты `lof_*`, `build_lof_*`, `patch_lof_*` — референс-пайплайн LOF; пути — в `scripts/paths.py` ([PROJECT_LAYOUT.md](PROJECT_LAYOUT.md)). Для git: `scripts/_work/` и `__pycache__/` в `.gitignore`.

---

## 6. Типичные ошибки

| Симптом | Причина | Действие |
|---------|---------|----------|
| Пакет не открывается | regex удалил часть узла | откат `.bak`, правка по Guid |
| recall ≈ 0 (LOF) | неверные метки / порт train | [-1,1]→[1,0]; скоринг-порт fitter |
| metrics на 2000+ строк | нет фильтра SAMPLE | фильтр перед classification metrics |
| Нумерация «пропала» | узлы только в WorkFlow | нумеровать WorkFlow + ModelViews |

---

## 7. Качество ответов агента

- Не выдумывать узлы: ТЗ → эталон `.lgp` → docs kits.
- После XML — `verify` + баланс `<Items>`.
- Версия: целевая **7.3.1**; старые пакеты **6.5.x** — отдельная ветка (другие Engine).

---

## 8. Дополнительные материалы

| Документ | Содержание |
|----------|------------|
| [REFERENCE.md](REFERENCE.md) | архитектура пакета, LOF-инварианты, жизненный цикл правок |
| [examples/case-study-lof-ecg.md](examples/case-study-lof-ecg.md) | разбор референс-проекта LOF |
| [workflows/](workflows/) | пошаговые сценарии по типам задач |
