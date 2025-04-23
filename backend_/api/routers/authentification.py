"""
Authentication Routes Module.

This module provides the authentication endpoints for the application, including
user login handling. It uses OAuth2 with Password (and hashing), including the use of JWT tokens
for secure authentication and access token generation.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from api.authentication.oauth import create_access_token, oauth2_scheme
from api.utils.utils import verify_password 
from jose import JWTError, jwt
import config
from api.models import models
from api.schemas import schemas

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM

router = APIRouter(tags=['Authentication'])

@router.post(
    '/login',
    response_model=schemas.Token,
    summary="User Login",
    description=(
        """User Login: Authenticate a user and generate an access token.

        This endpoint handles user authentication by verifying the provided credentials
        (email and password). Upon successful authentication, it generates and returns
        a JWT access token that can be used to access protected endpoints.

        Args:
        - userdetails (OAuth2PasswordRequestForm): User credentials.
        - db (Session): Database session.

        Returns:
        - dict: Dictionary containing the access token and token type.

        Raises:
        - HTTPException: If the provided credentials are incorrect.
        """
    )
)
def login(
    userdetails: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    user = db.query(models.User).filter(models.User.email == userdetails.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The User does not exist"
        )

    if not verify_password(userdetails.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The Passwords do not match"
        )
        
    if not user.email_active:
        raise HTTPException(status_code=400, detail="Please confirm your email before logging in.")
    
    access_token = create_access_token(data={"user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post(
    '/logout',
    summary="User Logout",
    description=(
        """User Logout: Log out a user and blacklist the current token.

        This endpoint logs out the authenticated user by blacklisting the provided JWT token,
        preventing it from being used for future requests. This ensures that the token is no longer valid.

        Args:
        - token (str): Access token.
        - db (Session): Database session.

        Returns:
        - dict: Dictionary with a success message.

        Raises:
        - HTTPException: If the token cannot be validated.
        """
    )
)
def logout(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        jti = payload.get("jti")

        if jti:
            try:
                db.add(models.TokenBlacklist(jti=jti))
                db.commit()
            except IntegrityError:
                pass

        return {"message": "Logout successful"}

    except JWTError as e:
        raise credentials_exception



# @router.post(
#     '/login',
#     response_model=schemas.Token,
#     summary="User Login",
#     description=(
#         """User Login: Authenticate a user and generate an access token.

#         This endpoint handles user authentication by verifying the provided credentials
#         (email and password). Upon successful authentication, it generates and returns
#         a JWT access token that can be used to access protected endpoints.

#         Args:
#         - userdetails (OAuth2PasswordRequestForm): User credentials.
#         - db (Session): Database session.

#         Returns:
#         - dict: Dictionary containing the access token and token type.

#         Raises:
#         - HTTPException: If the provided credentials are incorrect.
#         """
#     )
# )
# async def login(
#     userdetails: OAuth2PasswordRequestFormReCaptcha = Depends(),
#     db: Session = Depends(get_db)
# ):
#     # Verify reCAPTCHA token
#     verification_result = await verify_recaptcha(userdetails.recaptcha_token)
#     if not verification_result.success:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reCAPTCHA token")

#     user = db.query(models.User).filter(models.User.email == userdetails.username).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="The User does not exist"
#         )

#     if not verify_password(userdetails.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="The Passwords do not match"
#         )

#     access_token = create_access_token(data={"user_id": user.id})
#     return {"access_token": access_token, "token_type": "bearer"}

