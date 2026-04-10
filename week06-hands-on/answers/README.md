# 정답 스크립트

> 실습에서 AI가 생성해야 할 코드의 참고 정답입니다.
> 수강생에게 직접 보여주지 마세요. AI가 만들어주지 못할 때 강사용으로 사용합니다.

| 파일 | 대응 Step | 내용 |
|------|-----------|------|
| `import_sales_answer.py` | Step 1 | Excel 8개 → monthly_sales UPSERT (멱등) |
| `fetch_rates_answer.py` | Step 2 | 한국수출입은행 API → exchange_rates UPSERT (함정 4종 + 8통화) |
| `run_pipeline_answer.py` | Step 3 | fetch + import을 함수로 import, 로그 append, 실패 시 flag 알림 |
| `register_task_answer.ps1.txt` | Step 4 | Windows 작업 스케줄러 등록 PowerShell |

## 사용법 (강사용)

코드 실행은 Claude가 담당합니다. 강사는 Claude에게 다음과 같이 지시하세요.

- **Step 1 검증**: "`answers/import_sales_answer.py`를 두 번 실행해서 멱등성 확인해줘."
- **Step 2 검증**: "`.env`에 인증키 설정하고 `answers/fetch_rates_answer.py`를 실행해줘."
- **Step 3 검증**: "`answers/run_pipeline_answer.py`를 돌리고 `logs/`에 생긴 파일을 보여줘."
- **Step 4 검증**: "`answers/register_task_answer.ps1.txt`의 내용을 보여줘. 실제 등록은 시연 PC에서만."

## 자립성 구조

정답 파일은 **`answers/` 폴더 안에서 자기완결적으로** 동작합니다:
- Python 파일들은 `os.path.dirname(__file__)` 기준 경로 사용 → 어느 CWD에서 돌려도 무방
- DB 경로: `answers/../../week05-hands-on/data/sales.db` (상위 참조)
- `.env`는 `answers/../.env` (week06-hands-on 루트)를 읽음

수강생이 루트에 만들 `import_sales.py` / `fetch_rates.py` / `run_pipeline.py`와
파일명이 달라서 충돌하지 않습니다.

## 주의 — 테스트 상태

- **`import_sales_answer.py`**: 8법인 × 6개월 = 48행 UPSERT 멱등성 검증 완료
- **`fetch_rates_answer.py`**: SSL 우회 적용, 8통화 폴백 검증 완료. 실제 API 호출은 강사가 공용 키로 사전 확인 필요
- **`run_pipeline_answer.py`**: 오케스트레이션·로그 append·실패 flag 생성·복구 시 flag 삭제 검증 완료
- **`register_task_answer.ps1.txt`**: PowerShell 파서 문법 검증 완료. 실제 등록은 시연 PC에서만
