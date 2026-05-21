"""Project-relative paths for Loginom assistant (no lab numbers or personal dirs)."""
from __future__ import annotations

import os
from pathlib import Path

_local = Path(__file__).with_name("paths.local.py")
if _local.is_file():
    import importlib.util

    _spec = importlib.util.spec_from_file_location("_paths_local", _local)
    _mod = importlib.util.module_from_spec(_spec)
    assert _spec.loader is not None
    _spec.loader.exec_module(_mod)

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
WORK_ROOT = SCRIPTS_DIR / "_work"


def project_root() -> Path:
    """Override with env LOGINOM_PROJECT_ROOT when the skill lives outside your data repo."""
    env = os.environ.get("LOGINOM_PROJECT_ROOT")
    if env:
        return Path(env)
    # Default: repo root above .cursor (monorepo layout)
    return Path(__file__).resolve().parents[4]


PROJECT = project_root()
DATA = PROJECT / "data"
PACKAGES = PROJECT / "packages"

# --- datasets ---
LOF_DATA = DATA / "lof"
REGRESSION_DATA = DATA / "regression"
SCORING_DATA = DATA / "scoring"

# --- package dirs ---
LOF_PKG = PACKAGES / "lof"
REGRESSION_PKG = PACKAGES / "regression"
SCORING_PKG = PACKAGES / "scoring"
ETL_PKG = PACKAGES / "etl"
ASSOCIATION_PKG = PACKAGES / "association"
FEATURES_PKG = PACKAGES / "features"
CLUSTERING_PKG = PACKAGES / "clustering"
ABC_PKG = PACKAGES / "abc"

LIBS_ROOT = PACKAGES / "libs"
SKLEARN_KIT_LGP = (
    LIBS_ROOT / "python_kits" / "python_kits" / "loginom_sklearn_kit.lgp"
)
SILVER_KIT_LGP = LIBS_ROOT / "silver_kit" / "silver_kit" / "loginom_silver_kit.lgp"
SKLEARN_META_LGP = (
    LIBS_ROOT / "python_kits" / "python_kits" / "loginom_sklearn_meta.lgp"
)

# --- reference .lgp (for extract_node_maps / builders) ---
ETL_REFERENCE_LGP = ETL_PKG / "packet1.lgp"
ASSOCIATION_REFERENCE_LGP = ASSOCIATION_PKG / "packet2.lgp"
FEATURES_REFERENCE_LGP = FEATURES_PKG / "features_reference.lgp"
CLUSTERING_REFERENCE_LGP = CLUSTERING_PKG / "clustering_reference.lgp"
ABC_TEMPLATE_LGP = ABC_PKG / "ABC_template.lgp"
REGRESSION_REFERENCE_LGP = REGRESSION_PKG / "regression_reference.lgp"
SCORING_REFERENCE_LGP = SCORING_PKG / "scoring_reference.lgp"

# --- LOF ---
LOF_TEMPLATE_LGP = LOF_PKG / "LOF_template.lgp"
LOF_REFERENCE_LGP = LOF_PKG / "LOF_reference.lgp"
LOF_PACKAGE_LGP = LOF_PKG / "lof_package.lgp"
LOF_PACKAGE_NAME = "lof_package"
LOF_EXPORT_REFERENCE = LOF_DATA / "export_reference.txt"
LOF_EXPORT_OUT = LOF_DATA / "export_out.txt"
LOF_SAMPLE_MAP = LOF_DATA / "sample_by_object.tsv"
LOF_EXPORT_SCRIPT_OUT = LOF_DATA / "export_output.txt"
LOF_NUMBERING_REPORT = LOF_DATA / "check_methodology_numbering.txt"

# --- regression / scoring builders ---
REGRESSION_TEMPLATE_LGP = REGRESSION_REFERENCE_LGP
REGRESSION_OUT_LGP = REGRESSION_PKG / "regression_package.lgp"
REGRESSION_PACKAGE_NAME = "regression_package"

SCORING_TEMPLATE_LGP = SCORING_REFERENCE_LGP
SCORING_OUT_LGP = SCORING_PKG / "scoring_otp_package.lgp"
SCORING_PACKAGE_NAME = "scoring_otp_package"

# Relative paths inside Loginom XML (from project root when opening .lgp)
LOF_DATA_REL = "data/lof"
REGRESSION_DATA_REL = "data/regression"
SCORING_DATA_REL = "data/scoring"
LIBS_REL = "packages/libs"
LIBS_REL_POSIX = LIBS_REL.replace("\\", "/")


def rel_to_project(path: Path) -> str:
    """Path string for Loginom FileName / HintPath (forward slashes)."""
    try:
        return path.relative_to(PROJECT).as_posix()
    except ValueError:
        return path.as_posix()


# --- script work directories (recreated on run; not committed) ---
WORK_LOF_BUILD = WORK_ROOT / "lof_build"
WORK_LOF_NATIVE = WORK_ROOT / "lof_native_build"
WORK_LOF_MERGE = WORK_ROOT / "lof_merge_template"
WORK_LOF_LAYOUT = WORK_ROOT / "lof_layout"
WORK_LOF_NUMBER = WORK_ROOT / "lof_number"
WORK_LOF_PATCH = WORK_ROOT / "lof_patch_unions"
WORK_LOF_USER_PATCH = WORK_ROOT / "lof_user_patch"
WORK_LOF_FIX_METRICS = WORK_ROOT / "lof_fix_metrics"
WORK_LOF_FIX_MODEL = WORK_ROOT / "lof_fix_model_path"
WORK_LOF_UNIT1_PY = WORK_ROOT / "lof_unit1_python"
WORK_LOF_NATIVE_WIRING = WORK_ROOT / "lof_native_wiring"
WORK_REGRESSION_BUILD = WORK_ROOT / "regression_build"
WORK_REGRESSION_REF = WORK_ROOT / "regression_ref"
WORK_SCORING_BUILD = WORK_ROOT / "scoring_build"

# Back-compat aliases used during migration
REPO_ROOT = PROJECT
LOF_DIR = LOF_DATA
