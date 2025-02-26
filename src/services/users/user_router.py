from fastapi import APIRouter, Depends, HTTPException, status
from services.users.models.users import User
from services.users.params import CreateUser, LoginUser
from auth import verify_password, create_access_token, authenticate_user
from services.users.apis.register import register_user
from services.users.apis.login import login_user

user = APIRouter()

@user.post("/register")
def register(request: CreateUser):
    return register_user(request)

@user.post("/login")
def login(request: LoginUser):
    return login_user(request)