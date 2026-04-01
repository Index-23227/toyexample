"""Step 4 Part C 테스트: Flask 웹 대시보드"""
import sqlite3
from flask import Flask, render_template_string

app = Flask(__name__)
DB_PATH = "data/sales.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>법인별 매출 현황</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; max-width: 900px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        th { background: #2c3e50; color: white; padding: 12px 16px; text-align: left; }
        td { padding: 10px 16px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f0f7ff; }
        .number { text-align: right; font-variant-numeric: tabular-nums; }
        a { color: #2980b9; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .total-row { font-weight: bold; background: #ecf0f1; }
        canvas { max-width: 900px; margin: 20px 0; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>법인별 매출 현황 대시보드</h1>
    <canvas id="chart" height="80"></canvas>
    <table>
        <tr>
            <th>법인명</th><th>통화</th>
            <th class="number">외화 합계</th>
            <th class="number">환율</th>
            <th class="number">원화 환산</th>
        </tr>
        {% set total_krw = namespace(v=0) %}
        {% for r in rows %}
        <tr>
            <td><a href="/detail/{{ r.corp_code }}">{{ r.corp_name }}</a></td>
            <td>{{ r.currency }}</td>
            <td class="number">{{ "{:,.0f}".format(r.foreign_total) }}</td>
            <td class="number">{{ "{:,.1f}".format(r.rate) }}</td>
            <td class="number">{{ "{:,.0f}".format(r.krw_total) }}원</td>
        </tr>
        {% set total_krw.v = total_krw.v + r.krw_total %}
        {% endfor %}
        <tr class="total-row">
            <td colspan="4">합계</td>
            <td class="number">{{ "{:,.0f}".format(total_krw.v) }}원</td>
        </tr>
    </table>

    <script>
        new Chart(document.getElementById('chart'), {
            type: 'bar',
            data: {
                labels: {{ labels | tojson }},
                datasets: [{
                    label: '원화 환산 매출 (원)',
                    data: {{ values | tojson }},
                    backgroundColor: ['#3498db','#2ecc71','#e74c3c','#f39c12','#9b59b6']
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { y: { ticks: { callback: v => (v/100000000).toFixed(1) + '억' } } }
            }
        });
    </script>
</body>
</html>
"""

DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ corp_name }} 상세</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        table { border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        th { background: #2c3e50; color: white; padding: 12px 16px; text-align: left; }
        td { padding: 10px 16px; border-bottom: 1px solid #eee; }
        .number { text-align: right; }
        a { color: #2980b9; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/">&larr; 목록으로</a>
    <h1>{{ corp_name }} — 월별 매출</h1>
    <table>
        <tr><th>월</th><th class="number">금액</th><th>비고</th></tr>
        {% for r in rows %}
        <tr>
            <td>{{ r.month }}</td>
            <td class="number">{{ "{:,.0f}".format(r.amount) }}</td>
            <td>{{ r.note or '' }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


@app.route("/")
def index():
    conn = get_db()
    rows = conn.execute("""
        SELECT c.corp_code, c.corp_name, c.currency,
               SUM(s.amount) AS foreign_total,
               e.rate,
               CAST(SUM(s.amount) * e.rate AS INTEGER) AS krw_total
        FROM monthly_sales s
        JOIN corporations c ON s.corp_code = c.corp_code
        JOIN exchange_rates e ON c.currency = e.currency
        GROUP BY c.corp_code
        ORDER BY krw_total DESC
    """).fetchall()
    conn.close()

    labels = [r["corp_name"] for r in rows]
    values = [r["krw_total"] for r in rows]
    return render_template_string(INDEX_HTML, rows=rows, labels=labels, values=values)


@app.route("/detail/<corp_code>")
def detail(corp_code):
    conn = get_db()
    corp = conn.execute(
        "SELECT corp_name FROM corporations WHERE corp_code = ?", (corp_code,)
    ).fetchone()
    rows = conn.execute(
        "SELECT month, amount, note FROM monthly_sales WHERE corp_code = ? ORDER BY month",
        (corp_code,),
    ).fetchall()
    conn.close()
    return render_template_string(DETAIL_HTML, corp_name=corp["corp_name"], rows=rows)


if __name__ == "__main__":
    print("브라우저에서 http://127.0.0.1:5000 을 열어보세요!")
    print("종료: Ctrl + C")
    app.run(debug=False, port=5000)
