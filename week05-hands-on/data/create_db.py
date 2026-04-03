"""
5주차 실습용 — SQLite 더미 DB 생성
실행: python data/create_db.py
MySQL 없어도 됩니다. SQLite는 Python에 기본 내장되어 있습니다.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sales.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ============================================================
# 테이블 1: 법인 마스터
# ============================================================
cur.execute("DROP TABLE IF EXISTS corporations")
cur.execute("""
CREATE TABLE corporations (
    corp_code TEXT PRIMARY KEY,
    corp_name TEXT NOT NULL,
    country   TEXT NOT NULL,
    currency  TEXT NOT NULL
)
""")

corps = [
    ("US01", "미국법인", "미국", "USD"),
    ("JP01", "일본법인", "일본", "JPY"),
    ("CN01", "중국법인", "중국", "CNY"),
    ("DE01", "독일법인", "독일", "EUR"),
    ("VN01", "베트남법인", "베트남", "VND"),
]
cur.executemany("INSERT INTO corporations VALUES (?,?,?,?)", corps)

# ============================================================
# 테이블 2: 월별 매출
# ============================================================
cur.execute("DROP TABLE IF EXISTS monthly_sales")
cur.execute("""
CREATE TABLE monthly_sales (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    corp_code TEXT NOT NULL,
    month     TEXT NOT NULL,
    amount    REAL NOT NULL,
    note      TEXT DEFAULT '',
    FOREIGN KEY (corp_code) REFERENCES corporations(corp_code)
)
""")

sales = [
    # 미국
    ("US01", "2026-01", 125000, ""),
    ("US01", "2026-02", 132000, "신규 거래처"),
    ("US01", "2026-03", 118000, ""),
    # 일본
    ("JP01", "2026-01", 15800000, ""),
    ("JP01", "2026-02", 16200000, ""),
    ("JP01", "2026-03", 14900000, "시즌 영향"),
    # 중국
    ("CN01", "2026-01", 890000, "춘절 영향"),
    ("CN01", "2026-02", 920000, ""),
    ("CN01", "2026-03", 875000, ""),
    # 독일
    ("DE01", "2026-01", 98000, ""),
    ("DE01", "2026-02", 105000, ""),
    ("DE01", "2026-03", 101000, ""),
    # 베트남
    ("VN01", "2026-01", 3250000000, ""),
    ("VN01", "2026-02", 3480000000, "대형 프로젝트"),
    ("VN01", "2026-03", 3120000000, ""),
]

cur.executemany(
    "INSERT INTO monthly_sales (corp_code, month, amount, note) VALUES (?,?,?,?)",
    sales,
)

# ============================================================
# 테이블 3: 환율
# ============================================================
cur.execute("DROP TABLE IF EXISTS exchange_rates")
cur.execute("""
CREATE TABLE exchange_rates (
    currency  TEXT NOT NULL,
    rate_date TEXT NOT NULL,
    rate      REAL NOT NULL,
    PRIMARY KEY (currency, rate_date)
)
""")

rates = [
    ("USD", "2026-03-31", 1350.0),
    ("JPY", "2026-03-31", 9.2),
    ("CNY", "2026-03-31", 186.0),
    ("EUR", "2026-03-31", 1480.0),
    ("VND", "2026-03-31", 0.056),
]
cur.executemany("INSERT INTO exchange_rates VALUES (?,?,?)", rates)

conn.commit()
conn.close()

print(f"DB 생성 완료: {DB_PATH}")
print("  - corporations (법인 마스터) : 5건")
print("  - monthly_sales (월별 매출)  : 15건")
print("  - exchange_rates (환율)      : 5건")
