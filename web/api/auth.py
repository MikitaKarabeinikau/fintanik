from fastapi import APIRouter, HTTPException, Depends
from web.schemas.auth import LoginRequest, TokenResponse
from web.utils.auth import verify_password, create_access_token, verify_token

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Login endpoint - verify password and return JWT token
    """
    if not verify_password(request.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": "user", "authenticated": True}
    )
    
    return TokenResponse(access_token=access_token)

@router.get("/verify")
def verify_auth(payload: dict = Depends(verify_token)):
    """
    Verify token endpoint - check if token is valid
    """
    return {
        "status": "authenticated",
        "user": payload.get("sub"),
        "expires": payload.get("exp")
    }
