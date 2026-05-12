from typing import TypedDict


class UserCreate(TypedDict):
    firstname: str
    lastname: str
    email: str
    password: str
    phone_number: str


class UserLogin(TypedDict):
    email: str
    password: str
