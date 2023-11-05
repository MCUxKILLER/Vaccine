from pydantic import BaseModel

class Vaccination(BaseModel):
    username: str
    name:str
    date_of_vaccination:str = "-"