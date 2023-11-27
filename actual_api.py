import json
from fastapi import FastAPI, HTTPException, status
from datetime import datetime


from models.user import User
from config.db import conn
from urllib.parse import unquote

from models.vaccination import Vaccination
from models.hospital import Hospitals
import pytz

app = FastAPI()


@app.get("/find")
async def find_all_user():
    # print([doc['username'] for doc in conn.CoVacMis.users.find()])
    return [doc["username"] for doc in conn.CoVacMis.users.find()]


@app.post("/create")
async def create_user(user: User):

    a = conn.CoVacMis.users.find_one({"username": user.username})
    if a is not None:
        return {
            "message": "Username already taken"
        }
    conn.CoVacMis.users.insert_one(dict(user))
    return {
        "message": "User created successfully"
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
async def vaccinate(body: Vaccination):
    # Body -> username, vaccine_name, date_of_vaccination
    #   vaccine_name -> { dose_count: 1, date: 27-05-2018}
    # body = json.loads(name)
    vaccine_name = body.name
    username = body.username
    date_of_vaccination = body.date_of_vaccination

    vaccines = conn.CoVacMis.users.find_one({"username": username})["vaccines"]
    if vaccines.get(vaccine_name, False):
        vaccine = vaccines[vaccine_name]
        vaccine["dose_count"] = vaccine.get("dose_count", 0) + 1
        vaccine["date_of_vaccination"] = date_of_vaccination
    else:
        vaccines[vaccine_name] = {
            "dose_count": 1,
            "date_of_vaccination": date_of_vaccination,
        }

    conn.CoVacMis.users.update_one(
        {"username": username}, {"$set": {"vaccines": vaccines}}
    )

    return {"success": 1}


@app.get("/hospital/login/{hospitalName}/{password}")
async def hospitalLogin(hospitalName: str, password: str):
    hospitalDetail = conn.CoVacMis.Hospital.find_one(
        {"hospitalName": hospitalName, "password": password}
    )
    return {
        "hospitalId": str(hospitalDetail["_id"]),
        "hospitalName": hospitalDetail["hospitalName"],
    }


@app.get("/hospital/getOrders/{hospitalName}")
async def retrieveOrders(hospitalName: str):
    allOrders = conn.CoVacMis.Hospital.find_one({"hospitalName": hospitalName})[
        "userOrder"
    ]
    date_format = "%d-%m-%Y"
    IST = pytz.timezone('Asia/Kolkata')
    orders = {}
    current_date = datetime.now(IST).date()
    # print(current_date)
    for i in allOrders.keys():
        # print(i)
        parsed_date = datetime.strptime(i, date_format).date()
        # print(parsed_date)
        if parsed_date == current_date:
            orders[i] = allOrders[i]
    return orders


@app.post("/user/order/")
async def placeOrder(body: dict):
    # username, vaccine_name, date, hospital_name

    username = body["username"]
    vaccine_name = body["vaccine_name"]
    date = body["date"]
    hospital_name = body["hospital_name"]
    brand_name = body["brand_name"]
    company_name = body["company_name"]

    user_orders = conn.CoVacMis.users.find_one({"username": username})["orders"]
    if user_orders.get(vaccine_name) is None:
        user_orders[vaccine_name] = {
            "company_name": company_name,
            "brand_name": brand_name,
            "hospital_name": hospital_name,
            "date": date,
        }
    else:
        return {
            "message": "You have already ordered this vaccine",
            "success": 0,
            "vaccine_info": user_orders.get(vaccine_name),
        }

    hospital = conn.CoVacMis.Hospital.find_one({"hospitalName": hospital_name})
    orders = hospital["userOrder"].get(date, {})

    if username in orders:
        return {
            "message": "You have already ordered a vaccine on this date",
            "success": 0,
            "vaccine_info": orders[username],
        }

    orders[username] = {
        "vaccine_name": vaccine_name,
        "company_name": company_name,
        "brand_name": brand_name,
    }

    try:
        with conn.start_session() as session:
            with session.start_transaction():
                conn.CoVacMis.users.update_one(
                    {"username": username},
                    {"$set": {"orders": user_orders}},
                )

                conn.CoVacMis.Hospital.update_one(
                    {"hospitalName": hospital_name},
                    {"$set": {f"userOrder.{date}": orders}},
                )
    except Exception as e:
        print(e)
        return {
            "success": 0,
            "message": "Something went wrong",
            "error": str(e)
        }

    return {
        "message": "You successfully placed the order.",
        "success": 1
    }


@app.post("/hospital/create")
async def hospitalSignUp(body: Hospitals):
    # username,password,latitude,longitude,address,mobilenumber
    # return print(body.hospitalName,body.address)
    hospitals = conn.CoVacMis.Hospital.find_one(
        {"$and": [{"hospitalName": body.hospitalName}, {"address": body.address}]}
    )
    if hospitals:
        return {"success": 0, "hospitalId": "0", "hospitalName": "0"}
    conn.CoVacMis.Hospital.insert_one(dict(body))
    hospitalId = conn.CoVacMis.Hospital.find_one({"hospitalName": body.hospitalName})[
        "_id"
    ]
    hospitalId = str(hospitalId)
    return {"success": 1, "hospitalId": hospitalId, "hospitalName": body.hospitalName}


@app.post("/hospital/orderComplete")
async def hospitalOrderComplete(body: dict):
    hospitalName = body["hospitalName"]
    date = body["date"]
    username = body["username"]

    hospital = conn.CoVacMis.Hospital.find_one({"hospitalName": hospitalName})
    orders = hospital["userOrder"][date]
    vaccine_order = orders[username]
    orders.pop(username)

    user = conn.CoVacMis.users.find_one({"username": username})
    user_doses = user["vaccines"].get(vaccine_order["vaccine_name"], {"dose_count": 0})["dose_count"]
    vaccine_name = vaccine_order.get("vaccine_name")
    user["orders"].pop(vaccine_name)

    user_vaccination = {"dose_count": user_doses + 1, "date_of_vaccination": date}

    try:
        with conn.start_session() as session:
            with session.start_transaction():
                conn.CoVacMis.Hospital.update_one(
                    {"hospitalName": hospitalName},
                    {"$set": {f"userOrder.{date}": orders}},
                )
                conn.CoVacMis.users.update_one(
                    {"username": username},
                    {"$set": {f"vaccines.{vaccine_order['vaccine_name']}": user_vaccination, "orders": user["orders"]}},
                )
    except Exception as e:
        print(e)
        return {
            "success": 0,
            "message": "Something went wrong",
            "error": str(e)
        }


    return {"success": 1}
    # {"hospitalName":"NUPUR HOSPITAL","date":"19-11-2023","username":"xyz123"}


@app.get("/hospital/getData")
async def getHospitalData():
    hospitals = {}
    for doc in conn.CoVacMis.Hospital.find():
        hospitals[str(doc["_id"])] = {
            "hospitalName": doc["hospitalName"],
            "location": doc["location"],
            "address": doc["address"],
        }
    return hospitals


@app.get("/user/orders/{username}")
async def getUserOrders(username: str):
    orders = conn.CoVacMis.users.find_one({"username": username})["orders"]

    if len(orders):
        return {
            "orders": orders,
            "success": 1
        }
    else:
        return {
            "orders": {},
            "success": 0
        }
