from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.db import models, database
from sqlalchemy import asc, delete, desc, select, func, update
from sqlalchemy.exc import SQLAlchemyError

from src.types.postTypes import postBaseRequest, postDeletion, postObj, postPagination, postUpdateRequest
from src.types.userTypes import userSession
import math

def get_post_by_id(db: Session, post_id: int)->postObj:
    stmt = select(models.Post).where(models.Post.id == post_id)
    result = db.execute(stmt).fetchone()

    if not result:
        return None 
    else:
        returnObj = postObj(id = result[0].id, title = result[0].title, content = result[0].content, creator_id = result[0].creator_id, board_id = result[0].board_id, isPublic = result[0].board.isPublic )
        return returnObj

def is_post_owner(post_id: int, user_session: userSession):
    if post_id in user_session.post_ids:
        return True 
    else:
        return False 
    
def post_create(db: Session, postForm: postBaseRequest, user_session: userSession)->postObj:
    try:
        newPost = models.Post(
            title = postForm.title,
            content = postForm.content,
            creator_id = user_session.id,
            board_id = postForm.id,
        )
        db.add(newPost)
        db.commit()
        return postObj(
            id = newPost.id,
            title = newPost.title,
            content = newPost.content,
            creator_id = newPost.creator_id,
            board_id = newPost.board_id,
            isPublic = newPost.board.isPublic
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = str(e.orig)
        )

def post_update(db: Session, postForm: postUpdateRequest, post_id: int):
    try:
        stmt = (
            update(models.Post)
                .where(models.Post.id == post_id)
                .values(
                    {
                        models.Post.title: postForm.title,
                        models.Post.content: postForm.content
                    }
                )
        )
        db.execute(stmt)
        db.commit()
        return True 
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = str(e.orig)
        )

def post_delete(db: Session, postForm: postDeletion):
    try:
        stmt = delete(models.Post).where(models.Post.id == postForm.id)
        db.execute(stmt)
        db.commit()
        return True
    except SQLAlchemyError as e:
            raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = str(e.orig)
            )
    
def posts_pagination(db: Session, post_pagination: postPagination, total_posts_size: int, user_session: userSession):
    pageNum = post_pagination.page 
    pageSize = post_pagination.pageSize
    boardId = post_pagination.boardId

    # if pageNum <= 0 then set pageNum to 1
    if pageNum <= 0:
        pageNum = 1

    lastPageNum = math.ceil(total_posts_size / pageSize)

    # if pageNum exceeds boards_size/pageSize, then return end page
    if pageNum > lastPageNum:
        pageNum = lastPageNum

    # if pageNum <= 0 then set pageNum to 1
    if pageNum <= 0:
        pageNum = 1

    # calculate offset and limit
    offset = (pageNum - 1) * pageSize
    limit = pageSize

    stmt = select(models.Post) \
        .join(models.Board) \
        .where((models.Board.id == boardId) & ((models.Board.creator_id == user_session.id) | (models.Board.isPublic == True))) \
        .offset(offset) \
        .limit(limit)
    posts_list = db.execute(stmt).fetchall()
    posts_result = list()
    for post in list(posts_list):
        posts_result.append(
            postObj(
                id = post[0].id,
                title = post[0].title,
                content = post[0].content,
                creator_id = post[0].creator_id,
                board_id = post[0].board_id,
                isPublic = post[0].board.isPublic
            )
        )
    
    return posts_result

def total_posts_size(db: Session):
    boardSize = db.query(models.Post).count()
    return boardSize