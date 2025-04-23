from fastapi import HTTPException, APIRouter
from api.schemas import schemas
from api.utils.recaptcha import verify_recaptcha

router = APIRouter(prefix='/re', tags=['Recaptcha'])

@router.post("/verify-recaptcha", response_model=schemas.ReCAPTCHAVerifyResponse)
async def verify_recaptcha_endpoint(request: schemas.ReCAPTCHAVerifyRequest):
    verification_result = await verify_recaptcha(request.token)
    if not verification_result.success:
        raise HTTPException(status_code=400, detail="Invalid reCAPTCHA token")
    return verification_result
