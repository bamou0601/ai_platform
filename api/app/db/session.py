from sqlalchemy.orm import sessionmaker
from app.db.database import engine

# Sessionを生成するファクトリー
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)