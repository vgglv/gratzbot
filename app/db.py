from os import getenv
import base64
import firebase_admin
from firebase_admin import db
from app.user import GUser
import time

private_key_encoded = getenv("FIREBASE_PRIVATE_KEY")
private_key_encoded_bytes = private_key_encoded.encode('ascii')
private_key_decoded_bytes = base64.b64decode(private_key_encoded_bytes)
private_key_string = private_key_decoded_bytes.decode('ascii')

cred = firebase_admin.credentials.Certificate({
    "type": "service_account",
    "project_id": getenv("FIREBASE_PROJECT_ID"),
    "client_email": getenv("FIREBASE_CLIENT_EMAIL"),
    "private_key": private_key_string,
    "token_uri": getenv("FIREBASE_TOKEN_URI")
})
default_app = firebase_admin.initialize_app(cred, {'databaseURL': getenv("db_url")})

def getUser(user_id: str, user_name : str) -> GUser:
    user = db.reference(f"/Users/{user_id}").get()
    print(f"getting user {user_id}, value: {user}")
    if not user:
        print("user not exist, creating user...")
        user = createUser(user_id, user_name)
        print(f"created user: {user}")

    result = GUser(
        user_id=user_id,
        name=user_name,
        gratz_amount=user["amount"],
        token=user["token"],
        farm=user["farm"],
        saved_date=user["saved_date"]
    )
    return result

def updateUserInDatabase(user:GUser) -> None:
    value = {
        "amount": user.getGratzAmount(),
        "name": user.getName(),
        "token": user.getToken(),
        "farm": user.getFarm(),
        "saved_date": user.getSavedDate()
    }
    db.reference(f"/Users/{user.getUserId()}").update(value)
    return value

def createUser(userId: str, name: str) -> dict[str, any]:
    current_timestamp = int(time.time())
    userData = {
        "amount": 0,
        "name": name,
        "token": 5,
        "farm": 1,
        "saved_date": current_timestamp
    }
    db.reference("/Users/").child(userId).set(userData)
    return userData

def getAllUsers():
    return db.reference("/Users/").get()
