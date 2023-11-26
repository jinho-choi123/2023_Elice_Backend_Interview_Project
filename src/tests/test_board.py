from fastapi.testclient import TestClient
from fastapi import status 
from src.utils.test_db_setup import override_get_db, refresh_db

from src.types.boardTypes import boardBaseRequest, boardObjResponse, boardUpdate, boardObj, boardResponse, boardListResponse
from src.types.authTypes import authResponse, authSigninRequest, authSignupRequest
from src.types.postTypes import postBaseRequest

from main import app
from src.db.database import get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# test board api without signin
def test_board_without_signin(refresh_db):
    boardForm = boardBaseRequest(
        name = "mango",
        isPublic = True
    )

    # board creation without signin
    response = client.post("/api/board/", json = boardForm.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # board update without signin
    # also it is invalid board
    response = client.patch("/api/board/123", json = boardForm.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # board delete without signin
    response = client.delete("/api/board/123")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # board get list without signin
    response = client.get("/api/board/list")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

    # board get without signin
    response = client.get("/api/board/234")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Cookie does not exists"}

def test_board_integrated(refresh_db):
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
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == boardObjResponse(
        success = True,
        message = "Board Creation Success!",
        board = boardObj(
            id = 1,
            name = "mango",
            post_ids = [],
            creator_id = 1,
            isPublic = True
        )
    ).model_dump()

    # board create with same name
    response = client.post("/api/board/", json = boardForm.model_dump())
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == boardObjResponse(
        success = False,
        message = "Board name already in use",
        board = None
    ).model_dump()

    # board get
    response = client.get("/api/board/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == boardObjResponse(
        success = True,
        message = "Board get success",
        board = boardObj(
            id = 1,
            name = "mango",
            post_ids = [],
            creator_id = 1,
            isPublic = True
        )
    ).model_dump()

    # board update
    updateBoardForm = boardBaseRequest(
        name = "mangohaschanged",
        isPublic = True
    )
    response = client.patch("/api/board/1", json = updateBoardForm.model_dump())
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == boardResponse(
        success = True,
        message = "Board update success!"
    ).model_dump()

    # board delete
    response = client.delete("/api/board/1")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == boardResponse(
        success = True,
        message = "Board deletion success!"
    ).model_dump()


def test_board_list_api_order(refresh_db):
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

    # create 20 boards 
    # board id with 1 has 1 post
    # board id with 2 has 2 post 
    # ...
    # board id with 20 has 20 post 
    for board_id in range(1, 21):
        boardForm = boardBaseRequest(
            name = "mango with id: " + str(board_id),
            isPublic = True
        )
        client.post("/api/board/", json = boardForm.model_dump())

        for post_id in range(board_id):
            postForm = postBaseRequest(
                id = board_id,
                title = "post title",
                content = "post content"
            )
            client.post("/api/post/", json = postForm.model_dump())

    # test the pagination and order!
    response = client.get("/api/board/list?page=1&pageSize=10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] == True 
    assert response.json()["message"] == "Board getting list success!"
    assert len(response.json()["boards"]) == 10
    # test index of all 10 boards
    for idx in range(10):
        assert response.json()["boards"][idx]["id"] == 20 - idx



    # test the pagination and order!
    response = client.get("/api/board/list?page=2&pageSize=10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] == True 
    assert response.json()["message"] == "Board getting list success!"
    assert len(response.json()["boards"]) == 10

    # test index of all 10 boards
    for idx in range(10):
        assert response.json()["boards"][idx]["id"] == 10 - idx

    
    
    # test the pagination and order!
    response = client.get("/api/board/list?page=2&pageSize=10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] == True 
    assert response.json()["message"] == "Board getting list success!"
    assert len(response.json()["boards"]) == 10

    # test index of all 10 boards
    for idx in range(10):
        assert response.json()["boards"][idx]["id"] == 10 - idx