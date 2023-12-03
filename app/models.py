from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChatEntry(Base):
    __tablename__ = 'chat_entries'

    id = Column(Integer, primary_key=True)
    device_name = Column(String)
    device_id = Column(String, index=True)
    prompt = Column(String)
    full_description = Column(String)
    created_date = Column(DateTime(timezone=True))
