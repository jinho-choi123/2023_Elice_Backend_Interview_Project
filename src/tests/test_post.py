from fastapi.testclient import TestClient
from fastapi import status 
from src.utils.test_db_setup import override_get_db, refresh_db, override_get_redis_client, refresh_redis

from src.types.boardTypes import boardBaseRequest, boardObjResponse, boardUpdate, boardObj, boardResponse, boardListResponse
from src.types.authTypes import authResponse, authSigninRequest, authSignupRequest
from src.types.postTypes import postBaseRequest, postObjResponse, postObj, postResponse, postUpdateRequest

from main import app
from src.db.database import get_db, get_redis_client

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis_client] = override_get_redis_client

client = TestClient(app)

# test post api without signin 
def test_post_without_signin(refresh_db, refresh_redis):

    postForm = postBaseRequest(
        id = 1,
        title = "mango cookie post",
        content = "post content"
    )
    # create post without signin
    response = client.post("/api/post", json = postForm.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # update post without signin
    response = client.patch("/api/post/1", json = postForm.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # delete post without signin
    response = client.delete("/api/post/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # get list of post without signin
    response = client.get("/api/post/list")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # get post without signin
    response = client.get("/api/post/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}


def test_post_integrated(refresh_db, refresh_redis):
    ## signup
    signupForm = authSignupRequest(
        email = "mango@mango.mango",
        password = "simplepassword",
        fullName = "mangocookie"
    )
    response = client.post("/api/auth/signup", json=signupForm.model_dump())
    #signin
    signinForm = authSigninRequest(
        email = "mango@mango.mango",
        password = "simplepassword"
    )
    response = client.post("/api/auth/signin", json = signinForm.model_dump())

    boardForm = boardBaseRequest(
        name = "mango",
        isPublic = True
    )

    # board creation 
    response = client.post("/api/board/", json = boardForm.model_dump())

    postForm = postBaseRequest(
        id = 1,
        title = "mango cookie post",
        content = "post content"
    )
    # create post 
    response = client.post("/api/post", json = postForm.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == postObjResponse(
        success = True,
        message = "Post creation success",
        post = postObj(
            id = 1, 
            title = "mango cookie post",
            content = "post content",
            creator_id = 1,
            board_id = 1,
            isPublic = True
        )
    ).model_dump()

    # post get 
    response = client.get("/api/post/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == postObjResponse(
        success = True,
        message = "Post get success",
        post = postObj(
            id = 1, 
            title = "mango cookie post",
            content = "post content",
            creator_id = 1,
            board_id = 1,
            isPublic = True
        )
    ).model_dump()

    # post udpate 
    updatePostForm = postUpdateRequest(
        title = "modified title",
        content = "modified content!"
    )
    response = client.patch("/api/post/1", json = updatePostForm.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == postObjResponse(
        success=True,
        message = "Post update success!",
        post = postObj(
            id = 1,
            title = "modified title",
            content = "modified content!",
            creator_id = 1,
            board_id = 1,
            isPublic = True
        )
    ).model_dump()

    # post delete
    response = client.delete("/api/post/1")
    
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == postResponse(
        success = True,
        message = "Post deletion success!"
    ).model_dump()


     # post get delted post
    response = client.get("/api/post/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == postObjResponse(
        success = False,
        message = "Post does not exists",
        post = None
    ).model_dump()

def test_post_list_api(refresh_db, refresh_redis):

    ## signup
    signupForm = authSignupRequest(
        email = "mango@mango.mango",
        password = "simplepassword",
        fullName = "mangocookie"
    )
    response = client.post("/api/auth/signup", json=signupForm.model_dump())
    #signin
    signinForm = authSigninRequest(
        email = "mango@mango.mango",
        password = "simplepassword"
    )
    response = client.post("/api/auth/signin", json = signinForm.model_dump())

    boardForm = boardBaseRequest(
        name = "mango",
        isPublic = True
    )

    # board creation 
    response = client.post("/api/board/", json = boardForm.model_dump())

    # create 100 posts
    for idx in range(100):
        postForm = postBaseRequest(
            id = 1,
            title = "mango cookie post!" + str(idx),
            content = "post content " + str(idx)
        )
        # create post 
        response = client.post("/api/post", json = postForm.model_dump())
    
    response = client.get("/api/post/list?boardId=1&page=1&pageSize=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["posts"]) == 10

    ## if we add all 10 list request's post ids, then it will be 1 ~ 100
    seenPostId = set()
    for i in range(1, 11):
        response = client.get(f'/api/post/list?boardId=1&page={i}&pageSize=10')
        for post in response.json()["posts"]:
            seenPostId.add(post["id"])
    
    # check if seenPostId 's size is 100
    assert len(seenPostId) == 100

    
        