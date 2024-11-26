from fastapi import FastAPI, Request, HTTPException, Query, Depends
from bson import ObjectId
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi import APIRouter
from modals.note import Note
from schemas.note import noteEntity,notesEntity
from config.db import conn
from fastapi.templating import Jinja2Templates
import json
from fastapi_pagination import Page, add_pagination, paginate, Params
from fastapi_pagination.bases import AbstractPage
from fastapi import Query
from bson.json_util import dumps
from typing import Optional
import os
from fastapi import UploadFile, File
from pathlib import Path




note = APIRouter()
templates = Jinja2Templates(directory="templates")

@note.get("/", response_class=HTMLResponse)
async def home(request: Request):
    docs = conn.notes.notes.find({}).sort("is_important", -1)
    newDocs = []
    for doc in docs:
        newDocs.append({
            "id" : doc["_id"],
            "title" : doc["title"],
            "content" : doc["content"],
            "noteFile" : doc["noteFile"] if "noteFile" in doc else '',
            "is_important" : doc["is_important"]
        })
    return templates.TemplateResponse(
        request=request, name="home.html", context={"newDocs" : newDocs}
    )

    
# @note.post("/add/")
# async def add_note(request: Request) -> RedirectResponse:  
#     form = await request.form()  
#     formDict = dict(form)  
#     formDict["is_important"] = "is_important" in formDict  
#     new_note = conn.notes.notes.insert_one(formDict)
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

#         result = conn.notes.notes.update_one({"_id": note_id}, update_query)

#         return RedirectResponse(url="/", status_code=303)

#     except Exception as e:
#         return {"e" : e}
    
@note.post("/add/")
async def add_note(request: Request, noteFile: UploadFile = File(None)) -> RedirectResponse:
    FILE_SAVE_DIR = "static/files/imgs/noteFiles"
    form = await request.form()
    formDict = dict(form)
    formDict["is_important"] = "is_important" in formDict

    # Handle file upload
    if noteFile.filename:
        print("noteFile", noteFile)
        file_location = os.path.join(FILE_SAVE_DIR, noteFile.filename)
        with open(file_location, "wb") as file:
            file.write(await noteFile.read())
        formDict["noteFile"] = file_location  # Save file path in the database
    else:
        formDict["noteFile"] = None
    print("formDict", formDict)
    new_note = conn.notes.notes.insert_one(formDict)
    return RedirectResponse(url="/", status_code=303)


@note.post("/update/{note_id}")
async def update_note(note_id: str, request: Request, noteFile: UploadFile = File(None)):
    try:
        FILE_SAVE_DIR = "static/files/imgs/noteFiles"
        form = await request.form()  # Parse the form data
        formDict = dict(form)

        # Handle the `is_important` field safely
        formDict["is_important"] = "is_important" in formDict

        try:
            # Convert `note_id` to ObjectId
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

        # Handle file upload
        if noteFile.filename:
            file_location = os.path.join(FILE_SAVE_DIR, noteFile.filename)
            with open(file_location, "wb") as file:
                file.write(await noteFile.read())
            update_query["$set"]["noteFile"] = file_location  # Update file path in the database

        # Update the note in the database
        result = conn.notes.notes.update_one({"_id": note_id}, update_query)
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return {"error": str(e)}
    
@note.get("/delete/{note_id}")
async def delete_note(note_id: str):
    print("note_id:", note_id)
    try:
        note_id_obj = ObjectId(note_id)
    except Exception:
        return JSONResponse(
            content={"error": "Invalid note ID"},
            status_code=400
        )

    result = conn.notes.notes.delete_one({"_id": note_id_obj})

    return RedirectResponse(url="/", status_code=303)

    
@note.get("/find_notes/{string}")
async def find_notes(string: str):
    try:
        print("string", string)
        notes_cursor = conn.notes.notes.find({"title": {"$regex": string, "$options": "i"}}).sort("is_important", -1)
        print("notes_cursor", notes_cursor)
        notes_list = notesEntity(notes_cursor)
        print("notes_list", notes_list)
        return notes_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@note.get("/get_all_notes/")
async def get_all_notes(request: Request, filter: str | None = None):
    filter_dict = json.loads(filter) if filter else {} 
    docs = []
    if "sort" in filter_dict:
        sort_order = 1 if filter_dict.get('sort', '').upper() == "ASC" else -1
        docs = conn.notes.notes.find({}).sort("title", sort_order)
    elif "important" in filter_dict:
        docs = conn.notes.notes.find({"is_important": filter_dict['important']})
    elif "all" in filter_dict:
        docs = conn.notes.notes.find({})
    else:
        docs = conn.notes.notes.find({})

    newDocs = notesEntity(docs)
    
    return newDocs
