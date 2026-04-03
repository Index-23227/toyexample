"""
Step 2 정답: Flask 웹 대시보드
메인 페이지 + 법인별 상세 페이지
"""
import sqlite3
import os
from flask import Flask, render_template

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sales.db")


def get_db():
    """DB 연결을 반환한다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.template_filter("comma")
def comma_filter(value):
    """금액에 천 단위 콤마를 붙인다."""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value


@app.route("/")
def index():
    """메인 페이지: 법인별 매출 합계 + 원화 환산"""
    conn = get_db()
    rows = conn.execute("""
        SELECT c.corp_code,
               c.corp_name,
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
    """).fetchall()
    conn.close()
    return render_template("index.html", rows=rows)


@app.route("/corp/<corp_code>")
def detail(corp_code):
    """법인별 상세 페이지: 월별 매출 내역"""
    conn = get_db()

    # 법인 정보
    corp = conn.execute(
        "SELECT * FROM corporations WHERE corp_code = ?", (corp_code,)
    ).fetchone()

    # 월별 매출
    sales = conn.execute("""
        SELECT month, amount, note
        FROM   monthly_sales
        WHERE  corp_code = ?
        ORDER  BY month
    """, (corp_code,)).fetchall()

    # 합계
    total = sum(row["amount"] for row in sales)

    conn.close()
    return render_template("detail.html", corp=corp, sales=sales, total=total)


if __name__ == "__main__":
    app.run(debug=True)
