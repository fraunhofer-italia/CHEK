"""
API Routes for User Management.
Author: Elias Niederwieser
Year: 2024
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request, status
from sqlalchemy.orm import Session
from api.models import models
from api.schemas import schemas
from database import get_db
from api.utils.utils import hash_pass, is_strong_password
from api.authentication.oauth import check_admin_role
from api.utils.recaptcha import verify_recaptcha

from api.utils.token_utils import generate_confirmation_token
from api.utils.email_utils import send_email
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=['User Management'])

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_dir)

@router.get(
    '/',
    response_model=List[schemas.UserOutput],
    dependencies=[Depends(check_admin_role)],
    summary="Get All Users (Admin Only) [50 RPM]",
    description="""
    Retrieve a list of all users from the database. (Admin Only):
    
        - This endpoint allows an admin to get a list of all users registered in the system.
        - The response includes an array of user objects with detailed user information.
        - This endpoint is rate-limited to 50 requests per minute.
    """
)
async def get_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.get(
    '/{user_id}',
    response_model=schemas.UserOutput,
    dependencies=[Depends(check_admin_role)],
    status_code=status.HTTP_200_OK,
    summary="Get One User (Admin Only)",
    description="""
    Retrieve details of a single user by their user_id. (Admin Only):
    
     - This endpoint allows an admin to get detailed information about a specific user by their user ID.
     - The response includes the user's full information if found, otherwise a 404 error is returned.
    """
)
async def get_one_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}"
        )
    return user

@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOutput,
    summary="Create User",
    description="""
    Register a new user
    
        - This endpoint allows for the registration of a new user. 
        - The request body must include the user's details such as email, password, and other required fields defined in the CreateUser schema. 
        - The password will be validated for strength and hashed before storing. 
        - If the email is already registered or the password is weak, appropriate error responses are returned."
    """
)
async def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    # Verify reCAPTCHA token
    # verification_result = await verify_recaptcha(user.recaptcha_token)
    # if not verification_result.success:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reCAPTCHA token")

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if not is_strong_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Weak password. Password must include at least one number and one special character."
        )
    user.password = hash_pass(user.password)
    new_user = models.User(**user.dict(exclude={"recaptcha_token"}))
    
    token = generate_confirmation_token(new_user.email)

    confirmation_url = f"http://your-frontend-url/confirm-email?token={token}" #Julius

    name = f"{new_user.first_name} {new_user.last_name}"

    html_content = templates.get_template("confirmation_email.html").render(
        name=name, confirmation_url=confirmation_url
    )

    send_email(
        to_email=new_user.email,
        subject="CHEK Email Confirmation",
        text=f"Please confirm your email by clicking on the following link: {confirmation_url}",
        html=html_content
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )
    return new_user

@router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_admin_role)],
    summary="Delete User (Admin Only)",
    description="""
    Delete a user by their ID. (Admin Only):
    
        - This endpoint allows an admin to delete a user from the system by their user ID.
        - If the user is not found, a 404 error is returned. If there is an issue deleting the user, a 500 error is returned.
    """
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = db.query(models.User).filter(models.User.id == user_id).first()
    if deleted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}"
        )
    try:
        db.delete(deleted_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.put(
    '/{user_id}',
    response_model=schemas.UserOutput,
    dependencies=[Depends(check_admin_role)],
    summary="Update User (Admin Only)",
    description="""
    Update user details by their ID. (Admin Only):
    
        - This endpoint allows an admin to update the details of an existing user by their user ID.
        - The request body must include the fields to be updated as defined in the UpdateUser schema.
        - If the user is not found, a 404 error is returned. If there is an issue updating the user, a 500 error is returned."
    """
)
async def update_user(update_user: schemas.UpdateUser, user_id: int, db: Session = Depends(get_db)):
    updated_user = db.query(models.User).filter(models.User.id == user_id).first()
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}"
        )
    try:
        db.query(models.User).filter(models.User.id == user_id).update(
            update_user.dict(), synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )
    return db.query(models.User).filter(models.User.id == user_id).first()
