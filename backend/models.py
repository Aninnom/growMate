"""
SQLAlchemy 모델 + 초기 데이터 시드.
- Setting:    설정 화면 값 (그룹별 JSON 1행: notify / care / chat)
- Suggestion: 홈 말풍선 제안 (water / light) 의 상태 (active|dismissed|resolved)

센서/식물상태/일지는 하드웨어(라즈베리파이) 연동 전이라 프론트 mock 으로 두고,
'페이지 이동 시 사라지는' 문제가 있던 설정·제안만 여기서 DB 로 영속화한다.
"""
import json
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

# main.py 와 동일하게 두 실행 방식 모두 지원
try:
    from database import Base, SessionLocal
except ModuleNotFoundError:
    from backend.database import Base, SessionLocal


class Setting(Base):
    __tablename__ = "settings"
    # key: "notify" | "care" | "chat", value: JSON 문자열
    key: Mapped[str] = mapped_column(String(32), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class Suggestion(Base):
    __tablename__ = "suggestions"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    type: Mapped[str] = mapped_column(String(32))          # water | light
    status: Mapped[str] = mapped_column(String(16), default="active")  # active|dismissed|resolved


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(16))          # user | plant
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SensorReading(Base):
    """센서별 '최신값' 한 행. 라즈베리파이가 POST 할 때마다 갱신(upsert)된다."""
    __tablename__ = "sensor_readings"
    key: Mapped[str] = mapped_column(String(16), primary_key=True)  # soil|temp|humid|light
    value: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ── 초기 기본값 (lib/data/settings.js, suggestions.js 와 동일) ──────────
DEFAULT_SETTINGS = {
    "notify": {"water": True, "light": False, "chat": True},
    "care": {"autoProtect": True, "ledAuto": True, "showSuggest": False},
    "chat": {"saveHistory": True, "tone": "따뜻하게", "nickname": ""},
}

# 식물 프로필 (프론트 useProfile.js DEFAULT_PROFILE 과 동일).
# 적정 환경 범위(preferences)는 센서 상태/표정 판단의 단일 기준이 된다.
DEFAULT_PROFILE = {
    "name": "그로우메이트",
    "species": "몬스테라",
    "avatar": "happy",
    "adoptionDate": "",
    "preferences": {
        "tempMin": 18,
        "tempMax": 28,
        "humidityMin": 60,
        "humidityMax": 80,
        "soilMoistureMin": 40,
        "soilMoistureMax": 70,
        "wateringCycle": 7,
        "lightLevel": "보통",
    },
}

DEFAULT_SUGGESTIONS = [
    {"id": "water", "type": "water"},
    {"id": "light", "type": "light"},
]

# 라즈베리파이가 아직 값을 안 보냈을 때 홈에 보여줄 초기 센서값
DEFAULT_SENSORS = {"soil": 24, "temp": 24.6, "humid": 58, "light": 520}


def seed_defaults() -> None:
    """행이 없을 때만 기본값을 채운다 (이미 있으면 사용자 값 보존)."""
    db = SessionLocal()
    try:
        for group, val in DEFAULT_SETTINGS.items():
            if db.get(Setting, group) is None:
                db.add(Setting(key=group, value=json.dumps(val, ensure_ascii=False)))
        # 프로필도 settings 테이블의 "profile" 그룹으로 영속화
        if db.get(Setting, "profile") is None:
            db.add(Setting(key="profile", value=json.dumps(DEFAULT_PROFILE, ensure_ascii=False)))
        for s in DEFAULT_SUGGESTIONS:
            if db.get(Suggestion, s["id"]) is None:
                db.add(Suggestion(id=s["id"], type=s["type"], status="active"))
        for key, val in DEFAULT_SENSORS.items():
            if db.get(SensorReading, key) is None:
                db.add(SensorReading(key=key, value=val))
        db.commit()
    finally:
        db.close()
