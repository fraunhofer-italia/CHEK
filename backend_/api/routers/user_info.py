"""
API Routes for User Information.
Author: Elias Niederwieser
Year: 2024
"""
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi import APIRouter
from database import get_db
from api.authentication.oauth import get_current_user
from api.models import models
from api.schemas import schemas

router = APIRouter(prefix='/me', tags=['User Information'])

@router.get(
    '/',
    response_model=schemas.UserOutput,
    summary="Get User Information",
    description=(
        """Get User Information: Retrieve the information for the authenticated user.

        This endpoint returns the details of the currently authenticated user, including their
        user ID, email, and other relevant information stored in the database.
        """
    )
)
async def get_user_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_info = db.query(models.User).filter_by(id=current_user.id).first()
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Information not found"
        )
    return user_info
