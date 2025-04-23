from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import config
from api.schemas import schemas
import uuid
from database import get_db

from api.models import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/login')

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(config.ACCESS_TOKEN_EXPIRE_MINUTES)

from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm

class OAuth2PasswordRequestFormReCaptcha(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
        client_id: str = Form(None),
        client_secret: str = Form(None),
        recaptcha_token: str = Form(...)
    ):
        super().__init__(username=username, password=password, scope=scope, client_id=client_id, client_secret=client_secret)
        self.recaptcha_token = recaptcha_token

def create_access_token(data: dict):
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt


def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        jti = payload.get("jti")

        if jti and db.query(models.TokenBlacklist).filter_by(jti=jti).first():
            raise credentials_exception

        id: str = str(payload.get("user_id"))  # Convert to string
        if id is None:
            raise credentials_exception

        token_data = schemas.DataToken(id=id)
    except JWTError as e:
        print(e)
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not Validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_token_access(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user

def get_current_user_role(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_token_access(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token_data.id).first()

    if user is None:
        raise credentials_exception

    return user.role

def check_admin_role(current_user_role: str = Depends(get_current_user_role)):
    if current_user_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have admin role")


