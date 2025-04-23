"""
Benchmark and Roadmap AI Module

This module contains FastAPI routes and models for evaluating maturity model technology 
and managing roadmaps using AI. It includes endpoints for evaluating benchmarks, fetching 
roadmaps, and handling user-specific settings for AI conversations.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""
from typing import Optional

from fastapi import HTTPException, Depends, APIRouter, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from ai_tools.intellichek.roadmap import get_roadmap_from_ai
from langchain.chat_models import ChatOpenAI
import config
import json
import os
from api.models import models
from api.schemas import schemas
from database import get_db
from api.authentication.oauth import get_current_user, get_current_user_role

router = APIRouter(tags=['Benchmark and Roadmap AI'])

openai_api_key = config.OPENAI_API_KEY 

if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables.")

model = ChatOpenAI(temperature=float(config.TEMPERATURE), model=config.GPT_MODEL)

class ChatMessage(BaseModel):
    """Model representing the input string for A.I. conversation."""
    human_message: str

class UserChatLanguage(BaseModel):
    """Model representing user-specific settings for A.I. conversation."""
    language: Optional[str] = "English"


directory_path = './ai_tools/chek_database'
file_name = 'benchmark.json'

file_path = os.path.join(directory_path, file_name)

@router.post(
    "/evaluate_benchmark_chek", 
    summary="Evaluate Benchmark Check",
    description=(
    """
    Adds string maturity based on AI evaluation for a specific project.

    Parameters:
    - chat_message: ChatMessage - Input message for AI conversation.
    - chat_settings: UserChatSettings - User-specific settings for the AI conversation.
    - project_id: int - ID of the project to fetch the last BPMN data for.
    - current_user: models.User - Current authenticated user.
    - current_user_role: str - Role of the current authenticated user.
    - db: Session - Database session dependency.

    Returns:
    - dict: Dictionary containing the message and response data.
    """
    ),
    response_model=dict
)
async def evaluate_chek_benchmark(
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN data for."),
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
        else:
            owner_user_id = current_user.id

        entries = []
        
        categories = [models.MaturityModelOrganisation, 
                      models.MaturityModelTechnology,
                      models.MaturityModelInformation, 
                      models.MaturityModelProcess]

        for category in categories:
            category_entries = db.query(category).filter(
                category.user_id == owner_user_id,
                category.project_id == project_id
            ).all()

            for entry in category_entries:
                entries.append({
                    "label": entry.label,
                    "level": entry.level
                })
                
        if not entries:
            raise HTTPException(status_code=404, detail="No maturity entries found for the project.")

        # Load the JSON data from the file
        
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        new_entries = []

        for db_entry in entries:
            json_entry = next((item for item in json_data["Key Maturity Areas"] if item["kma"] == db_entry["label"]), None)
            if json_entry:
                level_difference = json_entry["check level"] - db_entry["level"]
                if level_difference < 0:
                    level_difference = 0

                dependencies = json_entry.get("dependencies", [])
                actions = json_entry.get("actions", [])
                chek_tools = json_entry.get("check tools", [])

                # Ensure dependencies, actions, and chek_tools are lists
                if isinstance(dependencies, str):
                    dependencies = [dependencies]
                if isinstance(actions, str):
                    actions = [actions]
                if isinstance(chek_tools, str):
                    chek_tools = [chek_tools]

                # Convert "No previous action needed" to empty list
                if "No previous action needed" in dependencies:
                    dependencies = []

                new_entries.append({
                    "kma": json_entry["kma"],
                    "level_difference": level_difference,
                    "dependencies": dependencies,
                    "actions": actions,
                    "chek_tools": chek_tools
                })
                
        db.query(models.BenchmarkModel).filter(
                    models.BenchmarkModel.project_id == project_id
                ).delete()

        # Insert new entries into the new database table
        model_instances = [
            models.BenchmarkModel(
                kma=data["kma"],
                level_difference=data["level_difference"],
                dependencies=data["dependencies"],
                actions=data["actions"],
                chek_tools=data["chek_tools"],
                user_id=current_user.id,
                project_id=project_id
            )
            for data in new_entries
        ]

        for instance in model_instances:
            db.add(instance)

        db.commit()

        return {"message": "The operation was completed successfully."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get(
    "/get_benchmark_chek", 
    summary="Get Benchmark Check",
    description="Retrieves the benchmark check data for a specific project.",
    response_model=List[schemas.BenchmarkModel]
)
async def get_benchmark_chek(
    project_id: int = Query(..., description="ID of the project to fetch the benchmark check data for."),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
                
        if current_user_role != "admin" and project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to access this project.")

        benchmark_data = db.query(models.BenchmarkModel).filter(
           models.BenchmarkModel.project_id == project_id
        ).all()

        if not benchmark_data:
            raise HTTPException(status_code=404, detail="No benchmark check data found for the project.")

        return benchmark_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.post(
    "/evaluate_benchmark_chek_roadmap", 
    summary="Evaluate Roadmap",
    description=(
    """
    Adds string maturity based on AI evaluation for a specific project.

    Parameters:
    - chat_message: ChatMessage - Input message for AI conversation.
    - chat_settings: UserChatSettings - User-specific settings for the AI conversation.
    - project_id: int - ID of the project to fetch the last BPMN data for.
    - current_user: models.User - Current authenticated user.
    - current_user_role: str - Role of the current authenticated user.
    - db: Session - Database session dependency.

    Returns:
    - dict: Dictionary containing the message and response data.
    """
    ),
    response_model=dict
)
async def evaluate_chek_benchmark(
    chat_settings: UserChatLanguage, 
    project_id: int = Query(..., description="ID of the project to fetch the last BPMN data for."),
    current_user: models.User = Depends(get_current_user),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
                
    
        entries = db.query(models.BenchmarkModel).filter(
            models.BenchmarkModel.project_id == project_id
        ).all()
        
        if not entries:
            raise HTTPException(status_code=404, detail="No benchmark entries found for the project.")

        formatted_entries = "\n".join([
            f"KMA: {entry.kma}\n"
            f"Level Difference: {entry.level_difference}\n"
            f"Dependencies: {', '.join(entry.dependencies)}\n"
            f"Actions: {', '.join(entry.actions)}\n"
            f"Chek Tools: {', '.join(entry.chek_tools)}\n"
            for entry in entries
        ])
        
        
        response, total_cost = await get_roadmap_from_ai(formatted_entries, chat_settings.language, model)

        db.query(models.Roadmap).filter(
            models.Roadmap.user_id == current_user.id,
            models.Roadmap.project_id == project_id
        ).delete()

        response_data = []
        
        for chat_message in response:
            try:
                kma_name = chat_message.get("kma")
                start_date = chat_message.get("start_date")
                end_date = chat_message.get("end_date")
                dependencies = chat_message.get("dependencies", [])
                actions = chat_message.get("actions", [])
                chek_tools = chat_message.get("chek_tools", [])
                
                response_data.append({
                    "kma": kma_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "dependencies": dependencies,
                    "actions": actions,
                    "chek_tools": chek_tools
                })
            except KeyError as e:
                raise HTTPException(status_code=500, detail=f"Missing key in AI response: {str(e)}")
            
        model_instances = [
            models.Roadmap(
                kma=data["kma"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                dependencies=data["dependencies"],
                actions=data["actions"],
                chek_tools=data["chek_tools"],
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

        return {"message": "The operation was completed successfully."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get(
    "/{project_id}/get-roadmap", 
    summary="Get Roadmaps",
    description= """
    Retrieves all roadmaps for a specific project ID.

    Parameters:
    - project_id: int - ID of the project to fetch the roadmaps for.
    - current_user: models.User - Current authenticated user.
    - current_user_role: str - Role of the current authenticated user.
    - db: Session - Database session dependency.

    Returns:
    - List[schemas.Roadmap]: List of roadmaps for the specified project.
    """,
    response_model=List[schemas.Roadmap]
)
def get_roadmaps(
    project_id: int, 
    current_user: models.User = Depends(get_current_user), 
    current_user_role: str = Depends(get_current_user_role), 
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user_role == "admin":
        roadmaps = db.query(models.Roadmap).filter(models.Roadmap.project_id == project_id).all()
    else:
        roadmaps = db.query(models.Roadmap).filter(models.Roadmap.project_id == project_id, models.Roadmap.user_id == current_user.id).all()

    if not roadmaps:
        raise HTTPException(status_code=404, detail="No roadmaps found for this project")

    return roadmaps
