from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence, Column, Integer, String, TEXT, FLOAT
from sqlalchemy.dialects.postgresql import TIMESTAMP

Base = declarative_base()

class Journey(Base):
    __tablename__ = "journeys_<username>" # name of the table 
    id = Column(Integer, Sequence("journeys_<username>_id"), primary_key=True)
    source = Column(TEXT)
    destination = Column(TEXT)
    departure_datetime = Column(TIMESTAMP)
    arrival_datetime = Column(TIMESTAMP)
    carrier = Column(TEXT)
    vehicle_type = Column(TEXT)
    price = Column(FLOAT)
    currency = Column(String(3))