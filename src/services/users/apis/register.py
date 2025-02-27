from auth import hash_password
from services.users.models.users import User
from database.db import db
from services.users.params import CreateUser

def register_user(request: CreateUser) -> User:
    hashed_password = hash_password(request.password)
    with db.atomic():
        user: User = User.get_or_none(User.username == request.username)
        if user:
            return "Username not available"

        user: User = User.create(username=request.username, password_hash=hashed_password)
    return {"id": user.id, "username": user.username}