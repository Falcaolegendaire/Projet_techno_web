import uvicorn
from typing import Annotated
from fastapi import FastAPI, Request, Form, status, Cookie, Depends, HTTPException, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from server.database import Database
from server.models import UserLogin, UserRegister
from server.repositories import AuthRepository, CartRepository, FlowerRepository, UserRepository
from server.api import create_api
from server.websocket import WebsocketManager

COOKIE_LIFETIME = 3600

# Creates a connection to the database
database = Database("/templates/database.db")
SessionDep = Annotated[AsyncSession, Depends(database.get_db_access)]

# Creates a type to make it easier to receive the token on each route
TokenType = Annotated[str | None, Cookie()]

# Creates and populates the database tables
@asynccontextmanager
async def lifespan(_: FastAPI):
    # executes at startup
    await database.create_db_and_tables()
    await database.populate_db()
    yield
    # executes at shutdown

# Creates a FastAPI application and mounts the public folder
app = FastAPI(lifespan=lifespan)
app.mount("/public", StaticFiles(directory="public"), name="public")
app.mount("/api", create_api(SessionDep, TokenType))

# Initializes the template rendering system
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request, db_session: SessionDep, token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    # Retrieves all categories and their flowers
    flower_repository = FlowerRepository(db_session)
    categories = await flower_repository.get_by_categories()

    # Generates the HTML page
    response = templates.TemplateResponse(request=request, name="pages/home.html", context={
        "is_connected": user is not None,
        "token": user.token if user is not None else 0,
        "categories": categories,
    })

    # In case the token is defined but invalid, we remove the cookie
    if token is not None and user is None:
        response.delete_cookie("token")

    return response


@app.get("/login", response_class=RedirectResponse)
async def get_login(request: Request, db_session: SessionDep, token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    # In case the user is authenticated, we redirect them to the home page
    if user is not None:
        return RedirectResponse("/")

    # Generates the HTML page
    return templates.TemplateResponse(request=request, name="pages/login.html", context={})


@app.post("/login", response_class=RedirectResponse)
async def post_login(request: Request, db_session: SessionDep, body: Annotated[UserLogin, Form()]):
    # Checks credentials
    auth_repository = AuthRepository(db_session)
    if not await auth_repository.verify_authentication(body):
        return templates.TemplateResponse(request=request, name="pages/login.html", context={"login_error": True})

    # We create the authentication token
    user_repository = UserRepository(db_session)
    user = await user_repository.get_by_username(body.username)
    user.auth_token = auth_repository.create_authentication_token(user.id)
    await user_repository.save_user(user)

    # We redirect them to the home page
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("token", user.auth_token, max_age=COOKIE_LIFETIME)
    return response


@app.post("/register", response_class=HTMLResponse)
async def post_register(request: Request, db_session: SessionDep, body: Annotated[UserRegister, Form()]):
    # Checks validity new user's information and adds the user to the user list in case of success
    user_repository = UserRepository(db_session)
    success = await user_repository.verify_registration(body)

    if success:
        await user_repository.create_user(body)

    # Returns the login page
    return templates.TemplateResponse(request=request, name="pages/login.html", context={
        "register_page": not success,
        "register_succeed": success,
        "register_error": not success
    })


@app.get("/logout", response_class=RedirectResponse)
async def get_logout(db_session: SessionDep, token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    # If there is an associated user to the token, we remove the token from their information
    if user is not None:
        user.auth_token = None
        user_repository = UserRepository(db_session)
        await user_repository.save_user(user)

    # We redirect the client to the home page
    response = RedirectResponse("/")
    response.delete_cookie("token")
    return response


@app.get("/market", response_class=RedirectResponse)
async def get_market(request: Request, db_session: SessionDep, token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    # If the user is not authenticate, we redirect to the home page
    if user is None:
        response = RedirectResponse("/")
        response.delete_cookie("token")
        return response

    # We retrieve all the flowers
    flower_repository = FlowerRepository(db_session)
    flowers = await flower_repository.get_all()

    # We send the market page
    return templates.TemplateResponse(request=request, name="pages/market.html", context={
        "is_connected": user is not None,
        "token": user.token if user is not None else 0,
        "flowers": flowers
    })


@app.get("/cart", response_class=RedirectResponse)
async def get_cart(request: Request, db_session: SessionDep, token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    # If the user is not authenticate, we redirect to the home page
    if user is None:
        response = RedirectResponse("/")
        response.delete_cookie("token")
        return response

    # We send the market page
    return templates.TemplateResponse(request=request, name="pages/cart.html", context={
        "is_connected": user is not None,
        "token": user.token if user is not None else 0,
    })


@app.post("/cart", response_class=RedirectResponse)
async def get_cart(request: Request, db_session: SessionDep, cart: Annotated[str, Form()], token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    # If the user is not authenticate, we redirect to the home page
    if user is None:
        response = RedirectResponse("/")
        response.delete_cookie("token")
        return response

    # We check the cart
    cart_repository = CartRepository(db_session)
    success = await cart_repository.apply_cart(user, cart)

    # We send the market page
    return templates.TemplateResponse(request=request, name="pages/cart.html", context={
        "is_connected": user is not None,
        "token": user.token if user is not None else 0,
        "success": success,
        "error": not success
    })


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def get_not_found(request: Request, db_session: SessionDep, full_path: str, token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    # We send the market page
    return templates.TemplateResponse(request=request, name="pages/notFound.html", context={
        "is_connected": user is not None,
        "token": user.token if user is not None else 0,
    })

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, db_session: SessionDep, token: TokenType = None):
    # Retrieves the user's information from their authentication token
    auth_repository = AuthRepository(db_session)
    user = await auth_repository.decode_authentication_token(token)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged.")

    # Accepts the connection
    websocket_manager = WebsocketManager()
    await websocket_manager.accept(ws)
    await websocket_manager.listening(ws)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)