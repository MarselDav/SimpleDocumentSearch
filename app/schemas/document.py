from pydantic import BaseModel, ConfigDict
from datetime import datetime


class Document(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id : int
    text : str
    created_date : datetime
    rubrics: list[str]

class ElasticResult(BaseModel):
    index : str
    id : str
    result : str

class DeleteDocumentResult(BaseModel):
    elasticsearch_result : ElasticResult
    postgres_result : bool