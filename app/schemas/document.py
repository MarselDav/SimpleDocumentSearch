from pydantic import BaseModel
from datetime import datetime


class Document(BaseModel):
    id : int
    text : str
    rubrics : list[str]
    created_date : datetime