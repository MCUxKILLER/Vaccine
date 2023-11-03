from fastapi import APIRouter, HTTPException, status

from models.user import User
from config.db import conn
from bson import ObjectId
from schemas.user import userEntity, usersEntity

user = APIRouter()


@user.get("/find")
async def find_all_user():
    # print(usersEntity(conn.CoVacMis.users.find()))
    return usersEntity(conn.CoVacMis.users.find())


@user.post("/create")
async def create_user(user: User):
    conn.CoVacMis.users.insert_one(dict(user))
    return usersEntity(conn.CoVacMis.users.find())


@user.get("/username/{username}/{password}")
async def find_one_user(username, password):
    a = conn.CoVacMis.users.find_one(
        {"$and": [{"username": username}, {"password": password}]}
    )

    if a is None:
        return {}
    else:
        return userEntity(a)
