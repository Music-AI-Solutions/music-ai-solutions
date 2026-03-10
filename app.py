# FastAPI main application
from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def read_root():
    return {'message':'Music AI Solutions API'}
