from pydantic import BaseModel
from typing import List


class User(BaseModel):
    _id: str
    fullname:str
    username: str
    dob: str
    password: str
    gender: str
    mobile_no: str
    vaccines: List[str] = []