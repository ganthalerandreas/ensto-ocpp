from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String

Base = declarative_base()


class ChargingSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)

    start_time = Column(String)
    end_time = Column(String)

    meter_start = Column(Float)
    meter_stop = Column(Float)

    energy_kwh = Column(Float)
    total_euro = Column(Float)

    status = Column(String)
