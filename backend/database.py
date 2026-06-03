from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

# DB 환경변수(DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME)가 모두 있으면 MySQL,
# 하나라도 없으면 로컬 개발용 sqlite로 동작한다.
_db_user = os.getenv("DB_USER")
_db_password = os.getenv("DB_PASSWORD")
_db_host = os.getenv("DB_HOST")
_db_port = os.getenv("DB_PORT")
_db_name = os.getenv("DB_NAME")

if all([_db_user, _db_password, _db_host, _db_port, _db_name]):
    password = quote_plus(_db_password)
    DATABASE_URL = f"mysql+pymysql://{_db_user}:{password}@{_db_host}:{_db_port}/{_db_name}"
    engine = create_engine(DATABASE_URL)
else:
    DATABASE_URL = "sqlite:///./growmate.db"
    # sqlite는 기본적으로 같은 스레드에서만 접근 허용 → FastAPI용으로 풀어준다.
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
