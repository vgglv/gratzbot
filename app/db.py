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
users_ref = db.reference("/Users/")
outputs_ref = db.reference("/Outputs/")
users = users_ref.get()
outputs = outputs_ref.get()

def getUser(userId: str, userName : str):
    if userId in users:
        return users[userId]
    else:
        return createUser(userId, userName)

def setUserData(userId: str, name: str, gratzAmount: int, token: int, unlimited: bool):
    myUser = getUser(userId)
    value = {
        "amount": gratzAmount,
        "name": name,
        "token": token,
        "unlimited": unlimited
    }
    if not myUser:
        users_ref.child(userId).set(value)
    else:
        users_ref.child(userId).update(value)
    
    users[userId] = value
    return users[userId]

def createUser(userId: str, name: str):
    return setUserData(userId, name, 0, 11, False)

def getOutput(amount: str):
    if amount in outputs:
        return outputs[amount]
    else:
        return None