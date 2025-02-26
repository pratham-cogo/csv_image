from auth import verify_password, create_access_token
from services.users.models.users import User
from services.users.params import LoginUser
from fastapi import HTTPException, status

def login_user(request: LoginUser) -> dict:
    user: User = User.get_or_none(User.username == request.username)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}