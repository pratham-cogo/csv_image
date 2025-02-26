from auth import hash_password
from services.users.models.users import User
from database import db
from services.users.params import CreateUser

def register_user(request: CreateUser) -> User:
    hashed_password = hash_password(request.password)
    with db.atomic():
        user: User = User.create(username=request.username, password=hashed_password)
    return {"id": user.id, "username": user.username}