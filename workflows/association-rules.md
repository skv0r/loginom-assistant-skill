# Workflow: ассоциативные правила

## Назначение

Поиск правил вида «если A, то B» в транзакционных данных (чеки, корзины).

## Типовая цепочка

| Этап | Engine / узел |
|------|----------------|
| Импорт чеков | `TBGImportTextFile` |
| Построение правил | `TBGAssnRulesEngine` |
| Фильтр по метрикам | `TBGFilterDataEngine` (support, confidence, lift) |
| Объединение веток | `TBGUnionDataEngine` |
| Просмотр | `TBGCubeView`, `TBGBrowseView` |

## Версия Loginom

Старые эталоны могут быть на **6.5.x** — перед переносом на 7.3.x сверить совместимость `TBGAssnRulesEngine`.

## Проверки

- Формат транзакций (ID чека, товар)
- Пороги support/confidence после фильтра не обнулили все правила
