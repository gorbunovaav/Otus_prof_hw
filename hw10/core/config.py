from pydantic import BaseModel, conlist
from pydantic_settings import BaseSettings
from pathlib import Path


class AuthJWT(BaseModel):
    private_key_path: Path = Path("certs/jwt-private.pem")
    public_key_path: Path = Path("certs/jwt-public.pem")
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()