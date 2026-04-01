"""Step 2 테스트: 경비내역.xlsx를 부서별/항목별로 정리"""
import openpyxl
from collections import defaultdict

# 경비내역.xlsx 읽기
wb = openpyxl.load_workbook("data/경비내역.xlsx")
ws = wb.active

# 헤더 확인
headers = [cell.value for cell in ws[1]]
print(f"컬럼: {headers}")

# 데이터 읽기
rows = []
for row in ws.iter_rows(min_row=2, values_only=True):
    rows.append(dict(zip(headers, row)))

print(f"총 {len(rows)}건 읽음\n")

# 부서별 합계
dept_totals = defaultdict(float)
for r in rows:
    dept_totals[r["부서"]] += r["금액"]

print("=== 부서별 경비 합계 ===")
for dept, total in sorted(dept_totals.items()):
    print(f"  {dept}: {total:,.0f}원")

# 항목별 합계
item_totals = defaultdict(float)
for r in rows:
    item_totals[r["항목"]] += r["금액"]

print("\n=== 항목별 경비 합계 ===")
for item, total in sorted(item_totals.items()):
    print(f"  {item}: {total:,.0f}원")

# 개인카드 건수
personal = [r for r in rows if r["결제방법"] == "개인카드"]
personal_total = sum(r["금액"] for r in personal)
print(f"\n=== 개인카드 사용 ===")
print(f"  건수: {len(personal)}건")
print(f"  금액: {personal_total:,.0f}원")

# 결과를 엑셀로 저장
out_wb = openpyxl.Workbook()

# 시트1: 부서별 합계
ws1 = out_wb.active
ws1.title = "부서별합계"
ws1.append(["부서", "합계금액"])
for dept, total in sorted(dept_totals.items()):
    ws1.append([dept, total])

# 시트2: 항목별 합계
ws2 = out_wb.create_sheet("항목별합계")
ws2.append(["항목", "합계금액"])
for item, total in sorted(item_totals.items()):
    ws2.append([item, total])

# 시트3: 개인카드
ws3 = out_wb.create_sheet("개인카드")
ws3.append(["일자", "부서", "항목", "금액"])
for r in personal:
    ws3.append([r["일자"], r["부서"], r["항목"], r["금액"]])

out_wb.save("data/경비정리결과.xlsx")
print("\n결과 저장: data/경비정리결과.xlsx")
