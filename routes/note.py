from fastapi import FastAPI, Request, HTTPException, Query, Depends
from bson import ObjectId
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi import APIRouter
from modals.note import Note
from schemas.note import noteEntity,notesEntity
from config.db import *
from fastapi.templating import Jinja2Templates
import json
import os
from fastapi import UploadFile, File
from pathlib import Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from static.paths import *

note = APIRouter()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")


@note.get("/users/me")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"username": credentials.username, "password": credentials.password}


@note.get("/", response_class=HTMLResponse)
async def home(request: Request):
    docs = users_collection.find({}).sort("is_important", -1)
    newDocs = notesEntity(docs)
    return templates.TemplateResponse(
        request=request, name="home.html", context={"newDocs" : newDocs}
    )

    
# @note.post("/add/")
# async def add_note(request: Request) -> RedirectResponse:  
#     form = await request.form()  
#     formDict = dict(form)  
#     formDict["is_important"] = "is_important" in formDict  
#     new_note = users_collection.insert_one(formDict)
#     return RedirectResponse(url="/", status_code=303)


# @note.post("/update/{note_id}")
# async def update_note(note_id: str, request: Request):
#     try:
#         form = await request.form()  # Parse the form data
#         formDict = dict(form)
        
#         # Handle the `is_important` field safely
#         formDict["is_important"] = "is_important" in formDict  # Default to False if not present

#         try:
#             # Convert `note_id` to ObjectId
#             note_id = ObjectId(note_id)
#         except Exception:
#             return {"error": "Invalid note_id format", "status_code": 400}

#         update_query = {
#             "$set": {
#                 "title": formDict.get("title"),
#                 "content": formDict.get("content"),
#                 "is_important": formDict.get("is_important"),
#             }
#         }

#         result = users_collection.update_one({"_id": note_id}, update_query)

#         return RedirectResponse(url="/", status_code=303)

#     except Exception as e:
#         return {"e" : e}
    
    
@note.post("/add/")
async def add_note(request: Request, noteFile: UploadFile = File(None)) -> RedirectResponse:
    form = await request.form()
    formDict = dict(form)
    formDict["is_important"] = "is_important" in formDict

    # Handle file upload
    if noteFile.filename:
        file_location = os.path.join(NOTES_PATH, noteFile.filename)
        with open(file_location, "wb") as file:
            file.write(await noteFile.read())
        formDict["noteFile"] = file_location 
    else:
        formDict["noteFile"] = None
    new_note = users_collection.insert_one(formDict)
    return RedirectResponse(url="/", status_code=303)


@note.post("/update/{note_id}")
async def update_note(note_id: str, request: Request, noteFile: UploadFile = File(None)):
    try:
        form = await request.form()  
        formDict = dict(form)

        formDict["is_important"] = "is_important" in formDict

        try:
            note_id = ObjectId(note_id)
        except Exception:
            return {"error": "Invalid note_id format", "status_code": 400}

        update_query = {
            "$set": {
                "title": formDict.get("title"),
                "content": formDict.get("content"),
                "is_important": formDict.get("is_important"),
            }
        }
        
        if noteFile.filename:
            file_location = os.path.join(NOTES_PATH, noteFile.filename)
            with open(file_location, "wb") as file:
                file.write(await noteFile.read())
            update_query["$set"]["noteFile"] = file_location
        elif formDict.get("deleteFile") == "DELETE":
            update_query["$set"]["noteFile"] = ""

        result = users_collection.update_one({"_id": note_id}, update_query)
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return {"error": str(e)}
   
    
@note.get("/delete/{note_id}")
async def delete_note(note_id: str):
    try:
        note_id_obj = ObjectId(note_id)
    except Exception:
        return JSONResponse(
            content={"error": "Invalid note ID"},
            status_code=400
        )

    result = users_collection.delete_one({"_id": note_id_obj})

    return RedirectResponse(url="/", status_code=303)

    
@note.get("/find_notes_by_id/{note_id}")
async def find_notes(note_id: str):
    try:
        note = users_collection.find_one({"_id": ObjectId(note_id)})
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return JSONResponse(noteEntity(note))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@note.get("/find_notes/{string}")
async def find_notes(string: str):
    try:
        notes_cursor = users_collection.find({"title": {"$regex": string, "$options": "i"}}).sort("is_important", -1)
        notes_list = notesEntity(notes_cursor)
        return notes_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@note.get("/get_all_notes/")
async def get_all_notes(request: Request, filter: str | None = None):
    filter_dict = json.loads(filter) if filter else {} 
    docs = []
    if "sort" in filter_dict:
        sort_order = 1 if filter_dict.get('sort', '').upper() == "ASC" else -1
        docs = users_collection.find({}).sort("title", sort_order)
    elif "important" in filter_dict:
        docs = users_collection.find({"is_important": filter_dict['important']})
    elif "all" in filter_dict:
        docs = users_collection.find({})
    else:
        docs = users_collection.find({})

    newDocs = notesEntity(docs)
    
    return newDocs
