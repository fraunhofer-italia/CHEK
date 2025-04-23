# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, TIMESTAMP, Boolean, text, ARRAY
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    municipality = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    language = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    email  = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)

    role = Column(String, default="user", nullable=True)
    email_active = Column(Boolean, default=False)
    published = Column(Boolean, server_default='TRUE')
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    roadmaps = relationship("Roadmap", back_populates="user")
    projects = relationship("Project", back_populates="user")
    chat_info = relationship("ChatInfo", back_populates="user")
    bpmn_extraction = relationship("BPMNExtraction", back_populates="user")
    
    maturity_model_technology = relationship("MaturityModelTechnology", back_populates="user")  
    maturity_model_organisation = relationship("MaturityModelOrganisation", back_populates="user") 
    maturity_model_information = relationship("MaturityModelInformation", back_populates="user") 
    maturity_model_process = relationship("MaturityModelProcess", back_populates="user") 
    report_as_is = relationship("ReportAsIs", back_populates="user") 
    report_maturity = relationship("ReportMaturity", back_populates='user') 
    report_roadmap = relationship("ReportRoadmap", back_populates='user') 
    benchmark_model = relationship("BenchmarkModel", back_populates="user")
    questionnaire_entries = relationship("QuestionnaireEntry", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    building_permit_instructions = Column(String)
    ai_processed_permit_process = Column(String)
    maturity_assessment = Column(Boolean, default=False)
    questionnair_submitted = Column(Boolean, default=False)
    roadmap_created = Column(Boolean, default=False)
    report_created = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    bpmn_data = relationship("BPMNData", back_populates="project")
    bpmn_extraction = relationship("BPMNExtraction", back_populates="project")
    maturity_model_organisation = relationship("MaturityModelOrganisation", back_populates="project") 
    maturity_model_information = relationship("MaturityModelInformation", back_populates="project") 
    maturity_model_process = relationship("MaturityModelProcess", back_populates="project") 
    maturity_model_technology = relationship("MaturityModelTechnology", back_populates="project")  
    roadmaps = relationship("Roadmap", back_populates="project")
    report_as_is = relationship("ReportAsIs", back_populates="project") 
    report_maturity = relationship("ReportMaturity", back_populates='project') 
    report_roadmap = relationship("ReportRoadmap", back_populates='project') 
    benchmark_model = relationship("BenchmarkModel", back_populates="project")
    questionnaire_entries = relationship("QuestionnaireEntry", back_populates="project")

class BPMNData(Base):
    __tablename__ = "bpmn_data"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    project_id = Column(Integer, ForeignKey('projects.id'))  
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    project = relationship("Project", back_populates="bpmn_data")

class ChatInfo(Base):
    __tablename__ = "chat_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_cost = Column(Float)
    user = relationship("User", back_populates="chat_info")

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    jti = Column(String, primary_key=True)

class BPMNTemplate(Base):
    __tablename__ = "bpm_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

class BPMNExtraction(Base):
    __tablename__ = "bpm_extraction"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    project_id = Column(Integer, ForeignKey('projects.id')) 
    user_id = Column(Integer, ForeignKey('users.id')) 
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    project = relationship("Project", back_populates="bpmn_extraction")
    user = relationship("User", back_populates="bpmn_extraction")

class MaturityModelTechnology(Base):
    __tablename__ = 'maturity_model_technology'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    justification = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 

    user = relationship("User", back_populates="maturity_model_technology")  
    project = relationship("Project", back_populates="maturity_model_technology")  

class MaturityModelProcess(Base):
    __tablename__ = 'maturity_model_process'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    justification = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 

    user = relationship("User", back_populates="maturity_model_process")  
    project = relationship("Project", back_populates="maturity_model_process") 

class MaturityModelInformation(Base):
    __tablename__ = 'maturity_model_information'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    justification = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 

    user = relationship("User", back_populates="maturity_model_information")  
    project = relationship("Project", back_populates="maturity_model_information") 

class MaturityModelOrganisation(Base):
    __tablename__ = 'maturity_model_organisation'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    justification = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 

    user = relationship("User", back_populates='maturity_model_organisation')  
    project = relationship("Project", back_populates='maturity_model_organisation') 

class ReportAsIs(Base):
    __tablename__ = 'report_as_is'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 

    user = relationship("User", back_populates='report_as_is')  
    project = relationship("Project", back_populates='report_as_is') 
    
class ReportRoadmap(Base):
    __tablename__ = 'report_roadmap'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 

    user = relationship("User", back_populates='report_roadmap')  
    project = relationship("Project", back_populates='report_roadmap') 
    
class ReportMaturity(Base):
    __tablename__ = 'report_maturity'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 

    user = relationship("User", back_populates='report_maturity')  
    project = relationship("Project", back_populates='report_maturity') 

class QuestionnaireEntry(Base):
    __tablename__ = "questionnaire_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String, nullable=False)
    maturity_category = Column(String, nullable=False)
    question_number = Column(Integer, nullable=False)
    answer_number = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user = relationship("User", back_populates="questionnaire_entries")
    project = relationship("Project", back_populates="questionnaire_entries")

class Roadmap(Base):
    __tablename__ = 'roadmaps'
    id = Column(Integer, primary_key=True, index=True)
    kma = Column(String, index=True)
    start_date = Column(String, index=True)
    end_date = Column(String, index=True)
    dependencies = Column(ARRAY(String))
    actions = Column(ARRAY(String))
    chek_tools = Column(ARRAY(String))
    
    user_id = Column(Integer, ForeignKey('users.id')) 
    project_id = Column(Integer, ForeignKey('projects.id')) 
    
    user = relationship("User", back_populates='roadmaps')  
    project = relationship("Project", back_populates='roadmaps')

class BenchmarkModel(Base):
    __tablename__ = 'benchmark_model'

    id = Column(Integer, primary_key=True, index=True)
    kma = Column(String, index=True)
    level_difference = Column(Integer)
    dependencies = Column(ARRAY(String))
    actions = Column(ARRAY(String))
    chek_tools = Column(ARRAY(String))

    user_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))

    user = relationship("User", back_populates="benchmark_model")
    project = relationship("Project", back_populates="benchmark_model")