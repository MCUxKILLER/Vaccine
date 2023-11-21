from pydantic import BaseModel
from typing import List,Dict,Any

class Hospitals(BaseModel):
    hospitalName:str
    location : List[str]
    password:str
    userOrder:Dict[str,Dict[str,str]] = {}
    mob:str
    address:str
    fullAddr:str