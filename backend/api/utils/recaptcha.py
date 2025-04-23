import httpx
import logging
from config import RECAPTCHA_SECRET_KEY
from api.schemas import schemas

logging.basicConfig(level=logging.INFO)

async def verify_recaptcha(token: str) -> schemas.ReCAPTCHAVerifyResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={"secret": RECAPTCHA_SECRET_KEY, "response": token},
            )
            response.raise_for_status()
            response_data = response.json()
            logging.info(f"reCAPTCHA verification response: {response_data}")
            return schemas.ReCAPTCHAVerifyResponse(**response_data)
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {e.response.status_code} {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail="Error verifying reCAPTCHA")
    except httpx.RequestError as e:
        logging.error(f"An error occurred while requesting reCAPTCHA verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Error verifying reCAPTCHA")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error verifying reCAPTCHA")