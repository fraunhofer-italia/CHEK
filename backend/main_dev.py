"""
Main Application Module.

This module initializes and configures the FastAPI application, including middleware, database connections,
and API routers. It sets up the main entry point for the CHEK Backend API.

Author: Elias Niederwieser (Fraunhofer Italia)
Date: 2024
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from api.routers.limiter import limiter
from slowapi.errors import RateLimitExceeded
from database import engine
import config as config 

from api.routers import (
    prices, questionaire, process_map, 
    users, authentification, projects,
    user_info, bpmn, maturity_models, 
    report, extraction_evaluation, 
    recaptcha, roadmap, email
)
from api.models import models
import logging

models.Base.metadata.create_all(bind=engine)

app = FastAPI(**config.FASTAPI_CONFIG)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded, 
    _rate_limit_exceeded_handler
    )

logging.basicConfig(level=logging.INFO)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)

app.include_router(authentification.router, prefix="/api/v1")
app.include_router(email.router, prefix="/api/v1")
app.include_router(recaptcha.router, prefix="/api/v1")
app.include_router(user_info.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(projects.router, prefix="/api/v1/projects")
app.include_router(bpmn.router, prefix="/api/v1/bpmn")
app.include_router(process_map.router, prefix="/api/v1/intellichek")
app.include_router(extraction_evaluation.router, prefix="/api/v1/intellichek")
app.include_router(questionaire.router, prefix="/api/v1/questionaire")
app.include_router(maturity_models.router, prefix="/api/v1")
app.include_router(roadmap.router, prefix="/api/v1/roadmap")
app.include_router(report.router, prefix="/api/v1/reports")
app.include_router(prices.router, prefix="/api/v1")
