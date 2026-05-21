# Структура `.lgp` (Loginom 7.3.x)

## Контейнер

- Файл `.lgp` — **ZIP-архив** (сигнатура `PK` в первых байтах).
- Проверка и распаковка: `scripts/loginom_pack.py`.

## Корневые файлы пакета

| Файл | Назначение |
|------|------------|
| `PackageInfo.xml` | Имя пакета, `ApplicationVersion`, `Guid`, локаль |
| `Variables.xml` | Переменные пакета |
| `References.xml` | Ссылки на внешние пакеты/модули |
| `Reports.xml` | Отчёты |
| `Unit_N/Unit.xml` | Сценарий (workflow) N |
| `Unit_N/Info.xml` | Метаданные сценария |
| `Unit_N/Unit.bin`, `Info.bin` | Бинарные дополнения (не править без необходимости) |

## Узел workflow

В `Unit.xml` узлы находятся в:

```xml
<Unit>
  <WorkFlow xsi:type="TBGPackageModelWorkFlow">
    <Nodes>
      <Item Guid="..." DisplayName="..." VendorGuid="...">
        ...
        <Component>
          <Engine xsi:type="TBGImportTextFile" FileName="..." CodePage="1251">
            <ColumnDefs>...</ColumnDefs>
          </Engine>
        </Component>
        <Position Left="..." Top="..."/>
      </Item>
    </Nodes>
  </WorkFlow>
</Unit>
```

## Полезные атрибуты

| Элемент | Атрибуты |
|---------|----------|
| Узел | `DisplayName`, `Guid`, `VendorGuid` |
| Колонка | `Name`, `DisplayName`, `DataType`, `DataKind`, `UsageType` |
| Engine | `xsi:type` (тип компонента), плюс специфичные (`FileName`, `CodePage`, …) |
| Порты | `InputPorts`, `OutputPorts`, `Name`, `DisplayName` |

## Типы Engine (типовые задачи)

| xsi:type | Назначение |
|----------|-------------------|
| `TBGImportTextFile` | TXT/CSV |
| `TBGImportExcelFileEngine` | Excel |
| `TBGImportNative` | `.lgd` |
| `TBGExportNative` | экспорт `.lgd` |
| `TBGFilterDataEngine` | фильтр строк |
| `TBGCalcData` | калькулятор / выражения |
| `TBGGroupDataEngine` | группировка |
| `TBGSortingEngine` | сортировка |
| `TBGAssnRulesEngine` | ассоциативные правила |
| `TBGPythonEngine` | Python / python_kits |
| `TBGCorrAnalysisEngine` | корреляции |
| `TBGDataRecoveryEngine` | пропуски |
| `TBGElimOutlierEngine` | выбросы |
| `TBGClusterizationEngine` | k-means |
| `TBGEMEngine` | EM-кластеризация |
| `TBGLogRegressionEngine` | логистическая регрессия |
| `TBGCoarseClassesEngine` | конечные классы (скоринг) |
| `TBGModelGenericComponentEngine` | компоненты python_kits / silver_kit |

## PackageIndex.bin

Loginom 7.3 может **предпочитать** `PackageIndex.bin` перед `PackageIndex.xml`. При сборке кастомных пакетов не копируйте `.bin` из шаблона с другим числом сценариев — иначе ошибки вида «не удалось открыть `\Unit_2\Info.bin`». Используйте только актуальный `PackageIndex.xml` или пересохраните пакет в Loginom.

## WorkFlow: Nodes, Links, ModelViews

Подробно (границы XML, ошибки агентов, нумерация): **[lgp-xml-workflow-structure.md](lgp-xml-workflow-structure.md)**.

Кратко:

- Рабочие узлы — `WorkFlow/Nodes` (элементы с `VendorGuid`).
- `WorkFlow/Links` — только связи; не путать с Filter/Replace.
- Таблицы/статистика на холсте могут дублироваться в `ModelViews/Nodes`.
- `ServiceNodes` — переменные сценария.

## Правка и сборка

1. `loginom_pack.py unpack` → каталог.
2. Править только нужные `Unit.xml` / `Variables.xml`.
3. `loginom_pack.py pack` → новый `.lgp`.
4. `loginom_pack.py verify` — валидность ZIP и XML.
5. Открыть в Loginom и выполнить пакет (финальная проверка).

**Не менять** `Guid` узлов и портов, если не создаёте новый узел с нуля. При добавлении узла — новые уникальные Guid.

## Пути к данным

В XML часто относительные пути к данным. При переносе проекта обновить `FileName` в `Engine` импорта и проверить `ColumnDefs`.
