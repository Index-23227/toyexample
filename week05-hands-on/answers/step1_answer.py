"""
Step 1 정답: DB 조회 → 터미널 출력
법인별 매출 합계 + 원화 환산
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sales.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 법인별 매출 합계 + 환율 + 원화 환산
cur.execute("""
    SELECT c.corp_name,
           c.currency,
           SUM(s.amount)            AS total,
           e.rate,
           ROUND(SUM(s.amount) * e.rate) AS krw_total
    FROM   monthly_sales s
    JOIN   corporations c  ON s.corp_code = c.corp_code
    JOIN   exchange_rates e ON c.currency = e.currency
    WHERE  e.rate_date = '2026-03-31'
    GROUP  BY c.corp_name
    ORDER  BY c.corp_name
""")

rows = cur.fetchall()
conn.close()

# 터미널 출력
print(f"{'법인명':<10} {'통화':<6} {'외화합계':>18} {'환율':>10} {'원화환산':>18}")
print("-" * 70)
for name, currency, total, rate, krw in rows:
    print(f"{name:<10} {currency:<6} {total:>18,.0f} {rate:>10} {krw:>18,.0f}")
