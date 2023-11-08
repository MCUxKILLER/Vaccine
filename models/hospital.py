from pydantic import BaseModel
from typing import List,Dict,Any

class Hospitals(BaseModel):
    hospitalName:str
    location : list(str)=[]
    password:str
    userOrder:List(Dict[str,Any])=[]
