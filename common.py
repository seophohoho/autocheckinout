import os
import sys
from pathlib import Path

APP_DIR = Path(os.environ["LOCALAPPDATA"]) / "SsafyAutoCheckin"
APP_EXE = "autocheck.exe"
TASKS = {"in": "SSAFY_AutoCheckin", "out": "SSAFY_AutoCheckout"}


def exe_dir() -> Path:
    """exe로 실행 중이면 exe가 있는 폴더, 아니면 소스 폴더."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent
