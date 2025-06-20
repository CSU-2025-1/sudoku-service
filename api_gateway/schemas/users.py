from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str