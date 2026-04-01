"""Step 4 Part B 테스트: DB 조회 + 환율 환산"""
import sqlite3

conn = sqlite3.connect("data/sales.db")
cur = conn.cursor()

# 법인별 매출 합계 + 환율 환산
query = """
SELECT
    c.corp_name  AS 법인명,
    c.currency   AS 통화,
    SUM(s.amount) AS 외화합계,
    e.rate       AS 환율,
    CAST(SUM(s.amount) * e.rate AS INTEGER) AS 원화환산
FROM monthly_sales s
JOIN corporations c ON s.corp_code = c.corp_code
JOIN exchange_rates e ON c.currency = e.currency
GROUP BY c.corp_code
ORDER BY 원화환산 DESC
"""

cur.execute(query)
results = cur.fetchall()

print(f"{'법인명':<10} {'통화':<6} {'외화합계':>16} {'환율':>8} {'원화환산':>16}")
print("-" * 60)
for row in results:
    name, cur_code, total, rate, krw = row
    print(f"{name:<10} {cur_code:<6} {total:>16,.0f} {rate:>8,.1f} {krw:>16,.0f}")

conn.close()
print("\nDB 조회 성공!")
