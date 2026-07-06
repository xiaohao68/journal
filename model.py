from pydantic import BaseModel

class QueryRequest(BaseModel):
    journal:str

class Journal_Response(BaseModel):
    journal_information:str
