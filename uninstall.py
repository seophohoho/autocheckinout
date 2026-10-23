"""작업 스케줄러 작업과 설치 폴더(계정 정보 포함)를 삭제한다."""
import shutil
import subprocess
import sys
import time

from common import APP_DIR, APP_EXE, TASKS, exe_dir


def main() -> None:
    print("=== SSAFY 자동 입퇴실 제거 ===\n")

    for name in TASKS.values():
        r = subprocess.run(["schtasks", "/Delete", "/TN", name, "/F"], capture_output=True)
        print(f"- 작업 삭제: {name}" + ("" if r.returncode == 0 else " (등록된 작업 없음)"))

    subprocess.run(["taskkill", "/IM", APP_EXE, "/F"], capture_output=True)
    time.sleep(1)

    if APP_DIR.exists():
        shutil.rmtree(APP_DIR)
        print(f"- 설치 폴더 삭제 (계정 정보, 로그 포함): {APP_DIR}")
    else:
        print("- 설치 폴더 없음")

    local_env = exe_dir() / ".env"
    if local_env.exists():
        if input(f"\n{local_env} 에도 계정 정보가 있습니다. 삭제할까요? (Y/n): ").strip().lower() != "n":
            local_env.unlink()
            print("- 삭제했습니다.")

    print("\n제거가 끝났습니다.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[오류] {e}")
    input("\n엔터를 누르면 창이 닫힙니다...")
    sys.exit(0)
