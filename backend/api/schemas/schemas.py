# schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectBase(BaseModel):
    name: Optional[str]
    building_permit_instructions: Optional[str] = None
    ai_processed_permit_process: Optional[str] = None
    questionnair_submitted: Optional[bool] = False
    maturity_assessment: Optional[bool] = False
    roadmap_created: Optional[bool] = False
    report_created: Optional[bool] = False

class ProjectCreate(ProjectBase):
    pass 

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    building_permit_instructions: Optional[str] = None
    ai_processed_permit_process: Optional[str] = None
    questionnair_submitted: Optional[bool] = None
    maturity_assessment: Optional[bool] = None
    roadmap_created: Optional[bool] = None
    report_created: Optional[bool] = None
    
class Project(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_orm = True
        
class CreateUser(BaseModel):
    first_name : str
    last_name : str
    municipality : str
    city : str
    country : str
    language : str
    zip_code : str
    email  : str
    password : str
    recaptcha_token: Optional[str] = None
    role: Optional[str] = "user"
    
class UpdateUser(BaseModel):
    first_name : str
    last_name : str
    municipality : str
    city : str
    country : str
    language : str
    zip_code : str
    email  : str    

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DataToken(BaseModel):
    id:Optional[str] = None
    

class UserOutput(BaseModel):
    first_name : str
    last_name : str
    municipality : str
    city : str
    country : str
    language : str
    zip_code : str
    email  : str
    role : str
    id: int
    email_active: Optional[bool] = False
    created_at: datetime
    class Config:
        from_orm = True


class ChatInfoSchema(BaseModel):
    total_cost: float

class BPMNDataSchema(BaseModel):
    bpmnData: str
    created_at: datetime

class BPMNTemplateSchema(BaseModel):
    title : str
    content : str
    created_at : datetime
 
class BPMNExtractionSchema(BaseModel):
    content : str
    project_id: int
    created_at : datetime

class MaturityModelTechnologySchema(BaseModel):
    content : str
    project_id: int
    created_at : datetime

class MaturityModelInformationSchema(BaseModel):
    content : str
    project_id: int
    created_at : datetime

class MaturityModelOrganisationSchema(BaseModel):
    content : str
    project_id: int
    created_at : datetime

class MaturityModelProcessSchema(BaseModel):
    content : str
    project_id: int
    created_at : datetime

class ReportAsIsCreate(BaseModel):
    content: str
    user_id: int
    project_id: int
    
class ReportMaturity(BaseModel):
    content: str
    user_id: int
    project_id: int
 
class ReportRoadmap(BaseModel):
    content: str
    user_id: int
    project_id: int
     
class QuestionnaireEntryBase(BaseModel):
    category: str
    maturity_category: str
    question_number: int
    answer_number: int

class QuestionnaireEntryCreate(QuestionnaireEntryBase):
    pass

class QuestionnaireEntry(QuestionnaireEntryBase):
    id: int
    description: str
    user_id: int

    class Config:
        from_orm: True

class BulkQuestionnaireEntryCreate(BaseModel):
    entries: List[QuestionnaireEntryCreate]
    
class ReCAPTCHAVerifyRequest(BaseModel):
    token: str

class ReCAPTCHAVerifyResponse(BaseModel):
    success: bool
    challenge_ts: str = None
    hostname: str = None
    score: float = None
    action: str = None
    error_codes: list = None

class MaturityModelEntry(BaseModel):
    label: str
    level: int
    justification: Optional[str] = None

class RoadmapBase(BaseModel):
    kma: str
    start_date: str
    end_date: str
    dependencies: List[str]
    actions: List[str]
    chek_tools: List[str]

class RoadmapCreate(RoadmapBase):
    pass

class Roadmap(RoadmapBase):
    id: int

    class Config:
        orm_mode = True

class BenchmarkModelBase(BaseModel):
    kma: str
    level_difference: int
    dependencies: List[str]
    actions: List[str]
    chek_tools: List[str]

class BenchmarkModelCreate(BenchmarkModelBase):
    pass

class BenchmarkModel(BenchmarkModelBase):
    id: int

    class Config:
        orm_mode = True
