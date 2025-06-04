from fastapi import Header, HTTPException, status
from typing import Optional

API_KEY = "1234567890"

def verify_api_key(Authorization: Optional[str] = Header(None)):
    if Authorization is None or Authorization != f"Bearer {API_KEY}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return Authorization
