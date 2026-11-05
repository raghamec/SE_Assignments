
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Calculator API",
    description="Simple Calculator using Python and FastAPI",
    version="1.0.0"
)


class Calculation(BaseModel):
    num1: float
    num2: float


@app.get("/")
def home():
    return {"message": "Welcome to Calculator API"}


@app.post("/add")
def add(data: Calculation):
    return {"operation": "addition", "result": data.num1 + data.num2}


@app.post("/subtract")
def subtract(data: Calculation):
    return {"operation": "subtraction", "result": data.num1 - data.num2}


@app.post("/multiply")
def multiply(data: Calculation):
    return {"operation": "multiplication", "result": data.num1 * data.num2}


@app.post("/divide")
def divide(data: Calculation):
    if data.num2 == 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot divide by zero"
        )

    return {"operation": "division", "result": data.num1 / data.num2}


@app.post("/square")
def square(data: Calculation):
    return {
        "operation": "square",
        "result": data.num1 ** 2
    }
