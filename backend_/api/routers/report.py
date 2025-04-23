"""
Results and Report Routes Module.

This module provides the endpoints related to results and report generation for the application,
including creating and retrieving reports for As-Is processes and maturity models based on user roles and project IDs.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

from typing import Optional
from fastapi import HTTPException, Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ai_tools.intellichek.report import generate_maturity_model_report, generate_building_permit_report, generate_roadmap_report
from api.utils.helpers import get_last_bpmn_data_for_user
from ai_tools.intellichek.helpers import sanitize_bpmn, write_response_to_file
from langchain.chat_models import ChatOpenAI
import config
from api.models import models
from database import get_db
from api.authentication.oauth import get_current_user, get_current_user_role, check_admin_role
import os


openai_api_key = config.OPENAI_API_KEY 
if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables.")
model = ChatOpenAI(temperature=float(config.TEMPERATURE), model=config.GPT_MODEL)

router = APIRouter(tags=['Results and Report'])

class Maturity(BaseModel):
    """Model representing the input string for A.I. conversation."""
    action: str
    description: str

class UserChatSettings(BaseModel):
    """Model representing user-specific settings for A.I. conversation."""
    language: Optional[str] = "English"


def write_response_to_file(response: str, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(response)


@router.post(
    "/as_is_process/{project_id}",
    summary="Create Report from the BPMN file/As-Is Process Map",
    description=(
        """Create Report from BPMN File/As-Is Process Map: Generate a report based on the BPMN data.

        This endpoint generates a summary report from the last saved BPMN data associated with a specific project 
        for the current user. The report is saved and associated with the project.

        Args:
        - chat_settings (UserChatSettings): User-specific chat settings.
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the generated report.

        Raises:
        - HTTPException: If no BPMN data is found, the project is not found, or an error occurs during the process.
        """
    ),
    response_model=dict
)
def create_as_is_report(
    chat_settings: UserChatSettings, 
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        last_saved_data = get_last_bpmn_data_for_user(db, current_user.id, project_id)
  
        if not last_saved_data:
            raise HTTPException(status_code=404, detail="No BPMN data found for the project.")
        
        sanitized_data = sanitize_bpmn(last_saved_data.content)
        response, total_cost = generate_building_permit_report(sanitized_data, chat_settings.language, model)
        
        write_response_to_file(response, './test/as_is_report.txt')
        
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
       
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        report_as_is = models.ReportAsIs(content=response, user=current_user, project=project)
        db.add(report_as_is)

        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)

        db.commit()
        return {"message": response}

    except HTTPException as http_error:
        db.rollback()
        raise http_error

@router.get(
    "/as_is_process/{project_id}",
    summary="Get the last As-Is Report for a given project ID",
    description=(
        """Get Last As-Is Report: Retrieve the most recent As-Is report for a specific project.

        This endpoint retrieves the last saved As-Is report content associated with a given project ID.
        Admin users can retrieve reports for any project, while regular users can retrieve reports for their own projects.

        Args:
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - dict: A dictionary containing the last As-Is report content.

        Raises:
        - HTTPException: If the project or report content is not found, or an error occurs during the retrieval.
        """
    ),
    response_model=dict
)
def get_as_is_report(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if current_user.role == "admin":
            owner_user_id = project.user_id
            
            last_content = (
                db.query(models.ReportAsIs)
                .filter(
                    models.ReportAsIs.project_id == project_id,
                    models.ReportAsIs.user_id == owner_user_id
                )
                .order_by(models.ReportAsIs.id.desc())
                .first()
            )
        else:
             
            last_content = (
                db.query(models.ReportAsIs)
                .filter(
                    models.ReportAsIs.project_id == project_id,
                    models.ReportAsIs.user_id == current_user.id
                )
                .order_by(models.ReportAsIs.id.desc())
                .first()
            )
            

        if not last_content:
            raise HTTPException(status_code=404, detail="No content found for the project.")

        return {"last_content": last_content.content}

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post(
    "/maturity/{project_id}",
    summary="Create Report for Maturity Model",
    description=(
        """Create Maturity Model Report: Generate and store a summary report for the maturity model.

        This endpoint generates a summary report for the maturity model aspects (technology, information,
        process, and organization) associated with a specified project and user. The report is saved and 
        associated with the project.

        Args:
        - chat_settings (UserChatSettings): User-specific chat settings.
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the generated report.

        Raises:
        - HTTPException: If the project is not found, or an error occurs during the process.
        """
    ),
    response_model=dict
)
def create_maturity_model_report(
    chat_settings: UserChatSettings, 
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
       
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        maturity_model_technologies = db.query(models.MaturityModelTechnology).filter(
            models.MaturityModelTechnology.project_id == project_id,
            models.MaturityModelTechnology.user_id == current_user.id
        ).all()

        maturity_model_information = db.query(models.MaturityModelInformation).filter(
            models.MaturityModelInformation.project_id == project_id,
            models.MaturityModelInformation.user_id == current_user.id
        ).all()

        maturity_model_process = db.query(models.MaturityModelProcess).filter(
            models.MaturityModelProcess.project_id == project_id,
            models.MaturityModelProcess.user_id == current_user.id
        ).all()

        maturity_model_organisation = db.query(models.MaturityModelOrganisation).filter(
            models.MaturityModelOrganisation.project_id == project_id,
            models.MaturityModelOrganisation.user_id == current_user.id
        ).all()

        all_models = maturity_model_technologies + maturity_model_information + maturity_model_process + maturity_model_organisation

        if all_models:
            summary_string = ""
            for modela in all_models:
                if isinstance(modela, models.MaturityModelTechnology):
                    keyword = "Technology"
                elif isinstance(modela, models.MaturityModelInformation):
                    keyword = "Information"
                elif isinstance(modela, models.MaturityModelProcess):
                    keyword = "Process"
                elif isinstance(modela, models.MaturityModelOrganisation):
                    keyword = "Organisation"
                else:
                    keyword = "Unknown"

                summary_string += (
                    f"{keyword}: {modela.label} has the maturity level {modela.level} "
                    f"according to the justification {modela.justification}. "
                )

            response, total_cost = generate_maturity_model_report(summary_string, chat_settings.language, model)
            write_response_to_file(response, './test/maturity_report.txt')
            print(model)
            report_maturity = models.ReportMaturity(content=response, user=current_user, project=project)
           
            chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
            
            db.add(report_maturity)
            db.add(chat_info)

            db.commit()
            return {"message": response}
        else:
            return {"message": "No data found for the specified project and user."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/maturity/{project_id}",
    summary="Get the Maturity Report for a given project ID",
    description=(
        """Get Maturity Report: Retrieve the most recent maturity report for a specific project.

        This endpoint retrieves the last saved maturity report content associated with a given project ID.
        Admin users can retrieve reports for any project, while regular users can retrieve reports for their own projects.

        Args:
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - dict: A dictionary containing the last maturity report content.

        Raises:
        - HTTPException: If the project or report content is not found, or an error occurs during the retrieval.
        """
    ),
    response_model=dict
)
def get_maturity_model_report(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if current_user.role == "admin":
            owner_user_id = project.user_id
            last_content = (
                db.query(models.ReportMaturity)
                .filter(
                    models.ReportMaturity.project_id == project_id,
                    models.ReportMaturity.user_id == owner_user_id
                )
                .order_by(models.ReportMaturity.id.desc())
                .first()
            )
        else:    
            last_content = (
                db.query(models.ReportMaturity)
                .filter(
                    models.ReportMaturity.project_id == project_id,
                    models.ReportMaturity.user_id == current_user.id
                )
                .order_by(models.ReportMaturity.id.desc())
                .first()
            )

        if not last_content:
            raise HTTPException(status_code=404, detail="No content found for the project.")

        return {"last_content": last_content.content}

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post(
    "/roadmap/{project_id}",
    summary="Create Roadmap Report",
    description=(
        """Create Roadmap Report: Generate and store a summary report for the roadmap.

        This endpoint generates a summary report based on the roadmap data (including KMA, start and end dates,
        dependencies, actions, and check tools) associated with a specified project and user. The report is saved
        and associated with the project.

        Args:
        - chat_settings (UserChatSettings): User-specific chat settings.
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the generated report.

        Raises:
        - HTTPException: If the project is not found, or an error occurs during the process.
        """
    ),
    response_model=dict
)
def create_roadmap_report(
    chat_settings: UserChatSettings, 
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        roadmaps_db = db.query(models.Roadmap).filter(
            models.Roadmap.project_id == project_id,
          #  models.Roadmap.user_id == current_user.id
        ).all()

        if not roadmaps_db:
            return {"message": "No data found for the specified project and user."}
        roadmap_data = []
        for roadmap in roadmaps_db:
            roadmap_info = {
                "kma": roadmap.kma,
                "start_date": roadmap.start_date,
                "end_date": roadmap.end_date,
                "dependencies": roadmap.dependencies,
                "actions": roadmap.actions,
                "check_tools": roadmap.chek_tools
            }
            roadmap_data.append(roadmap_info)

        roadmap_db_string = "\n".join([str(r) for r in roadmap_data])
        response, total_cost = generate_roadmap_report(roadmap_db_string, chat_settings.language, model)
        write_response_to_file(response, './test/roadmap_report.txt')
        report_roadmap = models.ReportRoadmap(content=response, user=current_user, project=project)
        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)

        db.add(report_roadmap)
        db.add(chat_info)
        db.commit()

        return {"message": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/roadmap/{project_id}",
    summary="Get Roadmap Report for a Given Project ID",
    description=(
        """Get Roadmap Report: Retrieve the most recent roadmap report for a specific project.

        This endpoint retrieves the last saved roadmap report content associated with a given project ID.
        Admin users can retrieve reports for any project, while regular users can retrieve reports for their own projects.

        Args:
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.
        - current_user_role (str): Authenticated user's role dependency.

        Returns:
        - dict: A dictionary containing the last roadmap report content.

        Raises:
        - HTTPException: If the project or report content is not found, or an error occurs during the retrieval.
        """
    ),
    response_model=dict
)
def get_roadmap_report(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if current_user.role == "admin":
            owner_user_id = project.user_id
            last_content = (
                db.query(models.ReportRoadmap)
                .filter(
                    models.ReportRoadmap.project_id == project_id,
                    models.ReportRoadmap.user_id == owner_user_id
                )
                .order_by(models.ReportRoadmap.id.desc())
                .first()
            )
        else:    
            last_content = (
                db.query(models.ReportRoadmap)
                .filter(
                    models.ReportRoadmap.project_id == project_id,
                    models.ReportRoadmap.user_id == current_user.id
                )
                .order_by(models.ReportRoadmap.id.desc())
                .first()
            )

        if not last_content:
            raise HTTPException(status_code=404, detail="No content found for the project.")

        return {"last_content": last_content.content}

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
