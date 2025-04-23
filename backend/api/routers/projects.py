"""
Project Management Routes Module.

This module provides the project management endpoints for the application, including
creating, updating, retrieving, and deleting projects. It ensures that actions are performed
based on user roles, with appropriate permissions for admin and regular users.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""
from fastapi import HTTPException, Depends, status, APIRouter, File, UploadFile
from typing import List, Dict
from sqlalchemy.orm import Session
from database import get_db
from api.authentication.oauth import get_current_user, get_current_user_role
from api.models import models
from api.schemas import schemas
import os
import shutil

router = APIRouter(tags=['Project'])

@router.post(
    '/',
    response_model=schemas.Project,
    summary="Create a new project",
    description=(
        """Create a New Project: Register a new project for the authenticated user.
        
        This endpoint allows the authenticated user to create a new project. The user needs
        to provide the project details which will be stored in the database. The project is
        associated with the authenticated user.
        
        Args:
        - project (schemas.ProjectCreate): The project details to be created.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        
        Returns:
        - schemas.Project: The created project.
        """
    )
)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing_project = db.query(models.Project).filter_by(user_id=current_user.id).first()
    new_project = models.Project(**project.dict(), user_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.put(
    '/{project_id}',
    response_model=schemas.Project,
    summary="Update a project (User and Admin Permissions)",
    description=(
        """Update a Project: Modify an existing project based on user permissions.
        
        This endpoint allows the authenticated user or admin to update the details of an existing project.
        The user can update their own projects, while an admin can update any project.
        
        Args:
        - project_id (int): The ID of the project to be updated.
        - project (schemas.ProjectUpdate): The updated project details.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.
        
        Returns:
        - schemas.Project: The updated project.
        """
    )
)
def update_project(
    project_id: int,
    project: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
):
    if current_user_role == "admin":
        existing_project = db.query(models.Project).filter_by(id=project_id).first()
    else:
        existing_project = db.query(models.Project).filter_by(user_id=current_user.id, id=project_id).first()

    if not existing_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_project, field, value)

    db.commit()
    db.refresh(existing_project)
    return existing_project

@router.get(
    '/',
    response_model=List[schemas.Project],
    summary="Get projects (User and Admin Permissions)",
    description=(
        """Get Projects: Retrieve projects based on user role.
        
        This endpoint allows the authenticated user to retrieve a list of their own projects,
        while an admin can retrieve all projects in the system.
        
        Args:
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.
        
        Returns:
        - List[schemas.Project]: A list of projects based on user role.
        """
    )
)
def get_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
):
    if current_user.role == "admin":
        projects_query = db.query(models.Project)
    else:
        projects_query = db.query(models.Project).filter(models.Project.user_id == current_user.id)

    projects = projects_query.all()
    if not projects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")

    return projects

@router.get(
    '/{project_id}',
    response_model=schemas.Project,
    summary="Get One Project (User and Admin Permissions)",
    description=(
        """Get One Project: Retrieve details of a single project by its ID.
        
        This endpoint allows the authenticated user to retrieve details of their own project by its ID,
        while an admin can retrieve details of any project.
        
        Args:
        - project_id (int): The ID of the project to be retrieved.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.
        
        Returns:
        - schemas.Project: Details of the specified project.
        """
    )
)
def get_one_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
):
    if current_user_role == "admin":
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
    else:
        project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.user_id == current_user.id).first()

    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project not found with id: {project_id}")

    return project

@router.delete(
    '/{project_id}',
    response_model=schemas.Project,
    summary="Delete a project (User and Admin Permissions)",
    description=(
        """Delete a Project: Remove a project based on user permissions.
        
        This endpoint allows the authenticated user to delete their own project,
        while an admin can delete any project. It also removes associated files from the server.
        
        Args:
        - project_id (int): The ID of the project to be deleted.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.
        
        Returns:
        - schemas.Project: The deleted project.
        """
    )
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
):
    if current_user_role == "admin":
        project = db.query(models.Project).filter_by(id=project_id).first()
    else:
        project = db.query(models.Project).filter_by(id=project_id, user_id=current_user.id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.building_permit_instructions:
        file_path = project.building_permit_instructions
        project_directory = os.path.dirname(file_path)
        if os.path.exists(project_directory):
            try:
                shutil.rmtree(project_directory)
                print(f"Deleted directory: {project_directory}")
            except Exception as e:
                print(f"Failed to delete directory {project_directory}: {str(e)}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete project files")

    db.delete(project)
    db.commit()
    return project

@router.post(
    "/{project_id}/upload_text",
    summary="Upload Text File and Update Project",
    response_model=Dict[str, str],
    description=(
        """Upload Text File and Update Project: Upload a text file to a project and update its details.
        
        This endpoint allows the authenticated user to upload a text file and associate it with an existing project.
        The file is stored on the server, and the project's details are updated accordingly.
        
        Args:
        - project_id (int): The ID of the project to be updated.
        - file (UploadFile): The text file to be uploaded.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        
        Returns:
        - dict: A message indicating the success of the operation.
        
        Raises:
        - HTTPException: If the file is not a .txt file, the project is not found, or an error occurs during file upload.
        """
    )
)
def upload_text_file(
    project_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are accepted")

        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="User does not have access to this project")

        user_folder_name = f'{current_user.id}'
        sanitized_project_name = project.name.replace(" ", "_").replace("/", "_")
        file_path = f'./uploads/{user_folder_name}/{sanitized_project_name}/'
        os.makedirs(file_path, exist_ok=True)
        
        file_name = f'{file_path}user_process_description.txt'
      
        file_content = file.file.read()
        with open(file_name, 'wb') as f:
            f.write(file_content)

        project.building_permit_instructions = file_name
        db.add(project)
        db.commit()

        return {"message": "File uploaded and project updated successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
