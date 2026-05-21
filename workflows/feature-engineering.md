# Workflow: подготовка признаков

## Назначение

Очистка, восстановление пропусков, удаление выбросов, корреляционный анализ, производные признаки (OHLC и др.).

## Типовая цепочка

| Этап | Engine |
|------|--------|
| Импорт | `TBGImportTextFile` |
| Скриптовая логика | `TBGPythonEngine` (опционально) |
| Корреляции | `TBGCorrAnalysisEngine` |
| Признаки | `TBGCalcData` |
| Пропуски | `TBGDataRecoveryEngine` |
| Выбросы | `TBGElimOutlierEngine` |
| Экспорт | `TBGExportTextFile` |

## Правила для агента

- Замена CSV пользователя → обновить `FileName` и `ColumnDefs` в импорте и во всех `TBGCalcData`, ссылающихся на колонки
- Python: зависимости и пути к скрипту в настройках `TBGPythonEngine`
