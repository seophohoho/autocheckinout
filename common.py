import os
import sys
from pathlib import Path

# 릴리스 빌드 시 GitHub Actions가 태그 버전(v1.2.3 → 1.2.3)으로 바꿔 넣는다.
# 직접 빌드한 exe는 0.0.0이라 릴리스가 있으면 첫 실행 때 최신 릴리스로 업데이트된다.
VERSION = "0.0.0"
REPO = "seophohoho/autocheckinout"

APP_DIR = Path(os.environ["LOCALAPPDATA"]) / "SsafyAutoCheckin"
APP_EXE = "autocheck.exe"
TASKS = {"in": "SSAFY_AutoCheckin", "out": "SSAFY_AutoCheckout"}


def exe_dir() -> Path:
    """exe로 실행 중이면 exe가 있는 폴더, 아니면 소스 폴더."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent
