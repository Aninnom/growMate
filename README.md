# growMate 🌱
> 2026-1 한양대학교 ERICA 피지컬컴퓨팅 5조
> 라즈베리파이 + 센서 + LLM(Google Gemini)와 채팅으로 돌보는 양방향소통 스마트화분 프로젝트

![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=FastAPI&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=flat-square&logo=Raspberry-Pi)
![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=flat-square&logo=googlebard&logoColor=white)

## 📌 프로젝트 개요
growMate는 식물의 상태(온/습도 등)를 실시간으로 모니터링하고, Google Gemini 2.5 Flash를 기반으로 부여된 '식물 페르소나'와 사용자가 텍스트로 교감할 수 있는 스마트 화분입니다.

### 📡 System Architecture
```
React UI(Frontend) ──────▶ FastAPI(Backend) ──────▶ Gemini 2.5 Flash(Cloud API)
                    /api                      SSE
```

## Directory Structure
```
growMate/
├── frontend/      Frontend 디자인 초안
├── frontend-next/ React + Vite UI (식물 모니터/채팅)
├── backend/       FastAPI + Gemini API (식물 페르소나 챗봇)
├── db/            센서값 저장
├── raspberry/     식물 표정, 센서값 전송
└── README.md
```

## 코드 시작 가이드
### 0. clone
```bash
git clone https://github.com/Aninnom/growMate.git
cd growMate
```

### 1. Gemini API 키 발급
- https://aistudio.google.com/apikey → "Create API key" (개인 구글 계정 사용)
- 학교 계정은 GCP 정책 때문에 안 될 수 있음
- 무료 티어: 분당 10~30 요청, 일일 약 1500 — 발표/개발 충분, 카드 등록 불필요

### 2. 백엔드 실행(FastAPI)
```bash
cd backend

# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate       # Windows의 경우: .venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 파일 셋팅
cp .env.example .env # .env 열고 GEMINI_API_KEY=AIza... 본인 키 넣기

# 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

작동 확인:
```bash
curl http://localhost:8000/api/health
# {"ok": true, "model": "gemini-2.5-flash"}
```

### 3. 프론트엔드 실행 (별도 터미널)
```bash
cd frontend
npm install
npm run dev
```
브라우저 → http://localhost:5173 → 💬 탭에서 식물에게 말 걸기.

## 보안 및 API키 관리 가이드

- **`.env`는 절대 커밋 금지**. 루트 `.gitignore`에 등록되어 있음.
- 본인 API 키는 본인 컴퓨터에서만 보관. 팀원도 각자 발급해서 사용.
- 만약 키가 실수로 푸시됐다면 즉시 https://aistudio.google.com/apikey 에서 revoke 후 새 키 발급.

## 트러블슈팅

`backend/main.py`와 코드 안 주석 참고. 자주 보는 거:

| 증상 | 원인 / 해결 |
|---|---|
| `GEMINI_API_KEY 환경변수가 없음` | `backend/.env` 파일 위치/내용 확인. uvicorn을 `backend/`에서 실행했는지. |
| 응답이 한 글자만 옴 | Gemini 2.5의 thinking 토큰이 한도를 먹는 케이스. 이미 `thinking_budget=0`으로 끔. |
| 429 Too Many Requests | 분당 한도 초과. 1분 기다리거나 `MODEL=gemini-2.5-flash-lite`로. |
| CORS 오류 | `vite.config.js`의 `/api` proxy가 적용됐는지. |
| 한국어 응답이 어색함 | `backend/main.py`의 `build_system_prompt` 안 예시·규칙 조정. |
