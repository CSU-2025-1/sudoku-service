from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import UserModel


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


class UserRepository(BaseRepository):
    async def add_user(self, username: str, hashed_password: str) -> UserModel:
        try:
            new_user = UserModel(username=username, password=hashed_password)
            self.session.add(new_user)
            await self.session.commit()
            return new_user.id
        except Exception as e:
            print(e)
            return None
        finally:
            await self.session.rollback()

    async def get_by_username(self, username: str) -> UserModel:
        result = await self.session.execute(
            select(UserModel).filter(UserModel.username == username).limit(1)
        )
        result = result.scalar_one_or_none()
        if not result:
            raise RuntimeError("User does not exist!")
        return result