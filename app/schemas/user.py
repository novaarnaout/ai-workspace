from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    name: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)