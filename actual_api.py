import json
from fastapi import FastAPI, HTTPException, status


from models.user import User
from config.db import conn
from urllib.parse import unquote

app = FastAPI()


@app.get("/find")
async def find_all_user():
    # print([doc['username'] for doc in conn.CoVacMis.users.find()])
    return [doc["username"] for doc in conn.CoVacMis.users.find()]


@app.post("/create")
async def create_user(user: User):
    conn.CoVacMis.users.insert_one(dict(user))
    return {
        "message": "User created successfully",
        "username": user.username,
    }


@app.get("/login/{username}/{password}")
async def find_one_user(username, password):
    a = conn.CoVacMis.users.find_one(
        {"$and": [{"username": username}, {"password": password}]}
    )

    if a is None:
        return {}
    else:
        return {
            "username": a["username"],
            "password": a["password"],
            "fullname": a["fullname"],
            "dob": a["dob"],
            "gender": a["gender"],
            "mobile_no": a["mobile_no"],
            "vaccines": a["vaccines"],
        }


@app.get("/vaccines")
async def get_vaccines_list():
    # vaccines = []
    vaccines = {}
    for doc in conn.CoVacMis.Vaccine.find():
        vaccines[doc["name"]] = {
            "Age_group": doc["Age_group"],
            "dose_count": doc["dose_count"],
        }
        # vaccines[doc["name"]] = doc["Age_group"]
    return vaccines


@app.get("/vaccines/{vaccine}")
async def get_vaccine(vaccine):
    vaccine_data = conn.CoVacMis.Vaccine.find_one({"name": vaccine})
    if vaccine_data is None:
        return {}
    else:
        vaccine_data.pop("_id")
    return vaccine_data


@app.get("/price/{company}/{vaccine}")
async def get_price(company, vaccine):
    return conn.CoVacMis.Company.find_one({"Company": company})["vaccines"][vaccine]


@app.post("/vaccinate")
async def vaccinate(body):
    # Body -> username, vaccine_name, date_of_vaccination
    #   vaccine_name -> { dose_count: 1, date: 27-05-2018}
    body = json.loads(body)
    vaccine_name = body["name"]
    username = body["username"]
    date_of_vaccination = body.get("date", "-")

    vaccines = conn.CoVacMis.users.find_one({"username": username})["vaccines"]
    if (vaccines.get(vaccine_name, False)):
        vaccine = vaccines[vaccine_name]
        vaccine["dose_count"] = vaccine.get("dose_count", 0) + 1
        vaccine["date_of_vaccination"] = date_of_vaccination
    else:
        vaccines[vaccine_name] = {
            "dose_count": 1,
            "date_of_vaccination": date_of_vaccination
        }
    
    conn.CoVacMis.users.update_one({"username": username}, {"$set": {"vaccines": vaccines}})

    return 1