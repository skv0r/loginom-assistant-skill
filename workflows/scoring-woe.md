# Workflow: скоринг и WOE-кодирование

## Назначение

Бинарная классификация с отбором признаков (IV), WOE, логистическая регрессия, ROC.

## Типовая цепочка

| Этап | Engine / компонент |
|------|-------------------|
| Train / test | `TBGImportNative` (`.lgd`) |
| Пропуски | `TBGDataRecoveryEngine` |
| Грубые классы | `TBGCoarseClassesEngine` |
| WOE | `WOE_ENCODER` (python_kits) или `TBGPythonEngine` |
| IV-отбор | category_kit / silver_kit |
| Модель | `TBGLogRegressionEngine` |
| Оценка | `TBGROCView`, `TBGLogRegressReport` |

## Модули

- `loginom_sklearn_kit.lgp`
- `loginom_category_kit.lgp` (IV, категории)
- `loginom_silver_kit.lgp` (опционально)

См. [external-modules.md](../external-modules.md).

## Проверки

- Train и test разделены; WOE считается **только на train**
- Схема TARGET / отклик согласована между `.lgd`
- Gini / ROC на hold-out test
