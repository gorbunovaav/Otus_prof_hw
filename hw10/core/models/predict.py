from fastapi import APIRouter, Depends
from pydantic import BaseModel, conlist
from users.schemas import UserSchema
import numpy as np
import onnxruntime as ort
from auth.jwt_auth import get_current_active_auth_user  

router = APIRouter(prefix="/api",tags=["Predict"])
session = ort.InferenceSession("diabetes_model.onnx", providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name

class Features(BaseModel):
    data: conlist(float, min_length=4, max_length=4)

@router.post("/predict")
def predict(
    features: Features,
    user: UserSchema = Depends(get_current_active_auth_user), 
):
    input_data = np.array([features.data], dtype=np.float32)
    output = session.run(None, {input_name: input_data})
    prediction = int(output[0][0] > 0.5)
    return {
        "username": user.username,
        "Предсказание": prediction,
        "диабет": bool(prediction)
    }