"""
Prices Management Routes Module.

This module provides the endpoints related to price calculations for the application,
including retrieving the sum of spend money for OpenAI tokens based on user roles.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.models import models
from database import get_db
from api.authentication.oauth import get_current_user, get_current_user_role

router = APIRouter(tags=['Prices'])

@router.get(
    "/get_price",
    summary="Get sum of spend money for OPENAI token",
    description=(
        """Get Sum of Spend Money: Retrieve the total spend money for OpenAI tokens based on user role.

        This endpoint calculates the total spend money for OpenAI tokens. If the user has an admin role, 
        it retrieves the sum for all users; otherwise, it retrieves the sum for the authenticated user only.

        Args:
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.
        - db (Session): Database session dependency.

        Returns:
        - dict: A dictionary containing the total spend money.

        Raises:
        - HTTPException: If an error occurs during the process.
        """
    )
)
def get_price(
    current_user: models.User = Depends(get_current_user), 
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    if current_user_role == "admin":
        total_price = db.query(models.ChatInfo).all()
    else:
        total_price = db.query(models.ChatInfo).filter(models.ChatInfo.user_id == current_user.id).all()
    return {"total_price": total_price}

@router.get(
    "/get_total_price",
    summary="Get total spend money for OPENAI token",
    description=(
        """Get Total Spend Money: Retrieve the total spend money for OpenAI tokens based on user role.

        This endpoint calculates the total spend money for OpenAI tokens. If the user has an admin role, 
        it retrieves the total spend money for all users; otherwise, it retrieves the total spend money 
        for the authenticated user only.

        Args:
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.
        - db (Session): Database session dependency.

        Returns:
        - dict: A dictionary containing the total spend money.

        Raises:
        - HTTPException: If an error occurs during the process.
        """
    )
)
def get_total_price(
    current_user: models.User = Depends(get_current_user), 
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    if current_user_role == "admin":
        total_price = db.query(models.ChatInfo).all()
    else:
        total_price = db.query(models.ChatInfo).filter(models.ChatInfo.user_id == current_user.id).all()
 
    sum_total_price = sum(price.total_cost for price in total_price)
    return {"total_price": sum_total_price}
