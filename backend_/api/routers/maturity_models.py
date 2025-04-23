"""
Maturity Model Routes Module.

This module provides the endpoints related to maturity model entries for the application,
including retrieving entries for organization, technology, information, and process aspects
based on user roles and project IDs.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""
from fastapi import HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from api.models import models
from database import get_db
from api.authentication.oauth import get_current_user, get_current_user_role
from api.schemas.schemas import MaturityModelEntry

router = APIRouter(tags=['Maturity Model'])

@router.get(
    "/get_maturity_entries_organisation",
    summary="Get Maturity Model Organisation Entries",
    description=(
        """Get Maturity Model Organisation Entries: Retrieve the maturity model entries for the organization aspect.

        This endpoint retrieves the maturity model entries associated with a specific project for the current user.
        Admin users can retrieve entries for any project, while regular users can retrieve entries for their own projects.

        Args:
        - project_id (int): The ID of the project to fetch the maturity entries for.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - list: A list of maturity model entries.

        Raises:
        - HTTPException: If the project or maturity entries are not found, or an error occurs during the retrieval.
        """
    ),
    response_model=list[MaturityModelEntry]
)
async def get_maturity_entries_organisation(
    project_id: int = Query(..., description="ID of the project to fetch the maturity entries for."),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if current_user_role == "admin":
            owner_user_id = project.user_id
            entries = db.query(models.MaturityModelOrganisation).filter(
                models.MaturityModelOrganisation.user_id == owner_user_id,
                models.MaturityModelOrganisation.project_id == project_id
            ).all()
        else:
            entries = db.query(models.MaturityModelOrganisation).filter(
                models.MaturityModelOrganisation.user_id == current_user.id,
                models.MaturityModelOrganisation.project_id == project_id
            ).all()

        if not entries:
            raise HTTPException(status_code=404, detail="No maturity entries found for the project.")

        response_data = [
            {
                "label": entry.label,
                "level": entry.level,
                "justification": entry.justification
            }
            for entry in entries
        ]

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/get_maturity_entries_technology",
    summary="Get Maturity Model Technology Entries",
    description=(
        """Get Maturity Model Technology Entries: Retrieve the maturity model entries for the technology aspect.

        This endpoint retrieves the maturity model entries associated with a specific project for the current user.
        Admin users can retrieve entries for any project, while regular users can retrieve entries for their own projects.

        Args:
        - project_id (int): The ID of the project to fetch the maturity entries for.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - list: A list of maturity model entries.

        Raises:
        - HTTPException: If the project or maturity entries are not found, or an error occurs during the retrieval.
        """
    ),
    response_model=list[MaturityModelEntry]
)
async def get_maturity_entries_technology(
    project_id: int = Query(..., description="ID of the project to fetch the maturity entries for."),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if current_user_role == "admin":
            owner_user_id = project.user_id
            entries = db.query(models.MaturityModelTechnology).filter(
                models.MaturityModelTechnology.user_id == owner_user_id,
                models.MaturityModelTechnology.project_id == project_id
            ).all()
        else:
            entries = db.query(models.MaturityModelTechnology).filter(
                models.MaturityModelTechnology.user_id == current_user.id,
                models.MaturityModelTechnology.project_id == project_id
            ).all()
            
        if not entries:
            raise HTTPException(status_code=404, detail="No maturity entries found for the project.")

        response_data = [
            {
                "label": entry.label,
                "level": entry.level,
                "justification": entry.justification
            }
            for entry in entries
        ]

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/get_maturity_entries_information",
    summary="Get Maturity Model Information Entries",
    description=(
        """Get Maturity Model Information Entries: Retrieve the maturity model entries for the information aspect.

        This endpoint retrieves the maturity model entries associated with a specific project for the current user.
        Admin users can retrieve entries for any project, while regular users can retrieve entries for their own projects.

        Args:
        - project_id (int): The ID of the project to fetch the maturity entries for.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - list: A list of maturity model entries.

        Raises:
        - HTTPException: If the project or maturity entries are not found, or an error occurs during the retrieval.
        """
    ),
    response_model=list[MaturityModelEntry]
)
async def get_maturity_entries_information(
    project_id: int = Query(..., description="ID of the project to fetch the maturity entries for."),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if current_user_role == "admin":
            owner_user_id = project.user_id
            entries = db.query(models.MaturityModelInformation).filter(
                models.MaturityModelInformation.user_id == owner_user_id,
                models.MaturityModelInformation.project_id == project_id
            ).all()
        else:
            entries = db.query(models.MaturityModelInformation).filter(
                models.MaturityModelInformation.user_id == current_user.id,
                models.MaturityModelInformation.project_id == project_id
            ).all()
        if not entries:
            raise HTTPException(status_code=404, detail="No maturity entries found for the project.")

        response_data = [
            {
                "label": entry.label,
                "level": entry.level,
                "justification": entry.justification
            }
            for entry in entries
        ]

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/get_maturity_entries_process",
    summary="Get Maturity Model Process Entries",
    description=(
        """Get Maturity Model Process Entries: Retrieve the maturity model entries for the process aspect.

        This endpoint retrieves the maturity model entries associated with a specific project for the current user.
        Admin users can retrieve entries for any project, while regular users can retrieve entries for their own projects.

        Args:
        - project_id (int): The ID of the project to fetch the maturity entries for.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - list: A list of maturity model entries.

        Raises:
        - HTTPException: If the project or maturity entries are not found, or an error occurs during the retrieval.
        """
    ),
    response_model=list[MaturityModelEntry]
)
async def get_maturity_entries_process(
    project_id: int = Query(..., description="ID of the project to fetch the maturity entries for."),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if current_user_role == "admin":
            owner_user_id = project.user_id
            entries = db.query(models.MaturityModelProcess).filter(
                models.MaturityModelProcess.user_id == owner_user_id,
                models.MaturityModelProcess.project_id == project_id
            ).all()
        else:
            entries = db.query(models.MaturityModelProcess).filter(
                models.MaturityModelProcess.user_id == current_user.id,
                models.MaturityModelProcess.project_id == project_id
            ).all()

        if not entries:
            raise HTTPException(status_code=404, detail="No maturity entries found for the project.")

        response_data = [
            {
                "label": entry.label,
                "level": entry.level,
                "justification": entry.justification
            }
            for entry in entries
        ]

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/get_maturity_entries_all_categories",
    summary="Get Maturity Model Entries for All Categories",
    description=(
        """Get Maturity Model Entries for All Categories: Retrieve the label and level for all four categories of maturity model entries (organization, technology, information, and process).

        This endpoint retrieves the maturity model entries associated with a specific project for the current user.
        Admin users can retrieve entries for any project, while regular users can retrieve entries for their own projects.

        Args:
        - project_id (int): The ID of the project to fetch the maturity entries for.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - list: A list of dictionaries containing the label and level for each maturity model entry.

        Raises:
        - HTTPException: If the project or maturity entries are not found, or an error occurs during the retrieval.
        """
    ),
    response_model=list[dict]
)
async def get_maturity_entries_all_categories(
    project_id: int = Query(..., description="ID of the project to fetch the maturity entries for."),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        print(f"Fetching project with ID: {project_id}")
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            print("Project not found.")
            raise HTTPException(status_code=404, detail="Project not found.")
        
        print(f"Project found: {project}")
        
        if current_user_role == "admin":
            owner_user_id = project.user_id
        else:
            owner_user_id = current_user.id
        
        print(f"Owner user ID: {owner_user_id}")

        entries = []
        categories = [models.MaturityModelOrganisation, models.MaturityModelTechnology, models.MaturityModelInformation, models.MaturityModelProcess]

        for category in categories:
            print(f"Fetching entries for category: {category.__name__}")
            category_entries = db.query(category).filter(
                category.user_id == owner_user_id,
                category.project_id == project_id
            ).all()
            
            print(f"Entries found: {category_entries}")

            for entry in category_entries:
                entries.append({
                    "label": entry.label,
                    "level": entry.level
                })

        if not entries:
            print("No maturity entries found for the project.")
            raise HTTPException(status_code=404, detail="No maturity entries found for the project.")

        print(f"Entries to return: {entries}")
        return entries

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

