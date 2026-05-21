# Workflow: ETL и работа с данными (нативные узлы)

## Назначение

Импорт, очистка, преобразование, агрегация, экспорт. Без sklearn kits.

## Типовая цепочка

1. `TBGImportTextFile` — TXT/CSV (часто CodePage 1251)
2. `TBGFilterDataEngine` — фильтр строк
3. `TBGSortingEngine` — сортировка
4. `TBGGroupDataEngine` / `TBGColumnFlippingEngine` — агрегации
5. `TBGImportNative` / `TBGExportNative` — `.lgd`
6. `TBGCalcData` — выражения, новые поля
7. `TBGChartView` / `TBGCubeView` — визуализация

## Несколько сценариев в одном пакете

Один `.lgp` может содержать `Unit_0` … `Unit_N` — отдельные ETL-ветки (разные источники или этапы отчёта).

## Проверки

- Число строк после фильтра и объединения
- `ColumnDefs` импорта совпадают с калькулятором
- Пути `FileName` в `Engine` — относительно корня открытия пакета

## Связанные документы

- [lgd-format.md](../lgd-format.md)
- [lgp-xml-guide.md](../lgp-xml-guide.md)
