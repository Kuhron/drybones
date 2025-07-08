from pathlib import Path


PROG_NAME_FOR_VERSION = "DryBones"
PROG_NAME_FOR_COMMAND = "dry"
DRYBONES_FILE_EXTENSION = ".dry"
HOME_DIR = Path.home()
DRYBONES_DIR_NAME = ".drybones"
GLOBAL_CONFIG_FP = HOME_DIR / ".drybones.conf"
PROJECT_CONFIG_FILE_NAME = "project.yaml"
if not GLOBAL_CONFIG_FP.exists():
    GLOBAL_CONFIG_FP.touch()
