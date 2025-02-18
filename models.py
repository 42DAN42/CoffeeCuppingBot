from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Cupping(Base):
    __tablename__ = "cuppings"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, index=True)
    dt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fragrance = Column(Float)
    aroma = Column(Float)
    flavor = Column(Float)
    aftertaste = Column(Float)
    acidity = Column(Float)
    sweetness = Column(Float)
    mouthfeel = Column(Float)
    overall = Column(Float)
    brewing_method = Column(String)
    bean_name = Column(String)
    note = Column(String)
    avg = Column(Float)
