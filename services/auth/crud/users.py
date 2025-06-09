from db.models import UserModel
from sqlalchemy.orm import Session


def get_users(db: Session):
    return db.query(UserModel).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_name(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()


def create_user(db: Session, username: str, password: str):
    db_user = UserModel(username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user