# Case study: LOF на табличных данных ЭКГ (ECG5000)

Разбор **референс-реализации** паттерна из [workflows/unsupervised-anomaly-lof.md](../workflows/unsupervised-anomaly-lof.md).  
Пути к файлам — в конкретном проекте пользователя; skill не привязан к номеру учебной работы.

## Контекст

| Параметр | Типичное значение |
|----------|-------------------|
| Пакет | `*.lgp` с двумя Unit: подготовка + модель |
| Данные | два TXT, ~3233 строки после исключения пограничного класса |
| Модули | `loginom_sklearn_meta.lgp`, `loginom_sklearn_kit.lgp` |
| Модель | LOF Novelty; сетка k∈{15,20,25}, c∈{0.02,0.05}; выбор по max Fbeta |

## Этапы реализации

1. **Сценарий подготовки** — нативное разбиение 70/15/15, seed=42, SAMPLE, IsTestSet, публичный узел датасета.
2. **Сценарий модели** — meta-scaling, LOF, model.fitter, замена меток, classification metrics.
3. **Правка связей** — valid/test на скоринговый порт fitter (не train).
4. **Нумерация узлов** — DisplayName по позиции на схеме (без смены Guid).

## Типичные метрики (ориентир)

| Выборка | Примечание |
|---------|------------|
| valid | подбор k, c по Fbeta (β=2) |
| test | итоговый F1 и матрица ошибок |

Расхождение с «эталоном из методички» при совпадении offline sklearn на том же export обычно из‑за **другого split**, не ошибки цепочки.

## Уроки (переносимые)

| Проблема | Решение |
|----------|---------|
| recall ≈ 0 | замена outlier_label; бинарный CLASS |
| XML не открывается | не удалять узлы regex; откат `.bak` |
| metrics на 2000+ строк | фильтр SAMPLE перед metrics |
| params внутри filepath-узла | менять `params` на главной схеме у LOF/fitter |

## Скрипты-референс

- [scripts/README.md](../scripts/README.md) — порядок запуска пайплайна  
- [scripts/SCRIPTS_REFERENCE.md](../scripts/SCRIPTS_REFERENCE.md) — `build_lof_project.py`, `validate_lof_metrics.py`, патчи wiring/metrics и др.
