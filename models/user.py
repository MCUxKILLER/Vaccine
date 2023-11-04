from pydantic import BaseModel
from typing import Dict, Any


class User(BaseModel):
    _id: str
    fullname:str
    username: str
    dob: str
    password: str
    gender: str
    mobile_no: str
    vaccines: Dict[str, Any] = []