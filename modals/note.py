from pydantic import BaseModel


class Note(BaseModel):
    title: str
    content: str
    is_important : bool = False
    