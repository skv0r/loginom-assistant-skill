# Каталог workflow Loginom

Сценарии по **типу задачи**, без привязки к учебным номерам.  
Эталонные `.lgp` пользователь указывает сам; skill описывает **паттерны узлов**.

Версия Loginom: **7.3.1** (типично). Пакеты **6.5.x** — устаревшие Engine (см. association-rules).

---

## Нативные компоненты (без python_kits)

| Workflow | Тема |
|----------|------|
| [etl-native.md](etl-native.md) | импорт, фильтр, сортировка, группировка, калькулятор, `.lgd` |
| [association-rules.md](association-rules.md) | транзакции → правила → фильтры support/confidence/lift |
| [feature-engineering.md](feature-engineering.md) | пропуски, выбросы, корреляции, OHLC, Python |
| [regression.md](regression.md) | Excel → recovery → dummy → логрегрессия → ROC |
| [abc-analysis.md](abc-analysis.md) | объём/выручка → ABC (silver_kit) |

## Машинное обучение (python_kits / встроенные ML)

| Workflow | Тема |
|----------|------|
| [clustering.md](clustering.md) | k-means, EM, meta-silhouettes |
| [scoring-woe.md](scoring-woe.md) | WOE, IV, coarse classes, логрегрессия, скоринг |
| [unsupervised-anomaly-lof.md](unsupervised-anomaly-lof.md) | LOF Novelty, meta-scaling, train/valid/test, metrics |

---

## Карта узлов из эталонов

```bash
python .cursor/skills/loginom-assistant/scripts/extract_node_maps.py
```

Скрипт читает пути к `.lgp` из своей конфигурации; для нового проекта — обновить список файлов в `extract_node_maps.py` или передать эталон вручную.

---

## Связанные документы

- [../lgp-xml-guide.md](../lgp-xml-guide.md) — типы `Engine`
- [../external-modules.md](../external-modules.md) — kits
- [../REFERENCE.md](../REFERENCE.md) — правка XML, LOF-инварианты
