def noteEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "title": item["title"],
        "content": item["content"],
        "noteFile" : item["noteFile"] if 'noteFile' in item else '',
        "is_important": item["is_important"],    
    }
    
def notesEntity(items) -> list:
    return [noteEntity(item) for item in items]
    