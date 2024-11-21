def noteEntity(item) -> dict:
    print("item", item)
    return {
        "id": str(item["_id"]),
        "title": item["title"],
        "content": item["content"],
        "is_important": item["is_important"],    
    }
    
def notesEntity(items) -> list:
    return [noteEntity(item) for item in items]