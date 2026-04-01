# Step 4: (어드밴스) DB 연결 & Flask 웹 시각화

> Step 1~3을 끝내고 시간이 남거나, DB/웹에 관심 있는 분을 위한 확장 실습입니다.
> MySQL 없어도 됩니다 — SQLite(Python 내장)로 똑같이 체험할 수 있습니다.

---

## 이 실습에서 하는 것

```
[Part A] 엑셀 데이터 → DB에 넣기          "데이터를 DB로 관리하면 뭐가 좋은지"
    ↓
[Part B] DB에서 데이터 꺼내서 조회          "SQL로 원하는 데이터만 뽑기"
    ↓
[Part C] Flask 웹 페이지로 시각화          "브라우저에서 보는 대시보드 만들기"
```

---

## 사전 준비

### 필요한 패키지 설치

VSCode 터미널(`Ctrl + ~`)에서 실행:

```
python -m pip install flask openpyxl
```

### 더미 DB 생성

```
python data/create_dummy_db.py
```

→ `data/sales.db` 파일이 생깁니다 (SQLite 데이터베이스)

---

## Part A: DB란 뭔가? (5분 설명)

**엑셀 vs DB 비교:**

| | 엑셀 | DB (데이터베이스) |
|--|------|------------------|
| 파일 | .xlsx 파일 하나하나 | 하나의 DB에 테이블 여러 개 |
| 찾기 | Ctrl+F, 필터 | SQL 한 줄로 정확히 검색 |
| 합치기 | 복사-붙여넣기 | JOIN 한 줄 |
| 동시 접근 | 한 명만 편집 가능 | 여러 명 동시 가능 |
| 데이터 양 | 100만 행 한계 | 수억 행 OK |

**SQL = DB에게 시키는 명령어**
```sql
-- "미국법인 매출만 보여줘"
SELECT * FROM monthly_sales WHERE corp_code = 'US01';

-- "법인별 매출 합계 보여줘"
SELECT corp_code, SUM(amount) FROM monthly_sales GROUP BY corp_code;
```

**이번 실습의 DB 구조:**
```
sales.db
├── corporations    (법인 마스터: 법인코드, 법인명, 국가, 통화)
├── monthly_sales   (월별 매출: 법인코드, 월, 금액, 비고)
└── exchange_rates  (환율: 통화, 일자, 환율)
```

---

## Part B: AI에게 DB 조회 코드 시키기

### CLAUDE.md에 DB 정보 추가하기

Step 1에서 만든 CLAUDE.md에 아래 내용을 **추가**하세요:

```markdown
## DB 정보
- SQLite DB 파일: data/sales.db
- 테이블 목록:
  - corporations: corp_code(PK), corp_name, country, currency
  - monthly_sales: id(PK), corp_code(FK), month, amount, note
  - exchange_rates: currency(PK), rate_date(PK), rate
```

> **MySQL 쓰시는 분은** SQLite 대신 본인 MySQL 정보를 적으세요:
> ```markdown
> ## DB 정보
> - MySQL (localhost:3306)
> - DB명: (본인 DB명)
> - 테이블: (본인 테이블 목록)
> ```

### AI에게 시켜보기

```
data/sales.db (SQLite)에 연결해서
법인별 3개월 매출 합계를 조회하는 Python 코드를 만들어줘.

corporations 테이블과 JOIN해서 법인명도 같이 보여주고,
exchange_rates 테이블의 환율로 원화 환산 금액도 계산해줘.

결과를 표 형식으로 터미널에 출력해줘.
```

### 기대하는 결과 (대략 이런 모양)

```
법인명      통화    외화합계        환율      원화환산
미국법인    USD     375,000       1,350    506,250,000
일본법인    JPY     46,900,000    9.2      431,480,000
중국법인    CNY     2,685,000     186      499,410,000
...
```

---

## Part C: Flask 웹 페이지로 시각화

여기가 핵심입니다. 터미널 출력 대신 **브라우저에서 보는 대시보드**를 만듭니다.

### AI에게 시켜보기

```
data/sales.db에 연결해서 법인별 매출 현황을 보여주는
Flask 웹 앱을 만들어줘.

요구사항:
1. 메인 페이지(/)에 법인별 매출 합계 표를 보여줘
2. corporations와 monthly_sales를 JOIN해서 법인명으로 표시
3. exchange_rates 환율로 원화 환산 금액도 같이 보여줘
4. HTML 테이블에 간단한 CSS 스타일 적용 (보기 좋게)
5. 법인명을 클릭하면 해당 법인의 월별 상세 페이지로 이동

파일 구조:
- app.py (Flask 앱)
- templates/index.html (메인 페이지)
- templates/detail.html (법인별 상세 페이지)

조건:
- SQLite 사용 (data/sales.db)
- 한국어 주석
- 금액은 천 단위 콤마 표시
```

### 실행하기

AI가 만들어준 `app.py`를 저장하고 터미널에서:

```
python app.py
```

그러면 이런 메시지가 나옵니다:
```
 * Running on http://127.0.0.1:5000
```

**브라우저에서 http://127.0.0.1:5000 접속** → 매출 대시보드 확인!

종료할 때는 터미널에서 `Ctrl + C`

---

## (보너스) 차트까지 넣고 싶다면

```
위에서 만든 Flask 앱의 메인 페이지에
법인별 매출 합계를 막대 차트로 보여줘.

Chart.js를 CDN으로 불러와서 사용하고,
표 위에 차트를 배치해줘.
```

→ 외부 라이브러리 설치 없이 바로 차트가 나옵니다!

---

## MySQL 쓰시는 분을 위한 팁

SQLite 대신 MySQL로 바꾸는 것은 AI에게 시키면 됩니다:

```
위에서 만든 Flask 앱을 MySQL로 바꿔줘.
- 호스트: localhost
- 포트: 3306
- DB명: (본인 DB명)
- 사용자: (본인 계정)
- 비밀번호는 환경변수 DB_PASSWORD에서 읽어와
```

필요한 패키지: `python -m pip install pymysql` 또는 `python -m pip install mysql-connector-python`

> DBeaver에서 보던 테이블을 **웹 브라우저에서** 보는 것 — 이게 Flask의 핵심입니다.

---

## 에러가 나면?

| 에러 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: No module named 'flask'` | Flask 미설치 | `python -m pip install flask` |
| `OperationalError: no such table` | DB가 안 만들어짐 | `python data/create_dummy_db.py` 실행 |
| `Address already in use` | 이미 서버가 켜져있음 | 터미널에서 Ctrl+C 후 다시 실행 |
| 페이지가 안 열림 | 포트 문제 | `app.run(port=8080)` 으로 변경 시도 |

---

## 여기까지 하면 배운 것

1. **엑셀 → DB**: 데이터를 DB에 넣으면 SQL로 자유롭게 조회 가능
2. **Flask**: Python으로 웹 페이지를 만들 수 있다 (HTML 이미 해봤으니 친숙!)
3. **전체 흐름**: 데이터(DB) → 처리(Python) → 화면(Flask/HTML) = 하나의 앱
4. 이 모든 코드를 **AI가 만들어줬다** — 직접 짤 필요 없음
