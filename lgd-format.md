# Формат `.lgd`

## Результат проверки

Файлы `.lgd` в Loginom 7.3.x (импорт через `TBGImportNative`):

| Проверка | Результат |
|----------|-----------|
| Магические байты | `BGDATA` (не `PK`) |
| Переименование в `.zip` | **Ошибка** `BadZipFile` |
| Встроенный ZIP | **Не найден** как валидный архив |

**Вывод:** `.lgd` — проприетарный контейнер **BGDATA**, не ZIP.

```bash
python .cursor/skills/loginom-assistant/scripts/loginom_lgd.py "path/to/data.lgd"
```

## Как работать агенту

1. **Импорт/экспорт** — `TBGImportNative` / `TBGExportNative` в `.lgp`.
2. **Обмен с агентом** — экспорт в CSV/TXT из Loginom или исходные CSV пользователя.
3. **Не** распаковывать `.lgd` переименованием в `.zip`.

## Связь с `.lgp`

```xml
<Engine xsi:type="TBGImportNative" FileName="data/train.lgd" .../>
```

При смене данных: новый `.lgd` из Loginom или замена на `TBGImportTextFile` + CSV.
