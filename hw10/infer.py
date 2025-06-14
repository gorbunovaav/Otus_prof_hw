from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conlist
import onnxruntime as ort
import numpy as np

app = FastAPI()

# Загрузка модели
session = ort.InferenceSession("diabetes_model.onnx", providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name

class Features(BaseModel):
    data: conlist(float, min_length=4, max_length=4)

@app.post("/predict")
def predict(features: Features):
    try:
        input_data = np.array([features.data], dtype=np.float32)
        output = session.run(None, {input_name: input_data})
        prediction = int(output[0][0] > 0.5)
        return {"Предсказание": prediction, "диабет": bool(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# # Пример входных данных: [Pregnancies, Glucose, BMI, Age]
# data = np.array([[2, 140, 35.5, 32]], dtype=np.float32)


# Предсказание
# output = session.run(None, {input_name: data})
# print("Предсказание (0=нет диабета, 1=есть):", int(output[0][0] > 0.5))
