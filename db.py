from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_message = Column(Text)
    bot_reply = Column(Text)

engine = create_engine('sqlite:///chat.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
