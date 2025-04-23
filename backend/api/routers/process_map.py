"""
Process Map AI Routes Module.

This module provides the AI-based process mapping endpoints for the application, including
various AI evaluations and transformations for user input, maturity assessments, and chat interactions.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

import os
from typing import Optional, Dict

from fastapi import HTTPException, Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_tools.intellichek.introduction_message import chat_introduction
from ai_tools.intellichek.evaluation_glossary import get_glossary_task, transform_user_process_description
from ai_tools.intellichek.evaluate_level_of_maturity import (
    evaluate_level_of_maturity_with_chat_final,
    evaluate_level_of_maturity_with_chat,
    chat_with_maturity_intro,
    evaluate_level_of_maturity_pre
)
from ai_tools.intellichek.basis import basic_ai_chat
from langchain.chat_models import ChatOpenAI
import config
from api.models import models
from api.schemas import schemas
from database import get_db
from api.authentication.oauth import get_current_user

router = APIRouter(tags=['Process Map AI'])

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
    "/introduction",
    summary="Add string to A.I. conversation",
    description=(
        """Add String to A.I. Conversation: Initialize a chat with the AI.

        This endpoint allows the authenticated user to start a conversation with the AI. 
        The AI generates a response based on the provided input string.

        Args:
        - chat_message (ChatMessage): The input string for the AI conversation.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the AI's response.

        Raises:
        - HTTPException: If an error occurs during the process.
        """
    ),
    response_model=dict
)
def add_chat_intro(
    chat_message: ChatMessage,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        response, total_cost = chat_introduction(chat_message.human_message, model)
        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/{project_id}/transform-initial-description",
    summary="Transform User Process Description",
    description=(
        """Transform User Process Description: Modify and save the user's process description.

        This endpoint transforms the user's original process description using the provided glossary
        and saves the transformed description for the specified project.

        Args:
        - project_id (int): The ID of the project.
        - chat_language (UserChatLanguage): The language settings for the chat.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary with a success message.

        Raises:
        - HTTPException: If the project or input file is not found, or an error occurs during the transformation.
        """
    ),
    response_model=Dict[str, str]
)
def transformation_of_original_description(
    project_id: int,
    chat_language: UserChatLanguage,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        input_file_path = project.building_permit_instructions
        if not input_file_path or not os.path.isfile(input_file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Input file not found")

        with open(input_file_path, 'r') as input_file:
            file_content = input_file.read()

        glossary_path = "./ai_tools/chek_database/maturity.txt"
        if not os.path.isfile(glossary_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Glossary file not found")

        with open(glossary_path, 'r') as glossary_file:
            glossary_content = glossary_file.read()

        response, total_cost = transform_user_process_description(
            file_content,
            glossary_content,
            chat_language.language,
            model  
        )

        output_file_path = f'{os.path.dirname(input_file_path)}/transformed_user_process_description.txt'
        with open(output_file_path, 'w') as output_file:
            output_file.write(response)

        project.ai_processed_permit_process = output_file_path
        db.add(project)
        db.commit()

        chat_info = models.ChatInfo(total_cost=total_cost, user_id=current_user.id)
        db.add(chat_info)
        db.commit()

        return {"message": "Success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.post(
    "/get-task-name",
    summary="Get the Task Name",
    description=(
        """Get Task Name: Retrieve task information based on provided input.

        This endpoint processes task information based on the provided task gateway,
        language, and specific ID. The response is formulated as a list separated by a colon
        with three elements:
        - The first element indicates the status (`$FOUND$`, `$UNSURE$`, `$NOTFOUND$`).
        - The second element is a list of corresponding action names or `NONE`.
        - The third element is the AI's response, translated and rewritten in a formal, short, 
          and warm manner according to the specified language.

        Args:
        - chat_message (ChatMessage): The input task information.
        - chat_settings (UserChatSettings): The chat settings including language and diagram ID.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the task name information and diagram ID.

        Raises:
        - HTTPException: If an error occurs during the process.
        """
    ),
    response_model=dict
)
def get_task_name(
    chat_message: ChatMessage,
    chat_settings: UserChatSettings,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        response, total_cost = get_glossary_task(chat_message.human_message, chat_settings.language, model)
        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()
        return {"message": response, "diagram_id": chat_settings.diagram_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/{project_id}/maturity/alpha",
    summary="Communicate with Maturity",
    description=(
        """Evaluate Maturity: Assess the maturity of a process based on user inputs.

        This endpoint allows users to have a chat with an AI assistant that evaluates a building
        permit process based on provided inputs. The AI matches the action to a maturity level and
        provides a status along with the matched level of maturity.

        Args:
        - project_id (int): The ID of the project.
        - maturity_action (str): The user's chosen action.
        - chat_settings (UserChatSettings): The chat settings including language and diagram ID.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the evaluation response and diagram ID.

        Raises:
        - HTTPException: If the project or transformed file is not found, or an error occurs during the evaluation.
        """
    ),
    response_model=dict
)
def get_maturity_from_user_description(
    project_id: int,
    maturity_action: str,
    chat_settings: UserChatSettings,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        transformed_file_path = project.ai_processed_permit_process
        if not transformed_file_path or not os.path.isfile(transformed_file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transformed file not found")

        with open(transformed_file_path, 'r') as transformed_file:
            evaluated_description = transformed_file.read()

        response, total_cost = evaluate_level_of_maturity_pre(
            maturity_action,
            evaluated_description,
            chat_settings.language,
            model
        )

        chat_info = models.ChatInfo(total_cost=total_cost, user_id=current_user.id)
        db.add(chat_info)
        db.commit()

        return {"message": response, "diagram_id": chat_settings.diagram_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/maturity/beta",
    summary="Communicate with Maturity",
    description=(
        """Evaluate Maturity: Assess the maturity of a process based on user inputs.

        This endpoint enables users to have a chat with an AI assistant that evaluates a 
        building permit process based on provided inputs. The AI matches the action to a maturity level and 
        provides a status along with the matched level of maturity.

        Args:
        - maturity (Maturity): The user's chosen action and description.
        - chat_settings (UserChatSettings): The chat settings including language and diagram ID.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the evaluation response and diagram ID.

        Raises:
        - HTTPException: If an error occurs during the evaluation.
        """
    ),
    response_model=dict
)
def get_maturity_from_user_chat(
    maturity: Maturity,
    chat_settings: UserChatSettings,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        response, total_cost = evaluate_level_of_maturity_with_chat(maturity.action, maturity.description, chat_settings.language, model)
        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()
        return {"message": response, "diagram_id": chat_settings.diagram_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/maturity/omega",
    summary="Communicate with Maturity",
    description=(
        """Evaluate Final Maturity: Assess the final maturity of a process based on user inputs.

        This endpoint enables users to have a chat with an AI assistant that evaluates a building permit
        process based on provided inputs. The AI matches the action to a maturity level and provides a 
        status along with the matched level of maturity.

        Args:
        - maturity (Maturity): The user's chosen action and description.
        - chat_settings (UserChatSettings): The chat settings including language and diagram ID.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the evaluation response and diagram ID.

        Raises:
        - HTTPException: If an error occurs during the evaluation.
        """
    ),
    response_model=dict
)
def get_final_maturity_from_user_chat(
    maturity: Maturity,
    chat_settings: UserChatSettings,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        response, total_cost = evaluate_level_of_maturity_with_chat_final(maturity.action, maturity.description, chat_settings.language, model)
        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()
        return {"message": response, "diagram_id": chat_settings.diagram_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/maturity/introduction",
    summary="Communicate with Maturity",
    description=(
        """Maturity Introduction: Engage in a chat with the AI assistant for maturity evaluation.

        This endpoint allows users to engage in a chat with an AI assistant that evaluates a 
        building permit process according to a maturity model. Based on the user's input, the AI 
        provides a detailed response regarding the process.

        Args:
        - chat_message (ChatMessage): The input string for the AI conversation.
        - chat_settings (UserChatSettings): The chat settings including language and diagram ID.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary containing the AI's response and diagram ID.

        Raises:
        - HTTPException: If an error occurs during the process.
        """
    ),
    response_model=dict
)
def add_string_maturityq(
    chat_message: ChatMessage,
    chat_settings: UserChatSettings,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        response, total_cost = chat_with_maturity_intro(chat_message.human_message, chat_settings.language, model)
        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()
        return {"message": response, "diagram_id": chat_settings.diagram_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/basic_chat/{project_id}",
    summary="Basic Chat",
    description=(
        """Basic Chat: Perform basic chat functionality.

        This endpoint allows the authenticated user to engage in a basic chat with the AI.
        The AI generates a response based on the provided input string and user-specific settings.

        Args:
        - chat_message (ChatMessage): The input data for the chat, containing the 'value' attribute.
        - chat_settings (UserChatLanguage): User's chat language settings.
        - project_id (int): The ID of the project for which the chat is conducted.
        - db (Session): Database session dependency.
        - current_user (models.User): Authenticated user dependency.

        Returns:
        - dict: A dictionary with a message key containing the response from the basic AI chat.

        Raises:
        - HTTPException: If an unexpected error occurs during the chat process.
        """
    ),
    response_model=dict
)
def basic_chat(
    chat_message: ChatMessage,
    chat_settings: UserChatLanguage,
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        response, total_cost = basic_ai_chat(chat_message.human_message, chat_settings.language, model)
        chat_info = models.ChatInfo(total_cost=total_cost, user=current_user)
        db.add(chat_info)
        db.commit()
        return {"message": response}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
