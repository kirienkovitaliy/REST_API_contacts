from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi_limiter.depends import RateLimiter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages

router = APIRouter(prefix="/auth", tags=['auth'])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=3, seconds=300))],
             status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes a UserModel object as input, which is validated by pydantic.
        The password is hashed using Argon2 and stored in the database.
        An email with an activation link is sent to the user's email address.

    :param body: UserModel: Get the user information from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param db: Session: Get a database session
    :return: A usermodel object, which is defined in the models
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_ALREADY_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenModel, status_code=status.HTTP_201_CREATED)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes the username and password from the request body,
        verifies that they are correct, and returns an access token.

    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Get the database session
    :return: A dictionary with the access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD)
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
        If there is no valid user associated with the given email address or if there are any errors during decoding
        or creating tokens then an HTTPException will be raised.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Get the database session
    :return: An access_token and a refresh_token
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
    It takes the token from the URL and uses it to get the user's email address.
    The function then checks if there is a user with that email in our database, and if not, returns an error message.
    If there is a user with that email in our database, we check whether their account has already been confirmed or not.
    If it has been confirmed already, we return another error message saying so; otherwise we call repository_users'
    confirmed_email function which sets the 'confirmed' field of that particular User object

    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A message that the email is already confirmed if the user has
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR)
    if user.confirmed:
        return {"message": messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED}
    await repository_users.confirmed_email(email, db)
    return {"message": messages.EMAIL_CONFIRMED}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their account. The function takes in a RequestEmail object, which contains the email of
    the user who wants to confirm their account. It then checks if there is already an unconfirmed
    account associated with that email address, and if so it sends an email containing a confirmation link.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :return: A json response that contains a message
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED}
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": messages.CHECK_YOUR_EMAIL_FOR_CONFIRMATION}
