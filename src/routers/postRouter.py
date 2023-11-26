from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.orm import Session
from src.controller.postController import get_post_by_id, is_post_owner, post_create, post_delete, post_update, posts_pagination, total_posts_size
from src.controller.boardController import get_board_by_id, is_board_owner
from src.db.database import get_db

from src.middlewares.authMiddleware import get_current_user
from src.types.postTypes import postBaseRequest, postDeletion, postListResponse, postObjResponse, postPagination, postResponse, postUpdateRequest 

postRouter = APIRouter(
    prefix="/post",
)


    
@postRouter.post("/")
def post_Create(postForm: postBaseRequest, db: Session = Depends(get_db), user = Depends(get_current_user)):
    # create post 
    newPost = post_create(db, postForm, user)

    if not newPost:
        # not reached
        return postObjResponse(
            success = False,
            message = "Post creation failed",
            post = None 
        )
    # post creation success 
    return postObjResponse(
        success = True,
        message = "Post creation success",
        post = newPost
    )

@postRouter.patch("/{post_id}")
def post_Update(post_id: int, postForm: postUpdateRequest, response: Response, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not is_post_owner(post_id, user):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return postObjResponse(
            success = False,
            message = "current user is not post owner. cannot update",
            post = None 
        )
    
    post_update(db, postForm, post_id)
    updatedPost = get_post_by_id(db, post_id)
    return postObjResponse(
        success = True,
        message = "Post update success!",
        post = updatedPost
    )

@postRouter.delete("/{post_id}")
def post_Delete(post_id: int, response: Response, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not get_post_by_id(db, post_id):
        return postResponse(
            success = False,
            message = "Post does not exists"
        )
    if not is_post_owner(post_id, user):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return postResponse(
            success = False,
            message = "User is not post owner"
        )

    postForm = postDeletion(
        id = post_id 
    )

    post_delete(db, postForm)

    return postResponse(
        success = True,
        message = "Post deletion success!"
    )

@postRouter.get("/list")
def post_List(boardId: int, response: Response, page: int = 0, pageSize: int = 10, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not boardId:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return postListResponse(
            success = False,
            message = "Board Id is not given",
            posts = None
        )
    
    # check if board is public or user is owner
    isBoardPublic = get_board_by_id(db, boardId).isPublic

    if (not isBoardPublic) and (not is_board_owner(boardId, user)):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return postListResponse(
            success = False,
            message = "User does not have access to the board.",
            posts = None
        )
    
    post_pagination = postPagination(page = page, pageSize = pageSize, boardId = boardId)

    total_posts = total_posts_size(db)

    showing_posts = posts_pagination(db, post_pagination, total_posts, user)

    return postListResponse(
        success = True,
        message = "Post getting list success!",
        posts = showing_posts
    )

@postRouter.get("/{post_id}")
def post_Get(post_id: int, response: Response, db: Session = Depends(get_db), user = Depends(get_current_user)):
    post = get_post_by_id(db, post_id)

    if not post:
        return postObjResponse(
            success = False,
            message = "Post does not exists",
            post = None 
        )
    elif post.isPublic | is_post_owner(post.id, user):
        return postObjResponse(
            success = True,
            message = "Post get success",
            post = post
        )
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return postObjResponse(
            success = False,
            message = "Post is not viewable. Please check if you are the owner of the post or the post is in public board",
            post = None
        )