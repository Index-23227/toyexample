# Week 05 — Excel에서 웹으로: DB + Flask 대시보드

> AI에게 시켜서 DB 조회 → 웹 대시보드까지 만들어봅니다.
> SQL도 Flask도 직접 쓸 필요 없습니다. CLAUDE.md에 요구사항을 적고, 한국어로 지시하세요.

## 사전 준비

```bash
python -m pip install flask openpyxl
python data/create_db.py
```

## 실습 순서

| Step | 내용 | 시간 | 수강생이 하는 것 |
|------|------|------|-----------------|
| **Step 0** | [DB 개념 이해](exercises/step0-db-concept.md) | 20분 | 슬라이드 듣기 + Excel vs DB 비교 체험 |
| **Step 1** | [AI로 DB 조회하기](exercises/step1-db-query.md) | 20분 | CLAUDE.md에 DB 정보 추가 → 자연어로 조회 지시 |
| ☕ | 쉬는 시간 | 10분 | |
| **Step 2** | [Flask 대시보드 만들기](exercises/step2-flask-dashboard.md) | 25분 | "웹으로 보여줘" 지시 → 브라우저에서 확인 |
| **Step 3** | [기능 확장 + 자유 실습](exercises/step3-extend-and-explore.md) | 25분 | 차트, 필터, 스타일 등 원하는 기능 추가 |
| ☕ | 쉬는 시간 | 10분 | |
| **자유** | 내가 보고 싶은 화면 만들기 | 20분 | 자유롭게 요구사항 추가 |
| **정리** | 오늘 배운 것 + 다음 시간 예고 | 10분 | |

## 핵심 파일

| 파일 | 용도 |
|------|------|
| `CLAUDE.md` | 하네스 — DB 스키마, Flask 요구사항 정의 |
| `data/sales.db` | SQLite 데이터베이스 |
| `app.py` | Flask 웹 앱 (AI가 생성) |
| `templates/` | HTML 템플릿 (AI가 생성) |
