from fastapi import FastAPI
from core.config import settings
from core.models import predict  
from auth import router as jwt_auth_router


app = FastAPI()
app.include_router(predict.router, prefix=settings.api_v1_prefix)
app.include_router(jwt_auth_router)

@app.get("/")
def hello_index():
    return {"message": "Hello index!"}