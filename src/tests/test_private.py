from fastapi.testclient import TestClient
from fastapi import status 
from src.utils.test_db_setup import override_get_db, refresh_db, override_get_redis_client, refresh_redis

from src.types.boardTypes import boardBaseRequest, boardObjResponse, boardUpdate, boardObj, boardResponse, boardListResponse
from src.types.postTypes import postBaseRequest, postObjResponse, postObj, postResponse, postListResponse, postUpdateRequest
from src.types.authTypes import authResponse, authSigninRequest, authSignupRequest
from src.types.postTypes import postBaseRequest

from main import app
from src.db.database import get_db, get_redis_client

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis_client] = override_get_redis_client

client = TestClient(app)

# test user trying to access other's private board 
def test_private_board(refresh_db, refresh_redis):
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
        isPublic = False
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
    response = client.post("/api/auth/signout")

    # login as other user that does not have access to the board
    ## signup
    signupForm = authSignupRequest(
        email = "hello@hello.hello",
        password = "hellopassword",
        fullName = "hellocookie"
    )
    response = client.post("/api/auth/signup", json=signupForm.model_dump())
    response.json() == authResponse(success = True, message = "signup success").model_dump()
    assert response.status_code == status.HTTP_200_OK

    #signin
    signinForm = authSigninRequest(
        email = "hello@hello.hello",
        password = "hellopassword"
    )
    response = client.post("/api/auth/signin", json = signinForm.model_dump())

    # trying to get private board
    response = client.get("/api/board/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == boardObjResponse(
            success = False,
            message = "Board get failed. Board is not accessible.",
            board = None
        ).model_dump()

    # trying to delete others board
    response = client.delete("/api/board/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == boardResponse(
            success = False,
            message = "User is not board owner."
        ).model_dump()
    
    # trying to update other's board
    updateBoard = boardBaseRequest(
        isPublic = True,
        name = "your board got hacked!!"
    )
    response = client.patch("/api/board/1", json = updateBoard.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == boardObjResponse(
            success = False,
            message = "LoggedIn user is not board owner.",
            board = None 
        ).model_dump()
    
    # trying to get list
    # trying to get others board
    response = client.get("/api/board/list")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == boardListResponse(
        success = True,
        message = "Board getting list success!",
        boards = []
    ).model_dump()




# test user trying to access other's private board 
def test_private_post(refresh_db, refresh_redis):
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
        isPublic = False
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
    response = client.post("/api/auth/signout")

    # login as other user that does not have access to the board
    ## signup
    signupForm = authSignupRequest(
        email = "hello@hello.hello",
        password = "hellopassword",
        fullName = "hellocookie"
    )
    response = client.post("/api/auth/signup", json=signupForm.model_dump())
    response.json() == authResponse(success = True, message = "signup success").model_dump()
    assert response.status_code == status.HTTP_200_OK

    #signin
    signinForm = authSigninRequest(
        email = "hello@hello.hello",
        password = "hellopassword"
    )

    response = client.post("/api/auth/signin", json = signinForm.model_dump())

    # get private post
    response = client.get("/api/post/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == postObjResponse(
            success = False,
            message = "Post is not viewable. Please check if you are the owner of the post or the post is in public board",
            post = None
        ).model_dump()

    # update private post
    updatePostForm = postUpdateRequest(
        title = "modified title",
        content = "modified content!"
    )
    response = client.patch("/api/post/1", json = updatePostForm.model_dump())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == postObjResponse(
            success = False,
            message = "current user is not post owner. cannot update",
            post = None 
        ).model_dump()
    
    # delete private post 
    response = client.delete("/api/post/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == postResponse(
            success = False,
            message = "User is not post owner"
        ).model_dump()
    
    # get post list from private board
    response = client.get("/api/post/list?boardId=1&page=1&pageSize=10")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == postListResponse(
            success = False,
            message = "User does not have access to the board.",
            posts = None
        ).model_dump()