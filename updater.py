"""GitHub Releases의 최신 autocheck.exe로 자기 자신을 교체한다.

실행 중인 exe는 삭제할 수 없지만 이름은 바꿀 수 있으므로
  autocheck.exe → autocheck.old.exe,  autocheck.new.exe → autocheck.exe
순서로 바꾸고, 남은 autocheck.old.exe는 다음 실행 때 지운다.
"""
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from common import APP_DIR, APP_EXE, REPO, VERSION

API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
OLD_EXE = APP_DIR / "autocheck.old.exe"
NEW_EXE = APP_DIR / "autocheck.new.exe"
HEADERS = {"User-Agent": "ssafy-autocheck", "Accept": "application/vnd.github+json"}


def parse_version(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.strip().lstrip("v").split("."))
    except ValueError:
        return (0,)


def cleanup() -> None:
    for f in (OLD_EXE, NEW_EXE):
        try:
            f.unlink(missing_ok=True)
        except OSError:
            pass


def is_installed_exe() -> bool:
    if not getattr(sys, "frozen", False):
        return False
    here = os.path.normcase(str(Path(sys.executable).resolve().parent))
    return here == os.path.normcase(str(APP_DIR.resolve()))


def fetch(url: str, timeout: int):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=timeout)


def self_update(log) -> None:
    if not is_installed_exe():
        log("업데이트 확인 건너뜀 (설치 폴더의 exe로 실행한 경우에만 업데이트)")
        return

    try:
        with fetch(API_URL, 15) as r:
            release = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            log("업데이트: 아직 배포된 릴리스가 없음")
            return
        raise

    latest = release["tag_name"]
    if parse_version(latest) <= parse_version(VERSION):
        log(f"업데이트: 최신 버전 사용 중 (v{VERSION})")
        return

    asset = next((a for a in release.get("assets", []) if a["name"] == APP_EXE), None)
    if asset is None:
        log(f"업데이트: {latest} 릴리스에 {APP_EXE}가 없음 - 건너뜀")
        return

    log(f"업데이트: v{VERSION} → {latest} 다운로드 중")
    with fetch(asset["browser_download_url"], 300) as r, NEW_EXE.open("wb") as f:
        shutil.copyfileobj(r, f)
    if NEW_EXE.stat().st_size != asset["size"]:
        NEW_EXE.unlink()
        raise RuntimeError("다운로드한 파일 크기가 다름")

    current = APP_DIR / APP_EXE
    OLD_EXE.unlink(missing_ok=True)
    current.rename(OLD_EXE)
    try:
        NEW_EXE.rename(current)
    except OSError:
        OLD_EXE.rename(current)  # 원래 exe로 되돌림
        raise
    log(f"업데이트 완료: {latest} (다음 실행부터 적용)")
