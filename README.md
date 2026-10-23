# SSAFY 자동 입실 / 퇴실

[SSAFY 교육 사이트](https://edu.ssafy.com)의 **입실하기 / 퇴실하기** 버튼을 자동으로 눌러 주는 윈도우 프로그램입니다.
윈도우 **작업 스케줄러**에 등록되어 동작하며, 관리자 권한 없이 설치할 수 있습니다.

## 무엇을 해 주나요?

| 언제 | 하는 일 |
|---|---|
| **PC를 켜고 윈도우에 로그인하면** (30초 후) | Chrome을 열어 로그인 → **입실하기** 클릭 → "정상적으로 입실이 되었습니다" 팝업의 **확인** 클릭 |
| **평일(월~금) 18:00** | 로그인 → **퇴실하기** 클릭 → 팝업 **확인** 클릭 → 성공하면 **5초 뒤 PC 전원 종료** |

- 하루에 한 번만 처리합니다. 같은 날 재부팅해도 다시 입실하지 않습니다.
- 부팅 직후 인터넷이 아직 안 잡혔으면 최대 5분까지 기다리고, 실패하면 최대 3번까지 다시 시도합니다.
- 끝내 실패하면 **"직접 입실(퇴실)해 주세요"** 경고창을 띄웁니다.
- 입실이 끝나면 **새 버전이 있는지 확인해서 스스로 업데이트**합니다. ([자동 업데이트](#자동-업데이트) 참고)

## 준비물

- Windows 10 / 11
- **Google Chrome** 설치 (PC에 설치된 Chrome을 사용합니다)
- **Python 3.10 이상** — 직접 빌드할 때만 필요합니다. Releases에서 받으면 필요 없습니다.

## 사용 순서 한눈에 보기

```
1. 실행 파일 준비  (처음 한 번)          →  Releases에서 zip 받기  또는  직접 빌드
2. 설치하기        (자리마다)            →  install.exe
3. 삭제하기        (자리를 옮기기 전)    →  uninstall.exe
```

## 1. 실행 파일 준비 (처음 한 번)

### 방법 A. Releases에서 받기 (권장)

1. [Releases 페이지](https://github.com/seophohoho/autocheckinout/releases/latest)에서 `autocheck-vX.Y.Z.zip`을 받습니다.
2. 압축을 풉니다. 이 폴더가 아래 설명의 `dist` 폴더입니다.
3. [2. 설치하기](#2-설치하기)로 넘어갑니다.

### 방법 B. 직접 빌드하기

저장소에는 소스 코드만 있고 exe 파일(`dist` 폴더)은 없습니다. 아래 순서로 직접 만듭니다.
직접 빌드한 exe는 버전이 `0.0.0`이라, Release가 있으면 첫 부팅 때 최신 Release 버전으로 자동 업데이트됩니다.

#### B-1. Python 설치 (이미 있으면 건너뛰기)

1. https://www.python.org/downloads/ 에서 Python을 받아 설치합니다.
2. 설치 첫 화면에서 **"Add python.exe to PATH"를 반드시 체크**합니다.
3. 설치가 끝나면 명령 프롬프트(`Win + R` → `cmd`)에서 확인합니다.
   ```
   python --version
   ```
   `Python 3.12.x`처럼 나오면 성공입니다.

#### B-2. 저장소 받기

```
git clone https://github.com/seophohoho/autocheckinout.git
cd autocheckinout
```

git이 없다면 GitHub에서 **Code → Download ZIP**으로 받아 압축을 풀어도 됩니다.

#### B-3. 빌드

저장소 폴더의 **`build.bat`를 더블클릭**합니다. 명령 프롬프트에서 실행하려면 아래처럼 입력합니다.

```
build.bat
```

처음 실행하면 다음 일을 자동으로 합니다. 약 1~3분 걸립니다.

1. `.venv` 가상환경 생성
2. 필요한 패키지 설치 (`requirements.txt`)
3. exe 3개 빌드

`Build done: ...\dist`가 나오면 성공입니다. `dist` 폴더가 생기고 그 안에 아래 파일들이 들어 있습니다.

| 파일 | 설명 |
|---|---|
| `install.exe` | 설치 프로그램. 계정 정보를 저장하고 작업 스케줄러에 입실/퇴실 작업을 등록합니다. |
| `uninstall.exe` | 제거 프로그램. 작업 스케줄러 작업과 설치 폴더(계정 정보 포함)를 삭제합니다. |
| `autocheck.exe` | 실제로 입실/퇴실을 하는 프로그램. 설치하면 작업 스케줄러가 알아서 실행합니다. |
| `.env.example` | 계정 정보 파일 예시 (선택 사항) |
| `README.md` | 이 문서 |

이 `dist` 폴더만 있으면 **Python이 없는 PC에서도** 설치할 수 있습니다. 자리를 옮길 때는 `dist` 폴더만 챙기면 됩니다.

**빌드가 안 될 때**

| 메시지 | 해결 방법 |
|---|---|
| `Python not found` | Python을 설치하고 "Add python.exe to PATH"를 체크했는지 확인하세요. 설치 후에는 명령 프롬프트를 새로 여세요. |
| `pip install failed` | 인터넷 연결을 확인하세요. 회사/교육장 네트워크에서 막혔다면 다른 네트워크에서 시도하세요. |
| 백신이 exe를 삭제함 | PyInstaller로 만든 exe를 오진하는 경우가 있습니다. `dist` 폴더를 백신 예외로 등록하세요. |

## 2. 설치하기

1. `dist` 폴더를 PC의 아무 곳에나 둡니다. (예: 바탕화면)
2. `install.exe`를 더블클릭합니다.
3. SSAFY 아이디(이메일)와 비밀번호를 입력합니다. 비밀번호는 입력해도 화면에 보이지 않는 것이 정상입니다.
4. `지금 바로 입실을 한 번 실행해 볼까요? (y/N)`
   - `y` → 바로 Chrome이 열리며 입실을 시도합니다. 처음 설치할 때 정상 동작하는지 확인하기 좋습니다.
   - 그냥 엔터 → 다음 로그인부터 동작합니다.
5. "설치가 끝났습니다"가 나오면 엔터를 눌러 창을 닫습니다.

> **계정을 매번 입력하기 귀찮다면**: `.env.example`을 복사해 `.env`로 이름을 바꾸고 아래처럼 채워서 `install.exe` 옆에 두세요. 설치할 때 이 파일을 자동으로 사용합니다.
>
> ```
> USERNAME="아이디@example.com"
> PASSWORD="비밀번호"
> ```

> **"Windows의 PC 보호" 파란 창이 뜨면**: 서명되지 않은 exe라서 뜨는 경고입니다. **추가 정보 → 실행**을 누르세요.

## 3. 삭제하기 (자리 이동 전 필수)

1. `uninstall.exe`를 더블클릭합니다.
2. 작업 스케줄러 작업 2개와 설치 폴더(저장된 계정 정보, 로그 포함)가 삭제됩니다.
3. `uninstall.exe` 옆에 `.env`가 있으면 삭제할지 묻습니다. 다른 사람이 쓸 PC라면 `Y`(엔터)로 꼭 지우세요.
4. 마지막으로 `dist` 폴더도 필요 없다면 지웁니다.

## 자리를 옮길 때

```
[기존 자리]  uninstall.exe 실행  →  dist 폴더 챙기기 (USB, 메일 등)
[새 자리]    dist 폴더 복사      →  install.exe 실행
```

## ⚠️ 18시 자동 종료 주의사항

- 퇴실에 성공하면 **5초 뒤 PC가 강제로 꺼집니다. 저장하지 않은 작업은 사라집니다.** 18시 전에 꼭 저장하세요.
- **종료를 취소하려면** 종료 알림이 뜬 5초 안에 `Win + R` → `shutdown /a` 입력 → 엔터.
- **18시 이후에도 남아서 작업할 날**에는 미리 사이트에서 직접 퇴실하세요. "이미 퇴실" 상태면 PC를 끄지 않습니다.
- 퇴실에 실패했거나 "이미 퇴실" 상태일 때는 PC를 끄지 않습니다.
- 18시에 PC가 절전 상태면 깨워서 실행합니다. 로그아웃했거나 전원이 꺼져 있으면 실행되지 않습니다.
- PC를 껐다가 다음 날 아침에 켜도, 밀린 퇴실 작업이 실행되지 않도록 **평일 18:00 이후에만** 퇴실합니다.

## 자동 업데이트

PC를 켜서 **입실이 끝나면**, [GitHub Releases](https://github.com/seophohoho/autocheckinout/releases)에 새 버전이 있는지 확인합니다.

```
부팅 → 입실 처리 → 최신 Release 확인 → 새 버전이면 autocheck.exe 다운로드·교체 → 다음 실행부터 새 버전
```

- 입실을 먼저 처리하므로 업데이트 때문에 입실이 늦어지지 않습니다.
- 업데이트에 실패해도(인터넷 문제 등) 입실/퇴실에는 영향이 없고, 다음 부팅 때 다시 시도합니다.
- 업데이트되는 것은 `autocheck.exe`뿐입니다. 계정 정보(`.env`)와 작업 스케줄러 설정은 그대로 유지됩니다.

### 업데이트 확인하기

#### 1. 지금 설치된 버전 보기

`autocheck.log`의 **마지막 `autocheck vX.Y.Z 실행` 줄**이 현재 버전입니다.

- **메모장으로 보기**: `Win + R` → `%LOCALAPPDATA%\SsafyAutoCheckin\autocheck.log` 입력 → 엔터 → 맨 아래로 이동
- **명령어로 보기** (PowerShell):
  ```
  Get-Content "$env:LOCALAPPDATA\SsafyAutoCheckin\autocheck.log" -Encoding utf8 -Tail 5
  ```

```
[2026-10-24 08:31:02] autocheck v1.0.0 실행: in      ← 현재 버전 v1.0.0
```

> 업데이트는 **다음 실행부터** 적용됩니다. `업데이트 완료: v1.1.0`이 찍힌 직후에는 아직 `v1.0.0 실행`으로 보이고, 그다음 실행부터 `v1.1.0 실행`으로 바뀝니다.

#### 2. 최신 버전 보기

[Releases 페이지](https://github.com/seophohoho/autocheckinout/releases/latest) 맨 위의 태그(예: `v1.1.0`)가 최신 버전입니다. 1번의 버전과 같으면 최신 상태입니다.

#### 3. 지금 바로 업데이트하기

부팅을 기다리지 않고 바로 확인/업데이트하려면 명령 프롬프트(`Win + R` → `cmd`)에서 실행합니다.

```
%LOCALAPPDATA%\SsafyAutoCheckin\autocheck.exe update
```

창 없이 몇 초 만에 끝납니다. 결과는 `autocheck.log` 맨 아래에 남습니다.

| 로그 메시지 | 뜻 |
|---|---|
| `업데이트: 최신 버전 사용 중 (v1.0.0)` | 이미 최신 버전입니다. |
| `업데이트: v1.0.0 → v1.1.0 다운로드 중` → `업데이트 완료: v1.1.0` | 새 버전으로 교체했습니다. 다음 실행부터 적용됩니다. |
| `업데이트: 아직 배포된 릴리스가 없음` | 저장소에 Release가 하나도 없습니다. |
| `업데이트 실패 (다음 부팅 때 다시 시도): ...` | 인터넷 문제 등으로 실패했습니다. 입실/퇴실에는 영향이 없습니다. |
| `업데이트 확인 건너뜀 (설치 폴더의 exe로 실행한 경우에만 업데이트)` | `dist` 폴더 등 설치 폴더가 아닌 곳의 exe를 실행했습니다. 위 명령처럼 설치 폴더의 exe를 실행하세요. |

> **로그에 버전 줄(`autocheck vX.Y.Z 실행`)이 아예 없다면** 업데이트 기능이 없는 예전 버전이 설치된 것입니다. 이 경우 [Releases](https://github.com/seophohoho/autocheckinout/releases/latest)에서 zip을 받아 `install.exe`를 한 번 다시 실행하세요. 그 뒤로는 자동으로 업데이트됩니다.

## 잘 되었는지 확인하기

설치 폴더: `%LOCALAPPDATA%\SsafyAutoCheckin`
(`Win + R` → 위 경로 붙여넣기 → 엔터)

| 파일 | 내용 |
|---|---|
| `autocheck.log` | 실행 기록. 언제 로그인했고, 팝업 메시지가 무엇이었는지 남습니다. |
| `error_날짜_시간.png` | 실패했을 때의 브라우저 화면 캡처 |
| `last_success_in.txt` / `last_success_out.txt` | 마지막으로 입실/퇴실에 성공한 날짜 |
| `.env` | 저장된 계정 정보 (평문) |

작업 스케줄러에서 확인하려면 `Win + R` → `taskschd.msc` → **작업 스케줄러 라이브러리**에서
`SSAFY_AutoCheckin`(입실), `SSAFY_AutoCheckout`(퇴실)을 찾으면 됩니다.

## 이럴 땐 이렇게

| 상황 | 방법 |
|---|---|
| 비밀번호를 바꿨다 | `install.exe`를 다시 실행하면 새 계정 정보로 덮어씁니다. |
| 오늘만 퇴실/종료를 안 하고 싶다 | 미리 직접 퇴실하거나, 작업 스케줄러에서 `SSAFY_AutoCheckout` 우클릭 → **사용 안 함** (다음 날 다시 **사용**으로) |
| 공휴일 | 공휴일은 구분하지 못합니다. 평일 공휴일에 PC가 켜져 있으면 18시에 퇴실을 시도합니다. |
| 경고창이 떴다 | 사이트에서 직접 입실/퇴실한 뒤, `autocheck.log`와 `error_*.png`를 확인하세요. |
| 사이트 화면이 바뀌어서 동작하지 않는다 | 버튼 위치가 바뀌었을 수 있습니다. 아래 "코드 수정하기"를 참고하세요. |
| 새 버전이 나왔다 | 다음 부팅 때 자동으로 업데이트됩니다. 바로 받으려면 `autocheck.exe update`를 실행하세요. |
| 직접 코드를 고쳤다 | `build.bat`로 다시 빌드한 뒤 `install.exe`를 다시 실행하세요. |

### 직접 실행하기 (테스트용)

명령 프롬프트에서 설치 폴더의 `autocheck.exe`를 실행합니다.

```
cd %LOCALAPPDATA%\SsafyAutoCheckin
autocheck.exe in                         입실
autocheck.exe out                        퇴실 (평일 18시 이후에만, 성공 시 PC 종료)
autocheck.exe in --force                 오늘 이미 성공했어도 다시 실행
autocheck.exe out --force --no-shutdown  퇴실하되 PC는 끄지 않음
autocheck.exe update                     새 버전 확인/업데이트만
```

## 보안 안내

- 계정 정보는 `%LOCALAPPDATA%\SsafyAutoCheckin\.env`에 **평문**으로 저장됩니다. 해당 윈도우 계정으로 로그인한 사람은 누구나 볼 수 있습니다.
- 공용 PC이거나 자리를 떠날 때는 반드시 `uninstall.exe`를 실행하세요.
- 자동 업데이트는 이 저장소의 Release를 그대로 받아 실행합니다. **저장소에 태그를 push할 수 있는 사람이 곧 모든 설치 PC에서 실행될 코드를 정할 수 있다**는 뜻이므로, 저장소 쓰기 권한을 함부로 주지 마세요.

---

## 코드 수정하기 (개발자용)

Python + [Playwright](https://playwright.dev/python/)(설치된 Chrome 사용) + PyInstaller로 만들었습니다.

| 파일 | 설명 |
|---|---|
| `autocheck.py` | 입실/퇴실 자동화 (`in` / `out` / `update`) |
| `updater.py` | GitHub Releases에서 새 `autocheck.exe`를 받아 자기 자신을 교체 |
| `install.py` | 설치, 작업 스케줄러 등록 |
| `uninstall.py` | 제거 |
| `common.py` | 공통 설정 (버전, 저장소, 설치 경로, 작업 이름) |
| `requirements.txt` | 필요한 패키지 (버전 고정) |
| `build.ps1` | 가상환경 준비 + exe 3개를 `dist\`에 빌드 |
| `build.bat` | `build.ps1`을 더블클릭으로 실행하기 위한 파일 |
| `.github/workflows/release.yml` | 태그 push 시 exe를 빌드해 GitHub Release에 올림 |

### 새 버전 배포하기

코드를 고쳐 `main`에 push한 뒤, **`v`로 시작하는 태그**를 push하면 됩니다.

```
git tag v1.1.0
git push origin v1.1.0
```

1. GitHub Actions가 Windows에서 exe를 빌드합니다. 이때 `common.py`의 `VERSION`에 태그 버전(`1.1.0`)을 넣습니다.
2. [Releases](https://github.com/seophohoho/autocheckinout/releases)에 `autocheck.exe`와 `autocheck-v1.1.0.zip`이 올라갑니다. 진행 상황은 저장소의 **Actions** 탭에서 볼 수 있습니다.
3. 설치된 PC들은 다음 부팅 때 자동으로 새 버전을 받습니다.

버전은 항상 이전보다 크게 올리세요. (`1.0.0` → `1.0.1` → `1.1.0`, 숫자로 비교합니다)

> 자동 업데이트는 `autocheck.exe`만 교체합니다. `install.py`의 작업 스케줄러 설정(실행 시각 등)을 바꿨다면, 각 PC에서 새 버전의 `install.exe`를 다시 실행해야 적용됩니다.

빌드하지 않고 소스로 바로 테스트하려면 다음처럼 실행합니다. 저장소 폴더에 `.env`가 있어야 합니다.

```
.venv\Scripts\python.exe autocheck.py in --force
```

사이트의 버튼 위치가 바뀌면 `autocheck.py`의 selector를 고친 뒤 다시 빌드하세요.

| 대상 | selector |
|---|---|
| 아이디 / 비밀번호 입력칸 | `#userId` / `#userPwd` |
| 로그인 버튼 | `.form-btn` 안의 "로그인" |
| 입실 / 퇴실 버튼 | `#checkIn` / `#checkOut` (없으면 `.btns` 안의 "입실하기" / "퇴실하기" 글자) |
| 결과 팝업 | `#layerPopup` 안의 "확인" |

실행 시각을 바꾸려면 `install.py`의 `PT30S`(로그인 후 대기)와 `T18:00:00`(퇴실 시각), `autocheck.py`의 `CHECKOUT_FROM`을 함께 고치세요.
