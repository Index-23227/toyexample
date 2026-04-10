# CLAUDE.md — 재경팀 월마감 자동화 파이프라인

> week04에서 만든 법인 엑셀 + week05에서 만든 DB·대시보드를 **한 번의 실행**으로 갱신하는 파이프라인을 만든다.
> 수강생은 코드를 직접 쓰지 않는다. 이 문서에 요구사항이 적혀 있고, 자연어로 Claude에게 지시한다.

---

## 프로젝트 구조

```
week06-hands-on/
├── CLAUDE.md                ← 이 문서 (하네스)
├── README.md                ← 사전 준비
├── .env                     ← 환율 API 키 (week06-hands-on/ 루트, git 미포함)
├── .env.example             ← 환율 API 키 템플릿
├── data/
│   ├── incoming/            ← 매월 받는 법인 엑셀 8개 (week04에서 복사)
│   │   ├── 법인_US01_미국.xlsx
│   │   ├── 법인_JP01_일본.xlsx
│   │   ├── 법인_CN01_중국.xlsx
│   │   ├── 법인_DE01_독일.xlsx
│   │   ├── 법인_VN01_베트남.xlsx
│   │   ├── 법인_IN01_인도.xlsx
│   │   ├── 법인_GB01_영국.xlsx
│   │   └── 법인_TH01_태국.xlsx
│   └── (sales.db는 week05 것을 공유해서 씀 — 아래 "DB 위치" 참고)
├── logs/                    ← 파이프라인 실행 로그 (AI가 생성)
├── exercises/               ← 실습 안내
├── answers/                 ← 정답 스크립트 (강사 전용)
├── import_sales.py          ← Step 1 결과물 (AI가 루트에 생성)
├── fetch_rates.py           ← Step 2 결과물
└── run_pipeline.py          ← Step 3 결과물
```

---

## 라이브러리 규칙

**외부 패키지는 `openpyxl` 하나만 설치한다.** 나머지는 전부 Python 표준 라이브러리를 사용한다:
- HTTP 호출: `urllib.request` (NOT `requests`)
- JSON 파싱: `json`
- DB: `sqlite3`
- `.env` 읽기: 수동 파싱 (6~7줄짜리 함수, `python-dotenv` 사용 금지)

> 이유: 수강생 PC마다 `requests`/`urllib3` 버전 충돌이 발생할 수 있다. stdlib만 쓰면 `pip install` 실패와 무관하게 동작한다.

### SSL 주의 (한국수출입은행 API)

한국수출입은행 서버는 TLS 중간 인증서를 보내지 않는 경우가 있어 Python의 기본 인증서 검증이 실패할 수 있다. API 호출 시 다음 패턴을 사용한다:

```python
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with urlopen(req, context=ctx, timeout=10) as resp:
    ...
```

> 운영 환경에서는 회사 CA 번들을 사용해야 한다. 이 설정은 교육용이다.

---

## 이어쓰는 자산 (week04/week05)

이번 주는 **새로 만들지 않는다**. 이미 만들어 둔 것을 연결한다.

### week04에서 가져온 것 — 법인 엑셀
- 위치: `data/incoming/법인_{code}_{country}.xlsx` (8개)
- 포맷 (시트명 `Sheet`):

  | 월 | 계정과목 | 통화 | 금액 | 비고 |
  |----|----------|------|------|------|
  | `2026-01` | `매출액` | `USD` | `125000` | `신규 거래처` |

- **모든 행은 `매출액`이다.** 다른 계정과목은 없다. 별도 필터링 불필요.
- 파일명에서 **법인코드/법인명을 파싱**한다: `법인_{code}_{name}.xlsx`

### week05에서 가져온 것 — DB
- **경로**: `../week05-hands-on/data/sales.db` (상위 폴더 참조)
- 스키마는 week05 CLAUDE.md와 동일:
  - `corporations(corp_code PK, corp_name, country, currency)`
  - `monthly_sales(id PK, corp_code, month, amount, note)`
  - `exchange_rates(currency, rate_date, rate)` — 복합 PK
- **DB가 없으면 먼저 `../week05-hands-on/data/create_db.py`를 실행**해서 생성한다.

> 이렇게 함으로써 이번 주에 돌린 파이프라인 결과가 **지난주에 만든 대시보드(`week05-hands-on/app.py`)에 그대로 반영**된다. 이것이 week06의 보상 포인트.

---

## 파이프라인 전체 그림

```
[data/incoming/*.xlsx]           [한국수출입은행 API]
          │                               │
          ▼                               ▼
    import_sales.py              fetch_rates.py
          │                               │
          └─────────────┬─────────────────┘
                        ▼
              [sales.db 업데이트]
                        │
                        ▼
                [logs/YYYYMMDD.log]
                        │
                        ▼
          (week05 대시보드 새로고침 시 반영)
```

3개의 스크립트가 있고, `run_pipeline.py` 하나가 이들을 순서대로 실행한다. 마지막에 **Windows 작업 스케줄러**가 매일 `run_pipeline.py`를 자동으로 돌린다.

---

## Step 1: Excel → DB (`import_sales.py`)

### 입력
`data/incoming/` 폴더의 `법인_{code}_{name}.xlsx` 파일 8개.

### 동작
1. 폴더의 모든 `법인_*.xlsx`를 읽는다.
2. 파일명에서 법인코드 파싱.
3. 각 행의 `(corp_code, month, amount, note)`를 `monthly_sales` 테이블에 쓴다. (`계정과목`, `통화` 컬럼은 DB에 넣지 않는다 — 법인 마스터에 이미 있으므로.)
4. **멱등성 필수**: `(corp_code, month)` 조합이 이미 있으면 **기존 행을 덮어쓴다**. 새로 INSERT 하지 않는다.

### 멱등성 구현 규칙
- SQLite에서는 `INSERT ... ON CONFLICT(corp_code, month) DO UPDATE SET ...` 구문 사용.
- 이를 위해 `monthly_sales`에 **`(corp_code, month)` UNIQUE 인덱스가 필요**하다. 없으면 `CREATE UNIQUE INDEX IF NOT EXISTS ux_sales_corp_month ON monthly_sales(corp_code, month)`로 먼저 만든다.
- 수강생이 같은 명령을 두 번 돌려도 `monthly_sales` 행 수가 **그대로** 유지되어야 한다 (Step 1의 검증 포인트).

### 출력 로그
- 처리한 파일 수, 처리한 행 수(UPSERT), 건너뛴 수, `monthly_sales` 총 행 수를 터미널에 출력.
- 멱등성 시연은 카운트가 아니라 **"두 번 돌려도 총 행 수가 그대로다"**로 보여준다.

### 에러 처리
- 엑셀 컬럼 누락 시: 어떤 파일의 어떤 컬럼이 없는지 에러 메시지에 표시 후 중단.
- `corp_code`가 `corporations` 테이블에 없으면: 해당 행만 건너뛰고 경고 로그.

---

## Step 2: 환율 API → DB (`fetch_rates.py`)

### API 정보 — 한국수출입은행 오픈API

- **엔드포인트**: `https://www.koreaexim.go.kr/site/program/financial/exchangeJSON`
- **파라미터**:
  - `authkey` — 인증키 (환경변수 `KOREAEXIM_AUTHKEY`에서 읽는다)
  - `searchdate` — `YYYYMMDD` 형식, 조회 기준일
  - `data` — `AP01` (환율 조회 고정)
- **응답**: JSON 배열. 각 항목 주요 필드:
  - `result` — `1`이면 성공
  - `cur_unit` — 통화 코드 (아래 "현실 함정" 참조)
  - `cur_nm` — 통화명 (한국어)
  - `deal_bas_r` — **매매기준율** (원/해당 통화 1단위). 우리가 쓸 값.
- **HTTP 호출은 반드시 `urllib.request`를 사용**한다 (위 "라이브러리 규칙" 참조). SSL 컨텍스트도 위 규칙 따름.

### ⚠️ 현실 함정 — 반드시 이렇게 처리한다

이 API는 **우리가 원하는 형식으로 주지 않는다**. 아래 규칙을 반드시 적용한다.

#### 1. 통화 코드 매핑

| API가 주는 값 | 우리 DB에 저장할 값 | 금액 변환 |
|---|---|---|
| `USD` | `USD` | 그대로 |
| `JPY(100)` | `JPY` | **`deal_bas_r` ÷ 100** (100엔 기준 → 1엔 기준) |
| `CNH` | `CNY` | 그대로 (역외위안도 사실상 동일 환율) |
| `EUR` | `EUR` | 그대로 |
| `INR` | `INR` | 그대로 |
| `GBP` | `GBP` | 그대로 |
| `THB` | `THB` | 그대로 |

`deal_bas_r`는 문자열이고 **천 단위 콤마가 들어있다** (예: `"1,350.50"`). `float()` 전에 콤마 제거 필요.

#### 2. `VND`는 API가 제공하지 않는다

- 한국수출입은행 API에는 `VND`가 없다.
- **폴백 규칙**: `exchange_rates` 테이블에 `VND`의 **가장 최근 rate**를 재사용. 그 값으로 오늘 날짜 row를 새로 INSERT.
- 기존에도 `VND`가 없으면 **하드코딩 상수 `0.056`** 사용. 로그에 "`VND`: 폴백값 사용 (0.056)" 경고.

#### 3. 주말·공휴일은 빈 배열이 온다

- 응답이 `[]` 또는 `result != 1`인 경우 → 에러 아님, "환율 데이터 없음".
- **전영업일 환율을 재사용**: `exchange_rates`에서 가장 최근 `rate_date`의 값들을 오늘 날짜로 복사해 INSERT.
- 로그에 "YYYY-MM-DD: 영업일 아님, 직전 영업일 환율 재사용" 기록.

#### 4. 평일 오전 11시 이전은 아직 미게시

- 오전 11시 이전에 호출하면 빈 배열.
- 처리는 #3과 동일 (직전 영업일 재사용 + 로그).

### 입력
- `.env` 파일: **`week06-hands-on/.env`** (루트). 없으면 에러 메시지로 설정 안내 후 중단.
- `searchdate`: 기본값 = **오늘**.

### 출력
- `exchange_rates` 테이블에 `(currency, rate_date=오늘, rate)` 8건 upsert (USD/JPY/CNY/EUR/VND/INR/GBP/THB).
- 복합 PK `(currency, rate_date)`이므로 **같은 날 두 번 돌려도 갱신**되고 중복되지 않는다 (멱등성).
- 터미널에 통화별 환율 출력.

---

## Step 3: 파이프라인 오케스트레이션 (`run_pipeline.py`)

### 동작

1. `logs/YYYYMMDD.log` 파일을 append 모드로 연다 (없으면 생성).
2. 시작 시각 기록.
3. **Step A** — `fetch_rates.py`의 로직을 함수로 호출 → 성공/실패 로그.
4. **Step B** — `import_sales.py`의 로직을 함수로 호출 → 성공/실패 로그. **A가 실패해도 B는 진행한다** (두 단계는 데이터 의존이 없음 — 환율 테이블과 매출 테이블은 독립).
5. 종료 시각 + 총 소요시간 기록.
6. 한 단계라도 실패했으면 **exit code 1**, 전부 성공이면 **exit code 0**.

### 실패 시 알림 (모니터링)

7. **실패 시**: `data/failure_YYYYMMDD.flag` 파일을 생성한다. 이 파일이 존재하면 week05 대시보드에 빨간 배너가 뜬다. 바탕화면에도 `파이프라인_실패_YYYYMMDD.txt` 요약을 생성해 다음날 아침 눈에 들어오게 한다.
8. **성공 시**: 오늘자 failure flag가 있으면 삭제한다 (재실행으로 복구됨).

### 구조 힌트 (Claude에게 반드시 지시)

- `fetch_rates.py`, `import_sales.py`는 **모듈로 import 가능**하게 만든다. 즉, 각 파일에 `def main():` 함수가 있고 `if __name__ == "__main__": main()`로 감싼다.
- `run_pipeline.py`는 `from fetch_rates import main as fetch_main`, `from import_sales import main as import_main` 식으로 호출.
- 이유: subprocess로 호출하면 에러 메시지 전달이 불편하고, 수강생이 로그 구조를 이해하기도 어렵다.

### 로그 포맷 예시

```
===== 2026-04-09 09:00:12 파이프라인 시작 =====
[환율 갱신] 시작
[환율 갱신] USD=1,350.00  JPY=9.20  CNY=186.00  EUR=1,480.00  VND=0.056 (폴백값)  INR=16.00  GBP=1,720.00  THB=38.90
[환율 갱신] 완료 (1.2초)
[매출 import] 시작
[매출 import] 8개 파일 처리: UPSERT 48건, SKIP 0건 (monthly_sales 총 48행)
[매출 import] 완료 (0.3초)
===== 2026-04-09 09:00:13 파이프라인 완료 (1.5초) =====
```

---

## Step 4: Windows 작업 스케줄러 등록

### 등록 방법
PowerShell에서 `schtasks` 명령 또는 `Register-ScheduledTask` cmdlet 사용. 강사는 Claude에게 자연어로 지시하면 된다:

> "이 파이프라인을 매일 오전 11:30에 자동 실행되도록 Windows 작업 스케줄러에 등록하는 PowerShell 스크립트를 만들어줘. Task 이름은 `Week06Pipeline`."

### 규칙

- **실행 시각**: 매일 11:30 (한국수출입은행 환율 게시가 11:00 이후이므로 여유를 두고 11:30).
- **Task 이름**: `Week06Pipeline`
- **작업 내용**: `run_pipeline.py`를 프로젝트 루트(`week06-hands-on/`)에서 실행.
- **등록 스크립트**: `answers/register_task_answer.ps1.txt` 참고 (강사용). Gmail 보안 차단 방지를 위해 `.ps1.txt` 확장자. 사용 시 `.txt`를 제거.
- **수강생 PC에는 실제로 등록하지 않는다** — "등록 스크립트가 어떻게 생겼는지 보고, `taskschd.msc`로 내가 원할 때 수동으로 돌릴 수 있다"까지만 경험시킨다.

### 주의
- PowerShell 스크립트는 **절대경로를 사용**한다. 작업 스케줄러는 CWD가 `C:\Windows\System32`이므로 상대경로는 깨진다.
- 파이썬 실행 파일 경로도 절대경로로 지정 (`py.exe` 풀 경로 또는 `where.exe py`로 찾은 값).
- **관리자 권한 PowerShell**이 필요할 수 있다. 시작 메뉴 → `PowerShell` 검색 → 우클릭 → "관리자 권한으로 실행".

---

## 환경변수 / `.env` 파일

**위치: `week06-hands-on/.env` (프로젝트 루트)**

```
KOREAEXIM_AUTHKEY=발급받은_인증키
```

- 강의에서는 강사가 **공용 키**를 `.env.example`의 주석에 적어두고 복사해서 쓰게 한다.
- 수강 이후 본인이 직접 발급받으려면 `https://www.koreaexim.go.kr/` → 공개API 메뉴에서 신청.
- **`.env` 파일은 절대 git에 올리지 않는다.** `.gitignore`에 포함되어 있다.
- **Python에서 `.env` 읽기**: `python-dotenv` 설치가 번거로우므로 수동 파싱(간단한 6~7줄짜리 함수) 권장. Claude에게 "`python-dotenv` 없이 `.env` 읽어줘"라고 지시.

---

## 작업 시 반드시 지킬 것

1. **`import_sales.py`는 멱등**이어야 한다. 같은 파일을 두 번 넣어도 `monthly_sales` 행 수가 그대로.
2. **환율 통화 매핑 규칙을 정확히 지킨다**: `JPY(100)` → ÷100, `CNH` → `CNY`, `VND` → 폴백.
3. **주말/11시 이전/빈 응답은 에러가 아니다.** 직전 영업일 환율을 복사해 오늘 날짜 row를 만든다.
4. **DB 경로는 week05 공유**: `../week05-hands-on/data/sales.db`. DB가 없으면 week05의 `create_db.py`를 먼저 실행.
5. **로그는 `logs/YYYYMMDD.log`에 append**. 같은 날 여러 번 돌려도 덮어쓰지 않고 누적.
6. **`run_pipeline.py`는 `fetch_rates.py`, `import_sales.py`를 import해서 함수로 호출**한다. subprocess 금지.
7. **작업 스케줄러 등록은 강사만 실행**한다. 수강생 PC는 건드리지 않는다.
8. **`answers/` 폴더는 강사 전용**. 수강생 요청 이행 중에는 먼저 열거나 복사하지 않는다. 루트에 새 파일을 생성한다.
9. **Python 실행 명령**은 환경에 따라 `python`, `python3`, `py` 중 동작하는 것 (Windows는 보통 `py`).
10. **에러가 나면 AI에게 에러 메시지를 그대로 보여주고 고치게 한다**.
11. **외부 라이브러리는 `openpyxl`만**. HTTP는 `urllib.request`, JSON은 `json`, DB는 `sqlite3`. `requests` 사용 금지.
12. **실패 시 flag 파일 + 바탕화면 알림**으로 모니터링. 재실행 성공 시 flag 자동 삭제.
