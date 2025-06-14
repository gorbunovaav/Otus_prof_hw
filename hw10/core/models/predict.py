from fastapi import APIRouter
from pydantic import BaseModel, conlist
import numpy as np
import onnxruntime as ort

router = APIRouter()
session = ort.InferenceSession("diabetes_model.onnx", providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name

class Features(BaseModel):
    data: conlist(float, min_length=4, max_length=4)

@router.post("/predict")
def predict(features: Features):
    input_data = np.array([features.data], dtype=np.float32)
    output = session.run(None, {input_name: input_data})
    prediction = int(output[0][0] > 0.5)
    return {"Предсказание": prediction, "диабет": bool(prediction)}