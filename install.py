"""autocheck.exe를 설치하고 작업 스케줄러에 입실/퇴실 작업을 등록한다.
  - 입실: 윈도우 로그인 30초 후
  - 퇴실: 평일(월~금) 18:00
"""
import datetime
import getpass
import os
import shutil
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

from dotenv import dotenv_values

from common import APP_DIR, APP_EXE, TASKS, exe_dir

TASK_XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>{description}</Description></RegistrationInfo>
  <Triggers>{trigger}
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{user}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <WakeToRun>{wake}</WakeToRun>
    <ExecutionTimeLimit>PT15M</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{command}</Command>
      <Arguments>{arguments}</Arguments>
      <WorkingDirectory>{workdir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""

LOGON_TRIGGER = """
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>{user}</UserId>
      <Delay>PT30S</Delay>
    </LogonTrigger>"""

WEEKDAY_18_TRIGGER = """
    <CalendarTrigger>
      <Enabled>true</Enabled>
      <StartBoundary>{start}</StartBoundary>
      <ScheduleByWeek>
        <WeeksInterval>1</WeeksInterval>
        <DaysOfWeek><Monday /><Tuesday /><Wednesday /><Thursday /><Friday /></DaysOfWeek>
      </ScheduleByWeek>
    </CalendarTrigger>"""


def ask_credentials() -> tuple[str, str]:
    src_env = exe_dir() / ".env"
    if src_env.exists():
        env = dotenv_values(src_env)
        if env.get("USERNAME") and env.get("PASSWORD"):
            print(f"- {src_env} 의 계정 정보를 사용합니다.")
            return env["USERNAME"], env["PASSWORD"]

    print("- SSAFY 계정 정보를 입력하세요. (비밀번호는 화면에 표시되지 않습니다)")
    while True:
        user = input("  아이디(이메일): ").strip()
        pw = getpass.getpass("  비밀번호: ")
        if user and pw:
            return user, pw
        print("  아이디와 비밀번호를 모두 입력하세요.")


def register_task(name: str, description: str, trigger: str, arguments: str, wake: bool) -> None:
    user = escape(f"{os.environ['USERDOMAIN']}\\{os.environ['USERNAME']}")
    xml = TASK_XML.format(
        description=escape(description),
        trigger=trigger.format(user=user, start=f"{datetime.date.today()}T18:00:00"),
        user=user,
        wake=str(wake).lower(),
        command=escape(str(APP_DIR / APP_EXE)),
        arguments=escape(arguments),
        workdir=escape(str(APP_DIR)),
    )
    with tempfile.NamedTemporaryFile("w", suffix=".xml", encoding="utf-16", delete=False) as f:
        f.write(xml)
    try:
        subprocess.run(
            ["schtasks", "/Create", "/TN", name, "/XML", f.name, "/F"],
            check=True, capture_output=True, text=True, encoding="mbcs",
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"작업 스케줄러 등록 실패 ({name}): {(e.stderr or e.stdout).strip()}") from e
    finally:
        os.remove(f.name)


def main() -> None:
    print("=== SSAFY 자동 입퇴실 설치 ===\n")
    src_exe = exe_dir() / APP_EXE
    if not src_exe.exists():
        raise RuntimeError(f"{APP_EXE} 를 찾을 수 없습니다. install.exe와 같은 폴더에 두세요.")

    user, pw = ask_credentials()

    APP_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(["taskkill", "/IM", APP_EXE, "/F"], capture_output=True)
    shutil.copy2(src_exe, APP_DIR / APP_EXE)
    q = lambda s: '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    (APP_DIR / ".env").write_text(f"USERNAME={q(user)}\nPASSWORD={q(pw)}\n", encoding="utf-8")
    for f in APP_DIR.glob("last_success_*.txt"):
        f.unlink()
    print(f"- 설치 위치: {APP_DIR}")

    register_task(TASKS["in"], "SSAFY 자동 입실 (로그인 시)", LOGON_TRIGGER, "in", wake=False)
    print(f"- 입실 작업 등록: '{TASKS['in']}' (윈도우 로그인 30초 후)")
    register_task(TASKS["out"], "SSAFY 자동 퇴실 (평일 18:00)", WEEKDAY_18_TRIGGER, "out", wake=True)
    print(f"- 퇴실 작업 등록: '{TASKS['out']}' (평일 18:00)")

    if input("\n지금 바로 입실을 한 번 실행해 볼까요? (y/N): ").strip().lower() == "y":
        subprocess.run(["schtasks", "/Run", "/TN", TASKS["in"]], capture_output=True)
        print(f"- 실행했습니다. 결과는 {APP_DIR / 'autocheck.log'} 에서 확인할 수 있습니다.")

    print("\n설치가 끝났습니다. 자리를 옮기기 전에 uninstall.exe를 실행하세요.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[오류] {e}")
    input("\n엔터를 누르면 창이 닫힙니다...")
    sys.exit(0)
