from core.auth import verify_password, get_password_hash, create_access_token, is_token_valid
from fastapi import HTTPException
from repositories.users import UserRepository
from schemas.users import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, user_create: UserCreate):
        exists = await self.user_repo.get_by_username(user_create.username)
        if exists:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        created_user = await self.user_repo.add_user(
            username=user_create.username,
            hashed_password=get_password_hash(user_create.password)
        )

        token = create_access_token({"sub": user_create.username})
        return {"access_token": token, "token_type": "bearer"}
    
    async def authenticate_user(self, username: str, password: str):
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    
    async def token_valid(token: str):
        if is_token_valid(token):
            return True
        else:
            raise HTTPException(status_code=400, detail="Invalid token")