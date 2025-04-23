from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models import models
from database import get_db
from api.utils.email_utils import send_email
from api.utils import token_utils as token_utils
from api.utils.utils import hash_pass
from fastapi.templating import Jinja2Templates
from api.utils.token_utils import verify_confirmation_token
from pathlib import Path

router = APIRouter(tags=['Email Service'])

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_dir)

@router.post("/password-reset-request")
def password_reset_request(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    name = user.first_name + ' ' + user.last_name
    token = token_utils.generate_reset_token(user.email)
    reset_url = f"http://your-frontend-url/reset-password?token={token}" #Julius

    html_content = templates.get_template("password_reset_email.html").render(
        name=name, reset_url=reset_url
    )

    send_email(
        to_email=user.email,
        subject="CHEK Password Reset Request",
        text=f"Click the following link to reset your password: {reset_url}",
        html=html_content
    )

    return {"message": "Password reset email sent."}


@router.post("/password-reset")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = token_utils.verify_reset_token(token)

    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.password = hash_pass(new_password)
    db.commit()

    return {"message": "Password reset successful."}


@router.get("/confirm-email", summary="Confirm User Email")
def confirm_email(token: str, db: Session = Depends(get_db)):
    email = verify_confirmation_token(token)
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.email_active:
        return {"message": "Email already confirmed."}

    user.email_active = True
    db.commit()

    return {"message": "Email confirmed successfully."}
