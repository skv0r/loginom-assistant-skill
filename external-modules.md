# Внешние модули (kits)

Готовые пакеты Loginom Python Kits и silver_kit. Пути — **в проекте пользователя** (типично `libs/python_kits/`, `libs/silver_kit/`).

## Расположение (шаблон)

| Модуль | Типичный путь |
|--------|----------------|
| Документация API | `libs/python_kits/docs/*.md` |
| sklearn kit | `libs/python_kits/python_kits/loginom_sklearn_kit.lgp` |
| meta kit | `libs/python_kits/python_kits/loginom_sklearn_meta.lgp` |
| silver kit | `libs/silver_kit/silver_kit/loginom_silver_kit.lgp` |
| category kit | `loginom_category_kit.lgp` (рядом с проектом или в libs) |

Подключение: `References.xml` целевого `.lgp`.

---

## python_kits — компоненты

| Узел | Назначение | Workflow |
|------|------------|----------|
| `meta-scaling` | z-нормализация по train | LOF, кластеризация |
| `neighbors.LOF Novelty` | LOF, novelty | [unsupervised-anomaly-lof.md](workflows/unsupervised-anomaly-lof.md) |
| `model.fitter` / `simple.fitter` | fit / predict | LOF, скоринг |
| `classification metrics` | P, R, F1, Fbeta, TN/FP/FN/TP | LOF, классификация |
| `meta-silhouettes` | качество кластеров | [clustering.md](workflows/clustering.md) |
| `WOE_ENCODER` | WOE | [scoring-woe.md](workflows/scoring-woe.md) |

### Параметры LOF / fitter

Часто задаются переменной **`params`** на узле (не во внутреннем `__current_filepath`):

```text
n_neighbors=20,contamination=0.05
```

Переменная **`filepath`** — каталог для `model.pkl`.

---

## silver_kit

| Узел | Назначение |
|------|------------|
| ABC-анализ (выполнение) | классы A/B/C по объёму |
| ABC (метод касательных) | альтернативный метод |

См. [workflows/abc-analysis.md](workflows/abc-analysis.md).

---

## Правила для агента

1. Не выдумывать параметры — сверять с `docs/<component>.md` и эталонным `Unit.xml`.
2. При настройке — DisplayName и схема полей как в эталоне **того же типа задачи**.
3. Внутренняя схема kit (`__current_filepath`, `Компонент`) — загрузка модели, **не** сетка гиперпараметров.

---

## Подключение нового python-компонента

1. Добавить kit в `References.xml`.
2. Узел `TBGModelGenericComponentEngine` / `TBGPythonEngine` по образцу эталона.
3. Синхронизировать `ColumnDefs`, `SyncThroughColumns`.
