from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str

class Chat(BaseModel):
    id: int = Field(alias="id")
    type: str

class Message(BaseModel):
    message_id: int
    user_from: Optional[User] = Field(alias="from")
    chat: Chat
    reply_to_message: Optional['Message'] = None
    text: Optional[str] = None

class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None
