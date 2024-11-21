from fastapi import FastAPI, Request, HTTPException
from bson import ObjectId
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter
from modals.note import Note
from schemas.note import noteEntity,notesEntity
from config.db import conn
from fastapi.templating import Jinja2Templates


note = APIRouter()
templates = Jinja2Templates(directory="templates")

@note.get("/", response_class=HTMLResponse)
async def home(request: Request):
    docs = conn.notes.notes.find({})
    newDocs = []
    for doc in docs:
        newDocs.append({
            "id" : doc["_id"],
            "title" : doc["title"],
            "content" : doc["content"],
            "is_important" : doc["is_important"]
        })
    return templates.TemplateResponse(
        request=request, name="home.html", context={"newDocs" : newDocs}
    )

    
@note.post("/add/")
async def add_note(request: Request) -> RedirectResponse:  
    form = await request.form()  
    formDict = dict(form)  
    formDict["is_important"] = "is_important" in formDict  
    new_note = conn.notes.notes.insert_one(formDict)
    return RedirectResponse(url="/", status_code=303)


@note.post("/update/{note_id}")
async def update_note(note_id: str, request: Request):
    try:
        form = await request.form()  # Parse the form data
        formDict = dict(form)
        
        # Handle the `is_important` field safely
        formDict["is_important"] = "is_important" in formDict  # Default to False if not present

        try:
            # Convert `note_id` to ObjectId
            note_id = ObjectId(note_id)
        except Exception:
            return {"error": "Invalid note_id format", "status_code": 400}

        # Prepare the update query
        update_query = {
            "$set": {
                "title": formDict.get("title"),
                "content": formDict.get("content"),
                "is_important": formDict.get("is_important"),
            }
        }

        # Perform the update in the database
        result = conn.notes.notes.update_one({"_id": note_id}, update_query)


        if result.modified_count == 1:
            return RedirectResponse(url="/", status_code=303)  # Redirect after successful update
        else:
            return RedirectResponse(url="/", status_code=303)  # Redirect after successful update

    except Exception as e:
        return {"e" : e}
    
    
    
@note.get("/find_notes/{string}")
async def find_notes(string: str):
    try:
        notes_cursor = conn.notes.notes.find({"title": {"$regex": string, "$options": "i"}})
        notes_list = notesEntity(notes_cursor)
        return notes_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@note.get("/get_all_notes/")
async def get_all_notes():
    docs = conn.notes.notes.find({})
    newDocs = notesEntity(docs)
    
    return newDocs