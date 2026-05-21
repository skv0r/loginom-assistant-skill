# Workflow: кластеризация

## Назначение

Разбиение объектов на кластеры; оценка качества (silhouette).

## Типовая цепочка

| Этап | Engine / компонент |
|------|-------------------|
| Импорт | `TBGImportExcelFileEngine` |
| Подготовка полей | `TBGReformColumnsEngine` |
| k-means | `TBGClusterizationEngine` |
| EM | `TBGEMEngine` |
| Оценка | `meta-silhouettes` (python_kits) |
| Отбор | `TBGFilterDataEngine` |

## Kits

Требуется `loginom_sklearn_kit.lgp` в `References.xml`. См. [external-modules.md](../external-modules.md).

## Проверки

- Число кластеров k и метрика silhouette на валидационной выборке
- Масштабирование признаков до кластеризации (если в эталоне есть meta-scaling)
