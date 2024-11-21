from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse

from pymongo import MongoClient


app = FastAPI()



conn = MongoClient("mongodb://localhost:27017/notes")


# @app.get("/")
# async def root():
#     return {"message": "Hello World you"}


