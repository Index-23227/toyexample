# 4주차 실습: CLAUDE.md 만들고 바이브코딩 체험하기

> **날짜**: 2026년 4월 첫째 주
> **대상**: VSCode 설치 완료, AI 대화 해본 분들
> **목표**: CLAUDE.md를 직접 만들고, 그걸로 AI에게 코드를 시켜본다
> **소요시간**: 약 90분

---

## 오늘의 흐름

```
[준비] 폴더 열기 & 파일 확인          (10분)
  ↓
[Step 1] CLAUDE.md 만들기             (25분)  ← 같이 한 줄씩
  ↓
[Step 2] 만든 MD로 바이브코딩 체험    (30분)  ← AI한테 코드 시키기
  ↓
[Step 3] 여러 파일 합치기 체험        (20분)  ← 실전 느낌
  ↓
[정리] 비교 & 다음 과제               (5분)
  ↓
[Step 4] (어드밴스) DB + Flask 시각화  ← 빨리 끝난 분 / 도전하고 싶은 분
```

---

## 사전 준비

1. VSCode가 설치되어 있어야 합니다
2. 이 폴더(`week04-hands-on`)를 VSCode로 열어주세요
   - VSCode → 파일 → 폴더 열기 → `week04-hands-on` 선택
3. `data/` 폴더에 실습용 엑셀 파일이 있는지 확인

---

## 폴더 구조

```
week04-hands-on/
├── README.md              ← 지금 보고 있는 파일
├── data/                  ← 실습용 더미 엑셀 데이터
│   ├── 법인_US01_미국.xlsx
│   ├── 법인_JP01_일본.xlsx
│   ├── 법인_CN01_중국.xlsx
│   ├── 법인_DE01_독일.xlsx
│   ├── 법인_VN01_베트남.xlsx
│   ├── 외화채권잔액.xlsx
│   ├── 경비내역.xlsx
│   ├── create_dummy_data.py
│   ├── create_dummy_db.py
│   └── sales.db
├── answers/               ← 예시 답안 (막히면 참고)
│   ├── README.md
│   ├── step2_answer.py
│   ├── step3_answer.py
│   ├── step4b_answer.py
│   └── step4c_answer.py
└── exercises/             ← 실습 가이드
    ├── 사전과제.md
    ├── step1-create-claude-md.md
    ├── step2-vibe-coding.md
    ├── step3-merge-files.md
    └── step4-advanced-db-flask.md
```

---

## 실습 순서

### Step 1: CLAUDE.md 만들기 (25분)
👉 [exercises/step1-create-claude-md.md](exercises/step1-create-claude-md.md)

AI에게 "내 업무가 뭔지" 알려주는 파일을 직접 만들어봅니다.
CLAUDE.md가 있으면 AI가 훨씬 정확한 코드를 만들어줍니다.

### Step 2: 바이브코딩 체험 (30분)
👉 [exercises/step2-vibe-coding.md](exercises/step2-vibe-coding.md)

만든 CLAUDE.md를 AI에게 주고, 간단한 엑셀 처리 코드를 시켜봅니다.
"경비내역.xlsx"를 부서별로 정리하는 코드를 AI가 만들어주는 것을 체험합니다.

### Step 3: 여러 파일 합치기 (20분)
👉 [exercises/step3-merge-files.md](exercises/step3-merge-files.md)

5개 법인 매출 파일을 하나로 합치는 코드를 AI에게 시킵니다.
실제 업무에서 "법인별 파일 20개 합치기"를 어떻게 자동화하는지 맛봅니다.

### Step 4: (어드밴스) DB 연결 & Flask 웹 시각화
👉 [exercises/step4-advanced-db-flask.md](exercises/step4-advanced-db-flask.md)

Step 1~3을 끝내고 여유가 있거나, DB/웹에 관심 있는 분을 위한 확장 실습입니다.
엑셀 데이터를 DB에 넣고, Flask로 브라우저에서 보는 대시보드를 만들어봅니다.
MySQL 없어도 SQLite(Python 내장)로 체험 가능합니다.
