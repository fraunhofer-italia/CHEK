from itsdangerous import URLSafeTimedSerializer
import config
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM

def generate_reset_token(email: str, expires_sec: int = 3600) -> str:
    """
    Generate a time-limited token for password reset.

    Args:
        email (str): The email for which the reset is being requested.
        expires_sec (int): Expiration time in seconds (default: 3600 sec = 1 hour).
    
    Returns:
        str: The generated token.
    """
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email, salt='password-reset-salt')

def verify_reset_token(token: str, expiration: int = 3600) -> str:
    """
    Verify the password reset token.

    Args:
        token (str): The reset token to verify.
        expiration (int): Time limit for the token in seconds (default: 1 hour).
    
    Returns:
        str: The email address if the token is valid, otherwise None.
    """
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create a JWT access token with expiration.

    Args:
        data (dict): The data to encode in the token (usually user data).
        expires_delta (timedelta): The expiration duration for the token.
    
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_confirmation_token(email: str) -> str:
    """
    Generate a confirmation token for email verification.

    Args:
        email (str): The email to generate a confirmation token for.
    
    Returns:
        str: The generated JWT token for email confirmation, valid for 24 hours.
    """
    expires = timedelta(hours=24)
    return create_access_token(
        data={"sub": email},
        expires_delta=expires
    )

def verify_confirmation_token(token: str) -> str:
    """
    Verify the email confirmation token.

    Args:
        token (str): The token to verify.
    
    Returns:
        str: The email address if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None
