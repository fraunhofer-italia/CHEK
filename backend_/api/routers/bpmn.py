"""
BPMN Management Routes Module.

This module provides the BPMN management endpoints for the application, including
creating, updating, retrieving, and deleting BPMN templates and data. It ensures that actions 
are performed based on user roles, with appropriate permissions for admin and regular users.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models import models
from api.schemas import schemas
from fastapi import APIRouter
from database import get_db
from api.authentication.oauth import get_current_user

router = APIRouter(tags=['BPMN'])

@router.post(
    "/bpm_templates/",
    summary="Save Process Maps Templates in the BD",
    description=(
        """Save Process Maps Templates: Store BPMN data as templates.

        This endpoint allows admin users to save BPMN templates in the database. These templates can be used 
        as starting points for new projects or processes.

        Args:
        - template (schemas.BPMNTemplateSchema): The BPMN template data to be saved.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A message indicating the success of the operation.

        Raises:
        - HTTPException: If the user is not authorized or an error occurs during the save operation.
        """
    )
)
def create_template(
    template: schemas.BPMNTemplateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to save templates.")
    
        db_template = models.BPMNTemplate(**template.dict())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return {"message": "BPMN template saved successfully."}
    except SQLAlchemyError as e: 
        db.rollback()
        raise HTTPException(status_code=500, detail=repr(e))
    finally:
        db.close()

@router.get(
    "/bpm_templates/",
    summary="Get all BPMN templates",
    description=(
        """Get All BPMN Templates: Retrieve all stored BPMN templates.

        This endpoint allows admin users to retrieve all BPMN templates stored in the database. These templates
        can be used as references or starting points for new projects.

        Args:
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - List[schemas.BPMNTemplate]: A list of BPMN templates.

        Raises:
        - HTTPException: If the user is not authorized to access the templates.
        """
    )
)
def get_all_templates(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to access all templates.")
    
    templates = db.query(models.BPMNTemplate).all()
    return templates

@router.get(
    "/bpm_templates/{template_id}",
    summary="Get a specific BPMN template",
    description=(
        """Get BPMN Template: Retrieve a specific BPMN template by its ID.

        This endpoint allows users to retrieve the details of a specific BPMN template by its ID.

        Args:
        - template_id (int): The ID of the BPMN template to be retrieved.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - schemas.BPMNTemplate: The details of the BPMN template.

        Raises:
        - HTTPException: If the template is not found.
        """
    )
)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    template = db.query(models.BPMNTemplate).filter(models.BPMNTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put(
    "/bpm_templates/{template_id}",
    summary="Update a BPMN template",
    description=(
        """Update BPMN Template: Modify a specific BPMN template by its ID.

        This endpoint allows admin users to update the details of an existing BPMN template.

        Args:
        - template_id (int): The ID of the BPMN template to be updated.
        - template (schemas.BPMNTemplateSchema): The updated BPMN template data.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A message indicating the success of the operation.

        Raises:
        - HTTPException: If the template is not found or the user is not authorized to update templates.
        """
    )
)
def update_template(
    template_id: int,
    template: schemas.BPMNTemplateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_template = db.query(models.BPMNTemplate).filter(models.BPMNTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to update templates.")
    
    for key, value in template.dict().items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return {"message": "BPMN template updated successfully."}

@router.delete(
    "/bpm_templates/{template_id}",
    summary="Delete a BPMN template",
    description=(
        """Delete BPMN Template: Remove a specific BPMN template by its ID.

        This endpoint allows admin users to delete a BPMN template from the database.

        Args:
        - template_id (int): The ID of the BPMN template to be deleted.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A message indicating the success of the operation.

        Raises:
        - HTTPException: If the template is not found or the user is not authorized to delete templates.
        """
    )
)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_template = db.query(models.BPMNTemplate).filter(models.BPMNTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to delete templates.")
    
    db.delete(db_template)
    db.commit()
    return {"message": "BPMN template deleted successfully."}

@router.post(
    "/autosave/",
    summary="Autosave BPMN Data",
    description=(
        """Autosave BPMN Data: Save BPMN data associated with a project.

        This endpoint allows the authenticated user to autosave BPMN data for a specific project.

        Args:
        - bpmn_data (schemas.BPMNDataSchema): The BPMN data to be saved.
        - project_id (str): The ID of the project to associate the BPMN data with.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A message indicating the success of the operation.

        Raises:
        - HTTPException: If the project is not found, the user is not authorized, or an error occurs during the save operation.
        """
    )
)
async def autosave_bpmn(
    bpmn_data: schemas.BPMNDataSchema,
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        if current_user.role != "admin" and project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to save data for this project.")

        db_entry = models.BPMNData(content=bpmn_data.bpmnData, project_id=project.id)
        db.add(db_entry)
        db.commit()

        return {"message": "BPMN data saved successfully."}

    except SQLAlchemyError as e: 
        db.rollback()
        raise HTTPException(status_code=500, detail=repr(e))
    finally:
        db.close()

@router.get(
    "/lastsave/{project_id}/",
    summary="Get Last Saved BPMN Data",
    description=(
        """Get Last Saved BPMN Data: Retrieve the last saved version of BPMN data for a project.

        This endpoint allows the authenticated user to retrieve the most recent BPMN data associated with a specific project.

        Args:
        - project_id (str): The ID of the project to retrieve the BPMN data for.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: The last saved BPMN data.

        Raises:
        - HTTPException: If the project is not found, the user is not authorized, or an error occurs during the retrieval operation.
        """
    )
)
async def get_last_saved_bpmn(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        if current_user.role != "admin" and project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to access data for this project.")

        last_saved_data = db.query(models.BPMNData).filter(models.BPMNData.project_id == project.id).order_by(models.BPMNData.created_at.desc()).first()
        
        if not last_saved_data:
            return {"message": "No BPMN data found for the project."}

        return {"bpmnData": last_saved_data.content}

    except SQLAlchemyError as e: 
        raise HTTPException(status_code=500, detail=repr(e))
    finally:
        db.close()
