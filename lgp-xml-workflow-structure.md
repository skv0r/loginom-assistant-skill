# Структура сценария в `Unit.xml` (Loginom 7.3.x)

Документ для **безопасной** правки workflow через скрипты. Применим к любому пакету с `TBGPackageModelWorkFlow`.

## Иерархия одного сценария (`Unit_N`)

```text
Unit.xml
└── WorkFlow (TBGPackageModelWorkFlow)
    ├── Nodes          ← основные узлы на холсте
    ├── Links          ← связи (НЕ узлы компонентов)
    ├── ServiceNodes   ← переменные сценария и служебное
    ├── ServiceLinks
    └── Annotations    ← текстовые блоки на холсте
└── ModelViews
    └── Nodes          ← часто: таблицы, статистика (те же Guid, что на схеме)
```

**Важно:** узлы «Таблица» / «Статистика» могут жить в `ModelViews/Nodes`, а не только в `WorkFlow/Nodes`. При нумерации и аудите учитывать **оба** блока.

## Как извлечь только блок `WorkFlow/Nodes`

**Правильно** — граница перед `Links` на уровне вкладки `\t\t`:

```python
wf = text.find('<WorkFlow xsi:type="TBGPackageModelWorkFlow">')
start = text.find("\n\t\t<Nodes>", wf) + len("\n\t\t<Nodes>")
end = text.find("\n\t\t</Nodes>\n\t\t<Links>", start)
nodes_block = text[start:end]
```

**Неправильно:**

- `re.search(r"<Nodes>(.*)</Nodes>\s*<Links>", sub, re.DOTALL)` без ограничения области — захватит **последнюю** пару в файле (вложенные `Nodes` внутри компонентов).
- Подсчёт глубины `<Nodes>` от первого вхождения — закроется на **первом вложенном** `</Nodes>` внутри первого узла.

## Отличить узел от связи

| Признак | Узел компонента | Связь (Link) |
|---------|-----------------|--------------|
| `VendorGuid` | есть | нет |
| `DisplayName` | обычно есть | нет |
| `Component` / `Engine` | есть | нет |
| Дочерний элемент | порты, сокеты | только `SourcePort` + `TargetPort` |

Элементы в `Links` с `Guid` **не переименовывать** как блоки — это не Filter/Replace.

## Безопасные операции (рекомендуется агенту)

| Операция | Подход |
|----------|--------|
| Переименование | По `Guid`: заменить только `DisplayName` у `\t\t\t<Item Guid="…" … VendorGuid=` |
| Позиция на холсте | Первый `<Position Left="…" Top="…"/>` внутри chunk этого `Guid` |
| Нумерация «1. …» | Отдельная нумерация **на каждый Unit**; порядок — по `(Top, Left)` или по топологии связей |
| Проверка после правки | `text.count("<Items>") == text.count("</Items>")` и `xml.etree.ElementTree.fromstring(text)` |

## Опасные операции (избегать)

1. **`re.sub(r"<Item Guid=…>.*?</Item>")` с `DOTALL`** — останавливается на первом вложенном `</Item>`, ломает XML (ошибки `DataValue` / `ReplaceBy` вне контекста, `Nodes`/`Items` mismatch).
2. **Вставка «пустых» узлов** с неверным `VendorGuid` или без полной копии структуры `Component` — Loginom не откроет пакет.
3. **Удаление узлов** из активной цепочки без переподключения `Links` — сценарий откроется, но метрики станут неверными.
4. **Правка `PackageIndex.bin` / `Unit.bin`** из чужого шаблона — ошибки «не удалось открыть Unit.bin». Для 7.3 часто достаточно `Unit.xml` + `PackageIndex.xml` (без `.bin`).

## Пересборка ZIP (`.lgp`)

```bash
python .cursor/skills/loginom-assistant/scripts/loginom_pack.py unpack project.lgp ./_work/pkg
# правки в _work/pkg/Unit_*/Unit.xml
python .cursor/skills/loginom-assistant/scripts/loginom_pack.py pack ./_work/pkg ./_work/pkg_edited.lgp
python .cursor/skills/loginom-assistant/scripts/loginom_pack.py verify ./_work/pkg_edited.lgp
```

Перед `pack`: **закрыть Loginom** (иначе файл занят). Делать backup `.lgp.bak_*`.

## Типовые `VendorGuid` (ориентир)

| VendorGuid (префикс) | Тип в UI |
|----------------------|----------|
| `a0e49d86-…` | Фильтр |
| `dc279f34-…` | Изменение / удаление полей (Reform) |
| `5346793b-…` | Замена |
| `f5aa91d2-…` | Объединение |
| `b2161dca-…` | Разбиение на множества |
| `c7b69712-…` | Калькулятор |
| `dd767700-…` | Импорт текста |
| `f2b7b8c5-…` | model.fitter (kits) |
| `e6ed8484-…` | Просмотр таблицы |
| `121165f9-…` | Статистика |

Точные имена компонентов смотреть в `Engine/@xsi:type` и `DisplayName` эталонного узла.

## Симптомы поломки XML

| Сообщение Loginom | Вероятная причина |
|-------------------|------------------|
| `Opening and ending tag mismatch: Nodes … Items` | Обрезан или вставлен фрагмент внутри `Nodes` |
| `Элемент схемы DataValue / ReplaceBy не найден` | Обрывки `ReplaceTable` попали на уровень workflow |
| `не удалось открыть Unit.bin` | Часто следствие невалидного `Unit.xml` |

Восстановление: откат из `.bak_*` или `loginom_pack.py unpack` последнего рабочего `.lgp`.
