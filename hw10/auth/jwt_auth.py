from users.schemas import UserSchema
from typing import Optional, List
from auth import utils as auth_utils
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)

# http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/jwt/login/")

class TokenInfo(BaseModel):
    access_token: str
    token_type: str

class UserSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    active: bool = True
    roles: List[str] = []

router = APIRouter(prefix="/jwt", tags=["JWT"])


john = UserSchema(
    username="john",
    password=auth_utils.hash_password("qwerty"),
    email="john@google.com",
    roles=["admin"],
)

sam = UserSchema(
    username="sam",
    password=auth_utils.hash_password("secret"),
    roles=["user"],
)

users_db: dict[str, UserSchema] = {
    john.username: john,
    sam.username: sam,
}


def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
    if not (user := users_db.get(username)):
        raise unauthed_exc

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.password
    ):
        raise unauthed_exc
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive"
        )
    return user

#данные из тела токена
def get_current_token_payload(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
    token: str = Depends(oauth2_scheme)
) -> UserSchema:
    # token = credentials.credentials
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}"
        )
    return payload


def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload)
) -> UserSchema:
    username: str | None = payload.get("sub")
    if user := users_db.get(username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token not found (token invalid, user not found)"
    )
    

def get_current_active_auth_user(
    user: UserSchema = Depends(get_current_auth_user),
    payload: dict = Depends(get_current_token_payload),
    ):
    if user.active:
        return user
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive"
        )

def require_roles(*allowed_roles: str):
    def _role_checker(
        user: UserSchema = Depends(get_current_active_auth_user),
        payload: dict = Depends(get_current_token_payload),
    ):
        user_roles = payload.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: required roles {allowed_roles}",
            )
        return user
    return _role_checker

@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserSchema = Depends(validate_auth_user),
):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        "roles": user.roles,

        # "logged_in_at"
    }
    access_token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=access_token,
        token_type="Bearer",
    )


@router.get("/users/me")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_active_auth_user)
    ):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
    }
    
@router.get("/admin-only")
def admin_only_action(user: UserSchema = Depends(require_roles("admin"))):
    return {"message": f"Welcome admin {user.username}!"}

@router.get("/dashboard")
def user_dashboard(user: UserSchema = Depends(require_roles("user", "admin"))):
    return {"message": f"Hello {user.username}, welcome to dashboard!"}
