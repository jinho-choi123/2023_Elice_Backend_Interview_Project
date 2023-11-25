from fastapi import APIRouter, Cookie, Response, status
from src.controller.postController import get_post_by_id, is_post_owner, post_create, post_delete, post_update, posts_pagination, total_posts_size
from src.db.database import SessionLocal

from src.middlewares.authMiddleware import get_current_user
from src.types.postTypes import postBaseRequest, postDeletion, postListResponse, postObjResponse, postPagination, postResponse 

postRouter = APIRouter(
    prefix="/post",
)


    
@postRouter.post("/")
def post_Create(postForm: postBaseRequest, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

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

@postRouter.patch("/")
def post_Update(postForm: postBaseRequest, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

    if not is_post_owner(postForm.id, user):
        return postResponse(
            success = False,
            message = "current user is not post owner. cannot update"
        )
    
    post_update(db, postForm)
    return postResponse(
        success = True,
        message = "Post update success!"
    )

@postRouter.delete("/{post_id}")
def post_Delete(post_id: int, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

    if not get_post_by_id(db, post_id):
        return postResponse(
            success = False,
            message = "Post does not exists"
        )
    if not is_post_owner(post_id, user):
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
def post_List(boardId: int, page: int = 0, pageSize: int = 10, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)

    if not boardId:
        return postListResponse(
            success = False,
            message = "Board Id is not given",
            posts = None
        )
    
    post_pagination = postPagination(page = page, pageSize = pageSize, boardId = boardId)

    db = SessionLocal()

    total_posts = total_posts_size(db)

    showing_posts = posts_pagination(db, post_pagination, total_posts, user)

    return postListResponse(
        success = True,
        message = "Post getting list success!",
        posts = showing_posts
    )

@postRouter.get("/{post_id}")
def post_Get(post_id: int, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)

    db = SessionLocal()
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
        return postObjResponse(
            success = False,
            message = "Post is not viewable. Please check if you are the owner of the post or the post is in public board",
            post = None
        )