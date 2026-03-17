import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def get_settings():
    """Get authentication settings from environment"""
    return {
        "password": os.getenv("WEB_APP_PASSWORD"),
        "secret_key": os.getenv("JWT_SECRET_KEY"),
        "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
        "expire_minutes": int(os.getenv("JWT_EXPIRE_MINUTES", 1440))
    }

def verify_password(plain_password: str) -> bool:
    """Verify password against environment variable"""
    settings = get_settings()
    return plain_password == settings["password"]

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    settings = get_settings()
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=settings["expire_minutes"])
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings["secret_key"], 
        algorithm=settings["algorithm"]
    )
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token from Authorization header"""
    settings = get_settings()
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            settings["secret_key"], 
            algorithms=[settings["algorithm"]]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
