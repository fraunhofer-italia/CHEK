import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")  
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0")) 

# PostgreSQL Configuration
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "fraunhoferlab")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", ""))
RECAPTCHA_SECRET_KEY= os.getenv("RECAPTCHA_SECRET_KEY", "6LdFeQ0qAAAAACwh51m8XGLl1z-uLPxb_AEYBIS_")

# FAST API SWAGGER
FASTAPI_CONFIG = {
    "title": "CHEK MAIN BACKEND",
    "description": "API Description for CHEK Main Backend",
    "summary":"Main Backend for the CHEK VA WebUI Tool",
    "version": "0.0.0",
    "terms_of_service":"http://example.com/terms/",
    "contact": {
        "name": "Fraunhofer ITALIA (Elias Niederwieser) for API Support",
        "url":"https://fraunhofer.it",
        "email": "elias.niederwieser@fraunhofer.it",
    },
    "swagger_ui_parameters": {"syntaxHighlight.theme": "obsidian"},
}
