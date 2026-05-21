# Layout проекта для Loginom Assistant

Скилл не привязан к номерам лабораторных работ. Задайте корень данных:

```bash
# Windows PowerShell
$env:LOGINOM_PROJECT_ROOT = "C:\path\to\your\project"

# или скопируйте scripts/paths.local.example.py → scripts/paths.local.py
```

## Структура каталогов

```
<PROJECT_ROOT>/
  data/
    lof/                    # ecg_train.txt, ecg_test.txt, export_*.txt, sample_by_object.tsv
    regression/             # xlsx для регрессии
    scoring/                # otp_train.lgd, otp_test.lgd
  packages/
    etl/packet1.lgp
    association/packet2.lgp
    features/features_reference.lgp
    clustering/clustering_reference.lgp
    abc/ABC_template.lgp
    regression/regression_reference.lgp
    regression/regression_package.lgp    # выход build_regression_project.py
    scoring/scoring_reference.lgp
    scoring/scoring_otp_package.lgp      # выход build_scoring_project.py
    lof/
      LOF_template.lgp
      LOF_reference.lgp       # эталон Unit_1 (kits)
      lof_package.lgp         # рабочий пакет
    libs/
      python_kits/python_kits/loginom_sklearn_kit.lgp
      python_kits/python_kits/loginom_sklearn_meta.lgp
      silver_kit/silver_kit/loginom_silver_kit.lgp
```

## Миграция со старых папок ЛР1–ЛР8

| Было | Стало |
|------|--------|
| `ЛР8/*.txt`, export | `data/lof/` |
| `ЛР8/мареев.lgp` | `packages/lof/LOF_reference.lgp` |
| `ЛР8/lr8_lof.lgp` | `packages/lof/lof_package.lgp` |
| `ЛР4/libs/...` | `packages/libs/...` |
| `ЛР6/*.xlsx` | `data/regression/` |
| `ЛР7/*.lgd` | `data/scoring/` |

`scripts/_work/` — только временные распаковки; в git не коммитится.
