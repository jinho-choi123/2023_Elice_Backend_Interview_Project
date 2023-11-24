from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List

from .database import Base, engine

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fullName = Column(String)
    email = Column(String, unique=True, index=True)
    password_salt = Column(String)
    password_hash = Column(String)
    boards: Mapped[List["Board"]] = relationship( back_populates="creator")

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True)
    isPublic = Column(Boolean, index=True, default=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    creator: Mapped["User"] = relationship(back_populates="boards")
    posts: Mapped[List["Post"]] = relationship(back_populates="board")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    creator = Column(Integer, ForeignKey("users.id"))
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))
    board: Mapped["Board"] = relationship(back_populates="posts")

Base.metadata.create_all(bind=engine)