from pydantic import BaseModel


class UserUpdate(BaseModel):
    name: str
    email: str