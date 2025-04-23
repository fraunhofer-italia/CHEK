"""
Extraction and Evaluation AI Routes Module.

This module provides the AI-based extraction and evaluation endpoints for the application, 
including extracting information from BPMN files and evaluating maturity models.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

from typing import Optional

from fastapi import HTTPException, Depends, APIRouter, Query # type: ignore
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_tools.intellichek.evaluation_technology import evaluate_technology
from ai_tools.intellichek.evaluation_information import evaluate_information
from ai_tools.intellichek.evaluation_process import evaluate_process
from ai_tools.intellichek.extraction import extraction_process
from ai_tools.intellichek.helpers import sanitize_bpmn
from api.utils.helpers import get_last_bpmn_data_for_user, get_last_bpmn_extraction_for_user
from langchain.chat_models import ChatOpenAI
import config
from api.models import models
from database import get_db
from api.authentication.oauth import get_current_user

router = APIRouter(tags=['Extraction and Evaluation AI'])

openai_api_key = config.OPENAI_API_KEY 

if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables.")

model = ChatOpenAI(temperature=float(config.TEMPERATURE), model=config.GPT_MODEL)

class ChatMessage(BaseModel):
    """Model representing the input string for A.I. conversation."""
    human_message: str

class Maturity(BaseModel):
    """Model representing the input string for A.I. conversation."""
    action: str
    description: str

class UserChatSettings(BaseModel):
    """Model representing user-specific settings for A.I. conversation."""
    language: Optional[str] = "English"
    diagram_id: Optional[str] = None

class UserChatLanguage(BaseModel):
    """Model representing user-specific settings for A.I. conversation."""
    language: Optional[str] = "English"

class ProcessDescriptionRequest(BaseModel):
    file_content: str
    glossary_content: str
    chat_settings: UserChatSettings

@router.post(
    "/extraction", 
    summary="Extract relevant information from the BPMN file",
    description=(
        """Extract BPMN Data: Extract relevant information from the BPMN file.

        This endpoint extracts and sanitizes the last saved BPMN data associated with a specific project for the 
        current user. The extracted information is then saved and associated with the project.

        Args:
        - chat_message (ChatMessage): The chat message content for extraction.
        - chat_settings (UserChatSettings): User-specific chat settings.
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the extracted information and diagram ID.

        Raises:
        - HTTPException: If no BPMN data is found, the project is not found, or an error occurs during the extraction.
        """
    ),
    response_model=dict
)
async def extract_bpmn_data(
    chat_message: ChatMessage, 
    chat_settings: UserChatSettings, 
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN data for."),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        last_saved_data = get_last_bpmn_data_for_user(db, current_user.id, project_id)
  
        if not last_saved_data:
            raise HTTPException(status_code=404, detail="No BPMN data found for the project.")
        
        sanitized_data = sanitize_bpmn(last_saved_data.content)
        response, total_cost = await extraction_process(sanitized_data, chat_settings.language, model)

        project = db.query(models.Project).filter(models.Project.id == project_id).first()
       
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        bpmn_extracted = db.query(models.BPMNExtraction).filter(models.BPMNExtraction.project_id == project.id).first()
        
        if not bpmn_extracted:
            bpmn_extracted = models.BPMNExtraction(content=response, project_id=project.id, user=current_user)
            db.add(bpmn_extracted)
        else:
            bpmn_extracted.content = response

        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)

        db.commit()
        return {"message": response, "diagram_id": chat_settings.diagram_id}

    except HTTPException as http_error:
        db.rollback()
        raise http_error

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/extraction",
    summary="Retrieve the last BPMN extraction content for a specific project",
    description=(
        """Get Last BPMN Extraction: Retrieve the most recent BPMN extraction content for a specific project.

        This endpoint retrieves the last saved BPMN extraction content associated with a given project ID
        for the current user.

        Args:
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the last BPMN extraction content.

        Raises:
        - HTTPException: If the project or extraction content is not found, or an error occurs during the retrieval.
        """
    ),
    response_model=dict
)
def get_last_bpmn_extraction_content(
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN extraction content for."),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
    
        bpmn_extracted = db.query(models.BPMNExtraction)\
                           .filter(models.BPMNExtraction.project_id == project_id,
                                   models.BPMNExtraction.user_id == current_user.id)\
                           .first()
  
        if not bpmn_extracted:
            raise HTTPException(status_code=404, detail="No BPMN extraction content found for the project and user.")
        
        return {"message": bpmn_extracted.content}

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post(
    "/evaluate_technology", 
    summary="Maturity Model Technology",
    description=(
        """Evaluate Technology Maturity Model: Evaluate and save technology maturity model data.

        This endpoint uses the last saved BPMN data associated with a specific project to evaluate and 
        save the technology maturity model data for the current user.

        Args:
        - chat_message (ChatMessage): Chat message content for evaluation.
        - chat_settings (UserChatSettings): User chat settings.
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the evaluated data and diagram ID.

        Raises:
        - HTTPException: If no BPMN extraction is found, the project is not found, or an error occurs during the evaluation.
        """
    ),
    response_model=dict
)
async def add_string_maturity(
    chat_message: ChatMessage, 
    chat_settings: UserChatSettings, 
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN data for."),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        last_saved_extraction = get_last_bpmn_extraction_for_user(db, current_user.id, project_id)
  
        if not last_saved_extraction:
            raise HTTPException(status_code=404, detail="No BPMN extraction found for the project.")
        
        result = last_saved_extraction.content
        response, total_cost = await evaluate_technology(result, chat_settings.language, model)
        
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        db.query(models.MaturityModelTechnology).filter(
            models.MaturityModelTechnology.user_id == current_user.id,
            models.MaturityModelTechnology.project_id == project_id
        ).delete()

        response_data = []
        for chat_message in response:
            label = chat_message.get("Label")
            level = chat_message.get("Level")
            justification = chat_message.get("Justification")
            response_data.append({
                "label": label,
                "level": level,
                "justification": justification
            })

        model_instances = [
            models.MaturityModelTechnology(
                label=data["label"],
                level=int(data["level"]),
                justification=data["justification"],
                user_id=current_user.id,
                project_id=project_id
            )
            for data in response_data
        ]

        for instance in model_instances:
            db.add(instance)

        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()

        return {"message": response, "diagram_id": chat_settings.diagram_id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post(
    "/evaluate_information", 
    summary="Maturity Model Information",
    description=(
        """Evaluate Information Maturity Model: Evaluate and save information maturity model data.

        This endpoint uses the last saved BPMN data associated with a specific project to evaluate and 
        save the information maturity model data for the current user.

        Args:
        - chat_message (ChatMessage): Chat message content for evaluation.
        - chat_settings (UserChatSettings): User chat settings.
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the evaluated data and diagram ID.

        Raises:
        - HTTPException: If no BPMN extraction is found, the project is not found, or an error occurs during the evaluation.
        """
    ),
    response_model=dict
)
async def add_string_maturity(
    chat_message: ChatMessage, 
    chat_settings: UserChatSettings, 
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN data for."),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        last_saved_extraction = get_last_bpmn_extraction_for_user(db, current_user.id, project_id)
  
        if not last_saved_extraction:
            raise HTTPException(status_code=404, detail="No BPMN extraction found for the project.")
        
        result = last_saved_extraction.content
        response, total_cost = await evaluate_information(result, chat_settings.language, model)
        print(response)
      

        db.query(models.MaturityModelInformation).filter(
            models.MaturityModelInformation.user_id == current_user.id,
            models.MaturityModelInformation.project_id == project_id
        ).delete()

        response_data = []
        for message in response:
            label = message.get("Label")
            level = message.get("Level")
            justification = message.get("Justification")
            response_data.append({
                "label": label,
                "level": level,
                "justification": justification
            })

        for data in response_data:
            existing_entry = db.query(models.MaturityModelInformation).filter(
                models.MaturityModelInformation.user_id == current_user.id,
                models.MaturityModelInformation.project_id == project_id,
                models.MaturityModelInformation.label == data["label"]
            ).first()

            if existing_entry:
                existing_entry.level = data["level"]
                existing_entry.justification = data["justification"]
                db.add(existing_entry)
            else:
                new_entry = models.MaturityModelInformation(
                    label=data["label"],
                    level=data["level"],
                    justification=data["justification"],
                    user_id=current_user.id,
                    project_id=project_id
                )
                db.add(new_entry)

        entries = db.query(models.QuestionnaireEntry).filter(
            models.QuestionnaireEntry.user_id == current_user.id,
            models.QuestionnaireEntry.project_id == project_id,
            models.QuestionnaireEntry.maturity_category == "Information"
        ).all()

        for entry in entries:
            existing_entry = db.query(models.MaturityModelInformation).filter(
                models.MaturityModelInformation.user_id == current_user.id,
                models.MaturityModelInformation.project_id == project_id,
                models.MaturityModelInformation.label == entry.category
            ).first()

            if existing_entry:
                existing_entry.level = entry.answer_number
                existing_entry.justification = entry.description
                db.add(existing_entry)
            else:
                new_entry = models.MaturityModelInformation(
                    label=entry.category,
                    level=entry.answer_number,
                    justification=entry.description,
                    user_id=current_user.id,
                    project_id=project_id
                )
                db.add(new_entry)

        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()

        combined_results = db.query(models.MaturityModelInformation).filter(
            models.MaturityModelInformation.user_id == current_user.id,
            models.MaturityModelInformation.project_id == project_id
        ).all()

        response_data = [
            {
                "label": entry.label,
                "level": entry.level,
                "justification": entry.justification
            }
            for entry in combined_results
        ]

        return {"message": "Information maturity data evaluated and saved successfully", "data": response_data}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post(
    "/evaluate_process", 
    summary="Maturity Model Process",
    description=(
        """Evaluate Process Maturity Model: Evaluate and save process maturity model data.

        This endpoint uses the last saved BPMN data associated with a specific project to evaluate and 
        save the process maturity model data for the current user.

        Args:
        - chat_message (ChatMessage): Chat message content for evaluation.
        - chat_settings (UserChatSettings): User chat settings.
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the evaluated data and diagram ID.

        Raises:
        - HTTPException: If no BPMN extraction is found, the project is not found, or an error occurs during the evaluation.
        """
    ),
    response_model=dict
)
async def add_string_maturity(
    chat_message: ChatMessage, 
    chat_settings: UserChatSettings, 
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN data for."),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        last_saved_extraction = get_last_bpmn_extraction_for_user(db, current_user.id, project_id)
  
        if not last_saved_extraction:
            raise HTTPException(status_code=404, detail="No BPMN extraction found for the project.")
        
        result = last_saved_extraction.content
        response, total_cost = await evaluate_process(result, chat_settings.language, model)
        
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        db.query(models.MaturityModelProcess).filter(
            models.MaturityModelProcess.user_id == current_user.id,
            models.MaturityModelProcess.project_id == project_id
        ).delete()

        response_data = []
        for chat_message in response:
            label = chat_message.get("Label")
            level = chat_message.get("Level")
            justification = chat_message.get("Justification")
            response_data.append({
                "label": label,
                "level": level,
                "justification": justification
            })

        model_instances = [
            models.MaturityModelProcess(
                label=data["label"],
                level=int(data["level"]),
                justification=data["justification"],
                user_id=current_user.id,
                project_id=project_id
            )
            for data in response_data
        ]

        for instance in model_instances:
            db.add(instance)

        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()

        return {"message": response, "diagram_id": chat_settings.diagram_id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post(
    "/evaluate_organisation",
    summary="Maturity Model Organisation",
    description=(
        """Evaluate Organisation Maturity Model: Evaluate and save organisation maturity model data.

        This endpoint evaluates and saves the organisation maturity model data based on questionnaire entries 
        for a specific project and user.

        Args:
        - project_id (int): The ID of the project.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the evaluated data.

        Raises:
        - HTTPException: If no questionnaire entries are found, the project is not found, or an error occurs during the evaluation.
        """
    ),
    response_model=dict
)
async def evaluate_organisation(
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN data for."),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        entries = db.query(models.QuestionnaireEntry).filter(
            models.QuestionnaireEntry.user_id == current_user.id,
            models.QuestionnaireEntry.project_id == project_id,
            models.QuestionnaireEntry.maturity_category == "Organization"
        ).all()

        if not entries:
            raise HTTPException(status_code=404, detail="No questionnaire entries found for the project and user in the Organization category.")

        db.query(models.MaturityModelOrganisation).filter(
            models.MaturityModelOrganisation.user_id == current_user.id,
            models.MaturityModelOrganisation.project_id == project_id
        ).delete()

        model_instances = [
            models.MaturityModelOrganisation(
                label=entry.category,
                level=entry.answer_number,
                justification=entry.description,
                user_id=current_user.id,
                project_id=project_id
            )
            for entry in entries
        ]

        for instance in model_instances:
            db.add(instance)

        db.commit()

        response_data = [
            {
                "label": instance.label,
                "level": instance.level,
                "justification": instance.justification
            }
            for instance in model_instances
        ]

        return {"message": "Organisation maturity data evaluated and saved successfully", "data": response_data}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
