# Справочник Loginom Assistant

Консолидированные практики для агента и разработчика. Без привязки к учебным номерам.

---

## 1. Архитектура пакета `.lgp`

```text
.lgp (ZIP)
├── PackageInfo.xml, PackageIndex.xml
├── References.xml          → внешние kits (.lgp)
├── Variables.xml
└── Unit_K/
    ├── Unit.xml            → сценарий (источник истины)
    ├── Info.xml
    └── Unit.bin            → не копировать из чужих шаблонов
```

Один пакет — несколько **сценариев** (`Unit_*`). Связь через **публичный узел** датасета или ссылку на узел другого Unit.

---

## 2. Два класса подготовки

| Класс | Средства | Workflow |
|-------|----------|----------|
| Нативные узлы | Фильтр, Разбиение, Калькулятор, Объединение | [workflows/etl-native.md](workflows/etl-native.md) |
| sklearn kits | meta-scaling, LOF, model.fitter, metrics | [workflows/unsupervised-anomaly-lof.md](workflows/unsupervised-anomaly-lof.md) и др. |

---

## 3. LOF: инварианты

1. Train — только норма.
2. LOF `novelty=true`.
3. Meta-scaling по train → применить ко всем потокам.
4. Скоринг valid/test — скоринговый порт fitter.
5. Метки: LOF {-1,1}→{1,0}; CLASS норма→0, аномалия→1.
6. Metrics только на отфильтрованном SAMPLE.
7. `beta` в metrics согласован с ТЗ (часто β=2).

---

## 4. Жизненный цикл правки XML

```text
ТЗ → эталон .lgp → backup → unpack → правки по Guid
  → баланс Items + parse → pack → verify → Loginom
```

**Не делать:** regex-удаление узлов; смена Guid цепочки; чужой `Unit.bin`.

**Делать:** переименование DisplayName; правка Links; аннотации.

---

## 5. Валидация

| Уровень | Инструмент |
|---------|------------|
| XML | `loginom_pack.py verify` |
| Данные | доли SAMPLE, число строк |
| Модель | offline sklearn на export |
| UI | classification metrics в Loginom |

---

## 6. Карта документов

| Блок | Документ |
|------|----------|
| Вход | [SKILL.md](SKILL.md) |
| Каталог задач | [workflows/catalog.md](workflows/catalog.md) |
| XML | [lgp-xml-workflow-structure.md](lgp-xml-workflow-structure.md), [lgp-xml-guide.md](lgp-xml-guide.md) |
| Kits | [external-modules.md](external-modules.md) |
| LOF | [workflows/unsupervised-anomaly-lof.md](workflows/unsupervised-anomaly-lof.md) |
| Скрипты | [scripts/README.md](scripts/README.md), [SCRIPTS_REFERENCE.md](scripts/SCRIPTS_REFERENCE.md) |
| Пример | [examples/case-study-lof-ecg.md](examples/case-study-lof-ecg.md) |

---

## 7. Чеклист LOF-проекта

- [ ] Split train/valid/test, seed фиксирован
- [ ] Train без аномалий; SAMPLE, IsTestSet
- [ ] Сетка k×c на valid, max Fbeta
- [ ] Test: F1 и матрица
- [ ] Пакет открывается без ошибок XML
