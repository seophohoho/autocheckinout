"""SSAFY 자동 입실/퇴실. 작업 스케줄러가 실행한다.

사용: autocheck.exe in|out|update [--force]
  in   : 입실하기 (윈도우 로그인 시), 끝나면 새 버전 확인/업데이트
  out  : 퇴실하기 (평일 18:00), 성공하면 5초 뒤 PC 종료
  update : 새 버전 확인/업데이트만
  --force : 오늘 이미 성공했어도 다시 실행
  --no-shutdown : 퇴실 후 PC를 끄지 않음
"""
import ctypes
import datetime
import subprocess
import sys
import time
import traceback

from dotenv import dotenv_values
from playwright.sync_api import Error as PWError
from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

import updater
from common import VERSION, exe_dir

LOGIN_URL = "https://edu.ssafy.com/comm/login/SecurityLoginForm.do"
NETWORK_WAIT_SEC = 300  # 부팅 직후 네트워크가 잡힐 때까지 최대 대기
MAX_ATTEMPTS = 3
CHECKOUT_FROM = datetime.time(18, 0)
SHUTDOWN_DELAY_SEC = 5

MODES = {
    "in": {"label": "입실", "button": "입실하기", "selector": "#checkIn"},
    "out": {"label": "퇴실", "button": "퇴실하기", "selector": "#checkOut"},
}

BASE = exe_dir()
LOG_FILE = BASE / "autocheck.log"


def log(msg: str) -> None:
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    if sys.stdout:
        print(line)


def alert(msg: str) -> None:
    MB_ICONWARNING, MB_TOPMOST = 0x30, 0x40000
    ctypes.windll.user32.MessageBoxW(None, msg, "SSAFY 자동 입퇴실", MB_ICONWARNING | MB_TOPMOST)


def load_credentials() -> tuple[str, str]:
    # os.environ에 넣지 않고 파일에서 직접 읽는다 (윈도우 기본 USERNAME 환경변수와 충돌 방지)
    env = dotenv_values(BASE / ".env")
    user, pw = env.get("USERNAME"), env.get("PASSWORD")
    if not user or not pw:
        raise RuntimeError(f".env에 USERNAME / PASSWORD가 없습니다: {BASE / '.env'}")
    return user, pw


def open_login_page(page) -> None:
    deadline = time.time() + NETWORK_WAIT_SEC
    while True:
        try:
            page.goto(LOGIN_URL, timeout=20_000)
            page.wait_for_selector("#userId", timeout=20_000)
            return
        except PWError as e:
            if time.time() > deadline:
                raise
            log(f"접속 대기 중 (네트워크 미연결?): {e.message.splitlines()[0]}")
            time.sleep(10)


def click(locator) -> None:
    try:
        locator.click(timeout=5_000)
    except PWTimeout:
        # 공지 팝업 등이 가리고 있으면 DOM에서 직접 클릭
        locator.evaluate("el => el.click()")


def is_done(message: str) -> bool:
    return "정상" in message or "이미" in message or "완료" in message


def confirm_popups(page) -> str:
    """사이트 팝업의 '확인'을 누른다. '퇴실하시겠습니까?' 같은 확인창이 먼저 뜰 수 있어 최대 3번."""
    popup = page.locator("#layerPopup")
    message = ""
    for i in range(3):
        ok = popup.get_by_text("확인", exact=True).first
        try:
            ok.wait_for(state="visible", timeout=15_000 if i == 0 else 5_000)
        except PWTimeout:
            if i > 0:
                break
            ok = page.get_by_text("확인", exact=True).locator("visible=true").first
            ok.wait_for(state="visible", timeout=5_000)
        message = popup.inner_text().strip() or "(메시지 없음)"
        log(f"팝업 메시지: {message}")
        click(ok)
        try:
            ok.wait_for(state="hidden", timeout=5_000)
        except PWTimeout:
            pass
        if is_done(message):
            break
    return message


def run_once(mode: dict, user: str, pw: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False, args=["--start-maximized"])
        page = browser.new_context(no_viewport=True).new_page()
        page.on("dialog", lambda d: (log(f"브라우저 알림: {d.message}"), d.accept()))
        try:
            log("로그인 페이지 접속")
            open_login_page(page)

            page.fill("#userId", user)
            page.fill("#userPwd", pw)
            click(page.locator(".form-btn").get_by_text("로그인", exact=True).first)
            page.wait_for_url("**/edu/main/**", timeout=30_000)
            log("로그인 성공")

            button = page.locator(mode["selector"]).or_(
                page.locator(".btns").get_by_text(mode["button"], exact=True)
            ).first
            button.wait_for(state="visible", timeout=30_000)
            click(button)
            log(f"'{mode['button']}' 클릭")

            message = confirm_popups(page)
            time.sleep(2)
            return message
        except Exception:
            shot = BASE / f"error_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
            try:
                page.screenshot(path=str(shot))
                log(f"오류 화면 저장: {shot}")
            except Exception:
                pass
            raise
        finally:
            browser.close()


def run_mode(key: str) -> int:
    mode = MODES[key]
    label = mode["label"]

    now = datetime.datetime.now()
    if key == "out" and (now.weekday() >= 5 or now.time() < CHECKOUT_FROM):
        # 18시에 PC가 꺼져 있어 다음 날 아침에 밀려 실행되는 경우 등을 막는다
        log(f"[퇴실] 평일 {CHECKOUT_FROM:%H:%M} 이후가 아니라서 건너뜀")
        return 0

    done_file = BASE / f"last_success_{key}.txt"
    today = now.date().isoformat()
    if "--force" not in sys.argv and done_file.exists() and done_file.read_text().strip() == today:
        log(f"[{label}] 오늘 이미 처리됨 - 건너뜀")
        return 0

    try:
        user, pw = load_credentials()
    except Exception as e:
        log(str(e))
        alert(f"자동 {label} 실패: {e}")
        return 1

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            log(f"=== 자동 {label} 시작 (시도 {attempt}/{MAX_ATTEMPTS}) ===")
            message = run_once(mode, user, pw)
            if is_done(message):
                done_file.write_text(today)
                log(f"{label} 완료")
                # 이번 실행에서 퇴실한 경우에만 종료 ('이미 퇴실' = 수동 퇴실 후 작업 중일 수 있음)
                if key == "out" and "이미" not in message and "--no-shutdown" not in sys.argv:
                    log(f"{SHUTDOWN_DELAY_SEC}초 뒤 PC 종료")
                    subprocess.run([
                        "shutdown", "/s", "/t", str(SHUTDOWN_DELAY_SEC),
                        "/c", "SSAFY 자동 퇴실 완료 - PC를 종료합니다. (취소: shutdown /a)",
                    ])
            else:
                log("예상과 다른 메시지 - 직접 확인 필요")
                alert(f"{label} 결과를 확인하세요:\n\n{message}")
            return 0
        except Exception:
            log("실패:\n" + traceback.format_exc())
            if attempt < MAX_ATTEMPTS:
                time.sleep(20)

    alert(f"자동 {label}에 실패했습니다. 직접 {label}해 주세요.\n\n로그: {LOG_FILE}")
    return 1


def update() -> None:
    try:
        updater.self_update(log)
    except Exception as e:
        log(f"업데이트 실패 (다음 부팅 때 다시 시도): {e!r}")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or args[0] not in (*MODES, "update"):
        log(f"잘못된 인자: {sys.argv[1:]} (사용: autocheck.exe in|out|update)")
        return 2
    key = args[0]
    updater.cleanup()
    log(f"autocheck v{VERSION} 실행: {key}")

    if key == "update":
        update()
        return 0

    rc = run_mode(key)
    if key == "in":
        # 입실을 먼저 끝낸 뒤 업데이트한다 (새 버전은 다음 실행부터 적용)
        update()
    return rc


if __name__ == "__main__":
    sys.exit(main())
