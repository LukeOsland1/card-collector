"""Authentication and authorization for web API."""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from db.database import get_db_session, UserCRUD, GuildConfigCRUD
from bot.permissions import get_user_permission_level, PermissionLevel

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Discord OAuth Configuration
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8080/auth/callback")

# Discord API URLs
DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_OAUTH_URL = f"{DISCORD_API_BASE}/oauth2/token"
DISCORD_USER_URL = f"{DISCORD_API_BASE}/users/@me"
DISCORD_GUILDS_URL = f"{DISCORD_API_BASE}/users/@me/guilds"

security = HTTPBearer(auto_error=False)


class AuthenticationError(HTTPException):
    """Custom authentication error."""
    
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionError(HTTPException):
    """Custom permission error."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, any]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise AuthenticationError("Invalid token")


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db = Depends(get_db_session),
) -> dict:
    """Get current authenticated user."""
    if not credentials:
        raise AuthenticationError()
    
    payload = verify_token(credentials.credentials)
    discord_id = payload.get("discord_id")
    
    if not discord_id:
        raise AuthenticationError("Invalid token payload")
    
    # Get user from database
    user = await UserCRUD.get_by_discord_id(db, int(discord_id))
    if not user:
        raise AuthenticationError("User not found")
    
    # Update last activity
    await UserCRUD.update_last_activity(db, int(discord_id))
    
    # Get user permissions for current guild if available
    guild_id = request.headers.get("X-Guild-ID")
    permission_level = PermissionLevel.USER
    
    if guild_id:
        try:
            # Create a mock interaction for permission checking
            class MockInteraction:
                def __init__(self, user_id, guild_id):
                    self.user = MockUser(user_id)
                    self.guild_id = int(guild_id)
                    self.guild = MockGuild(int(guild_id))
            
            class MockUser:
                def __init__(self, user_id):
                    self.id = int(user_id)
            
            class MockGuild:
                def __init__(self, guild_id):
                    self.id = guild_id
                    self.owner_id = None  # Would need to fetch from Discord API
            
            mock_interaction = MockInteraction(discord_id, guild_id)
            permission_level = await get_user_permission_level(mock_interaction, db, int(discord_id))
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
    
    return {
        "discord_id": int(discord_id),
        "username": payload.get("username", "Unknown"),
        "is_moderator": permission_level >= PermissionLevel.MODERATOR,
        "is_admin": permission_level >= PermissionLevel.ADMIN,
        "is_owner": permission_level >= PermissionLevel.OWNER,
        "permission_level": permission_level,
        "guild_id": guild_id,
    }


def require_permissions(
    moderator: bool = False,
    admin: bool = False,
    owner: bool = False,
):
    """Dependency factory for permission requirements."""
    
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        if owner and not current_user.get("is_owner", False):
            raise PermissionError("Owner permissions required")
        elif admin and not current_user.get("is_admin", False):
            raise PermissionError("Administrator permissions required")
        elif moderator and not current_user.get("is_moderator", False):
            raise PermissionError("Moderator permissions required")
        
        return current_user
    
    return permission_checker


async def exchange_discord_code(code: str) -> dict:
    """Exchange Discord OAuth code for access token."""
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(DISCORD_OAUTH_URL, data=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Discord OAuth error: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange Discord code"
            )
        
        return response.json()


async def get_discord_user(access_token: str) -> dict:
    """Get Discord user information using access token."""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(DISCORD_USER_URL, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Discord API error: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get Discord user info"
            )
        
        return response.json()


async def get_discord_guilds(access_token: str) -> list:
    """Get Discord guilds for user using access token."""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(DISCORD_GUILDS_URL, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Discord guilds API error: {response.text}")
            return []
        
        return response.json()


async def login_with_discord(code: str, db) -> dict:
    """Complete Discord OAuth login flow."""
    # Exchange code for access token
    token_response = await exchange_discord_code(code)
    access_token = token_response["access_token"]
    
    # Get user information
    user_info = await get_discord_user(access_token)
    discord_id = int(user_info["id"])
    username = f"{user_info['username']}#{user_info['discriminator']}"
    
    # Get or create user in database
    user = await UserCRUD.get_or_create(db, discord_id)
    
    # Create JWT token
    token_data = {
        "discord_id": discord_id,
        "username": username,
    }
    
    jwt_token = create_access_token(token_data)
    
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "discord_id": discord_id,
            "username": username,
            "avatar": user_info.get("avatar"),
            "global_name": user_info.get("global_name"),
        }
    }


def get_discord_oauth_url(state: Optional[str] = None) -> str:
    """Generate Discord OAuth authorization URL."""
    base_url = "https://discord.com/api/oauth2/authorize"
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds",
    }
    
    if state:
        params["state"] = state
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"


async def refresh_user_permissions(
    user_id: int,
    guild_id: int,
    db
) -> dict:
    """Refresh and cache user permissions for a guild."""
    try:
        # This would ideally fetch fresh data from Discord API
        # For now, we'll just recalculate based on database config
        
        class MockInteraction:
            def __init__(self, user_id, guild_id):
                self.user = MockUser(user_id)
                self.guild_id = guild_id
                self.guild = MockGuild(guild_id)
        
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
        
        class MockGuild:
            def __init__(self, guild_id):
                self.id = guild_id
                self.owner_id = None
        
        mock_interaction = MockInteraction(user_id, guild_id)
        permission_level = await get_user_permission_level(mock_interaction, db, user_id)
        
        return {
            "user_id": user_id,
            "guild_id": guild_id,
            "permission_level": permission_level,
            "is_moderator": permission_level >= PermissionLevel.MODERATOR,
            "is_admin": permission_level >= PermissionLevel.ADMIN,
            "is_owner": permission_level >= PermissionLevel.OWNER,
            "updated_at": datetime.utcnow(),
        }
        
    except Exception as e:
        logger.error(f"Error refreshing user permissions: {e}")
        return {
            "user_id": user_id,
            "guild_id": guild_id,
            "permission_level": PermissionLevel.USER,
            "is_moderator": False,
            "is_admin": False,
            "is_owner": False,
            "error": str(e),
        }


class OptionalAuth:
    """Optional authentication dependency."""
    
    async def __call__(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db = Depends(get_db_session),
    ) -> Optional[dict]:
        """Get current user if authenticated, otherwise return None."""
        if not credentials:
            return None
        
        try:
            return await get_current_user(request, credentials, db)
        except HTTPException:
            return None


optional_auth = OptionalAuth()


async def validate_api_key(api_key: str, db) -> Optional[dict]:
    """Validate API key for external integrations."""
    # This would validate API keys stored in database
    # For now, just check against environment variable
    valid_api_key = os.getenv("API_KEY")
    
    if not valid_api_key or api_key != valid_api_key:
        return None
    
    return {
        "type": "api_key",
        "is_moderator": True,
        "is_admin": True,
        "is_owner": False,
    }


async def get_current_user_or_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db = Depends(get_db_session),
) -> dict:
    """Get current user via JWT token or API key."""
    if not credentials:
        raise AuthenticationError()
    
    token = credentials.credentials
    
    # Try JWT token first
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException:
        pass
    
    # Try API key
    api_user = await validate_api_key(token, db)
    if api_user:
        return api_user
    
    raise AuthenticationError("Invalid token or API key")