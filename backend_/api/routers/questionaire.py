"""
Questionnaire Routes Module.

This module provides the endpoints for submitting and retrieving questionnaire entries
associated with projects. It validates the maturity category and category of the entries
based on predefined answer descriptions.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from api.models import models
from api.schemas import schemas
from api.authentication.oauth import get_current_user
from api.utils.answer_description import answer_descriptions

router = APIRouter(tags=['Questionnaire'])

@router.post(
    "/projects/{project_id}/submit_questionnaire", 
    response_model=List[schemas.QuestionnaireEntry],
    summary="Submit Questionnaire Entries",
    description=(
        """Submit Questionnaire Entries: Register questionnaire entries for a specific project.
        
        This endpoint allows the authenticated user to submit questionnaire entries for a specified project.
        The entries are validated based on predefined answer descriptions and then stored in the database.
        
        Args:
        - project_id (int): ID of the project.
        - bulk_entry (schemas.BulkQuestionnaireEntryCreate): Bulk questionnaire entry data.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        
        Returns:
        - List[schemas.QuestionnaireEntry]: The submitted questionnaire entries.
        """
    )
)
async def submit_questionnaire_entries(
    project_id: int,
    bulk_entry: schemas.BulkQuestionnaireEntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db.query(models.QuestionnaireEntry).filter(models.QuestionnaireEntry.project_id == project_id).delete()
    
    db_entries = []
    for entry in bulk_entry.entries:
        if entry.maturity_category not in answer_descriptions:
            raise HTTPException(status_code=400, detail="Invalid maturity category")
        
        category_descriptions = answer_descriptions[entry.maturity_category]
        
        if entry.category not in category_descriptions:
            raise HTTPException(status_code=400, detail="Invalid category")
        
        if not (0 <= entry.answer_number < len(category_descriptions[entry.category])):
            raise HTTPException(status_code=400, detail="Invalid answer number")
        
        description = category_descriptions[entry.category][entry.answer_number]

        db_entry = models.QuestionnaireEntry(
            project_id=project_id,
            category=entry.category,
            maturity_category=entry.maturity_category,
            question_number=entry.question_number,
            answer_number=entry.answer_number,
            description=description,
            user_id=current_user.id
        )

        db.add(db_entry)
        db_entries.append(db_entry)

    db.commit()
    for db_entry in db_entries:
        db.refresh(db_entry)

    return db_entries
@router.get(
    "/{project_id}/questionnaire_entries", 
    response_model=List[schemas.QuestionnaireEntry],
    summary="Get Questionnaire Entries",
    description=(
        """Get Questionnaire Entries: Retrieve questionnaire entries for a specific project.
        
        This endpoint retrieves the questionnaire entries associated with a specified project for
        the authenticated user.
        
        Args:
        - project_id (int): ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        
        Returns:
        - List[schemas.QuestionnaireEntry]: A list of questionnaire entries for the project.
        
        Raises:
        - HTTPException: If no questionnaire entries are found for the project.
        """
    )
)
async def get_questionnaire_entries(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    entries = db.query(models.QuestionnaireEntry).filter(models.QuestionnaireEntry.project_id == project_id).all()

    if not entries:
        raise HTTPException(status_code=404, detail="No questionnaire entries found for the project.")

    return entries
