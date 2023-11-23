from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, ARRAY
from sqlalchemy.orm import relationship

from .database import Base, engine

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fullName = Column(String)
    email = Column(String, unique=True, index=True)
    password_salt = Column(String)
    password_hash = Column(String)
    boards = relationship("Board", back_populates="creator")

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    isPublic = Column(Boolean, index=True, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="boards")
    posts = relationship("Post", back_populates="board")
    is_active = Column(Boolean, default=True)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    creator = Column(Integer, ForeignKey("users.id"))
    board_id = Column(Integer, ForeignKey("boards.id"))
    board = relationship("Board", back_populates="posts")
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)