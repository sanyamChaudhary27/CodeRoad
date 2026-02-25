from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from ..config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
    
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: The plain text password to hash
    
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
    
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        logger.error(f"JWT encoding error: {e}")
        raise

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token.
    
    Args:
        token: The JWT token to verify
    
    Returns:
        Optional[Dict[str, Any]]: The decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT verification error: {e}")
        return None

def create_player_token(player_id: str, username: str, email: str) -> str:
    """
    Create an access token for a player.
    
    Args:
        player_id: The player's ID
        username: The player's username
        email: The player's email
    
    Returns:
        str: The JWT access token
    """
    data = {
        "sub": player_id,
        "username": username,
        "email": email,
        "type": "access"
    }
    
    return create_access_token(data)

def validate_player_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate a player token and return player information.
    
    Args:
        token: The JWT token
    
    Returns:
        Optional[Dict[str, Any]]: Player information if token is valid
    """
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    # Check token type
    if payload.get("type") != "access":
        logger.warning(f"Invalid token type: {payload.get('type')}")
        return None
    
    # Check if token has required fields
    required_fields = ["sub", "username", "email"]
    if not all(field in payload for field in required_fields):
        logger.warning("Token missing required fields")
        return None
    
    return {
        "id": payload["sub"],
        "username": payload["username"],
        "email": payload["email"]
    }

def create_refresh_token(player_id: str) -> str:
    """
    Create a refresh token for a player.
    
    Args:
        player_id: The player's ID
    
    Returns:
        str: The JWT refresh token
    """
    data = {
        "sub": player_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=30)  # Refresh tokens last 30 days
    }
    
    return create_access_token(data)

def validate_refresh_token(token: str) -> Optional[str]:
    """
    Validate a refresh token and return player ID.
    
    Args:
        token: The refresh token
    
    Returns:
        Optional[str]: Player ID if token is valid
    """
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    # Check token type
    if payload.get("type") != "refresh":
        return None
    
    return payload.get("sub")

def generate_api_key(player_id: str, purpose: str = "general") -> str:
    """
    Generate an API key for a player.
    
    Args:
        player_id: The player's ID
        purpose: The purpose of the API key
    
    Returns:
        str: The API key
    """
    data = {
        "sub": player_id,
        "purpose": purpose,
        "type": "api_key",
        "exp": datetime.utcnow() + timedelta(days=365)  # API keys last 1 year
    }
    
    return create_access_token(data)

def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Validate an API key.
    
    Args:
        api_key: The API key to validate
    
    Returns:
        Optional[Dict[str, Any]]: API key information if valid
    """
    payload = verify_token(api_key)
    
    if payload is None:
        return None
    
    # Check token type
    if payload.get("type") != "api_key":
        return None
    
    return {
        "player_id": payload.get("sub"),
        "purpose": payload.get("purpose")
    }

# Password strength validation
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: The password to validate
    
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be at most 128 characters long"
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"



# FastAPI dependency for JWT authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_player(credentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to validate JWT token and return current player.

    Args:
        credentials: HTTP Bearer token from request

    Returns:
        Dict[str, Any]: Player information (id, username, email)

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    player_info = validate_player_token(token)

    if player_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return player_info
