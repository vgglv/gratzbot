from os import getenv
import base64
import firebase_admin
from firebase_admin import db

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

def getUser(userId: str, userName : str):
    user = db.reference(f"/Users/{userId}").get()
    print(f"getting user {userId}, value: {user}")
    if not user:
        print("user not exist, creating user...")
        user = createUser(userId, userName)
        print(f"created user: {user}")
    return user

def setUserData(userId: str, name: str, gratzAmount: int, token: int, unlimited: bool):
    value = {
        "amount": gratzAmount,
        "name": name,
        "token": token,
        "unlimited": unlimited
    }
    db.reference(f"/Users/{userId}").update(value)
    return value

def createUser(userId: str, name: str):
    userData = {
        "amount": 0,
        "name": name,
        "token": 11,
        "unlimited": False
    }
    db.reference("/Users/").child(userId).set(userData)
    print(f"creating user {userId} with {userData}")
    return userData

def getOutput(amount: str):
    output = db.reference(f"/Outputs/{amount}").get()
    print(f"getting output {output}")
    return output

def getAllUsers():
    return db.reference("/Users/").get()