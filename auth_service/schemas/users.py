from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    username: str


class UserCreate(BaseModel):
    username: str
    password: str