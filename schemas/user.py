def userEntity(item) -> dict:
    return {
        "_id": str(item["_id"]),
        "fullname":item["fullname"],
        "username": item["username"],
        "dob": item["dob"],
        "password": item["password"],
        "gender": item["gender"],
        "mobile_no": item["mobile_no"],
        # "vaccines":item["vaccines"],
    }


def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]
    