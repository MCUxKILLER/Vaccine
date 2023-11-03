from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    _id: str
    fullname:str
    username: str
    dob: str
    password: str
    gender: str
    mobile_no: str
    vaccines: list[str] = []