from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app import models, schemas
from app.auth import get_password_hash


def get_profile(db: Session, first_name: str, last_name: str):
    return db.query(models.User).filter(
        models.User.first_name == first_name,
        models.User.last_name == last_name,
        ).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        balance=user.balance,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, db_user: schemas.User, new_password: str):
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: int = None,
        first_name: str = None,
        last_name: str = None,
        sort_by: str = "id",
        order: str = "asc"
):
    query = db.query(models.User)

    if user_id is not None:
        query = query.filter(models.User.id == user_id)
    if first_name is not None:
        query = query.filter(models.User.first_name == first_name)
    if last_name is not None:
        query = query.filter(models.User.last_name == last_name)

    if order == "desc":
        query = query.order_by(desc(getattr(models.User, sort_by, 'id')))
    else:
        query = query.order_by(asc(getattr(models.User, sort_by, 'id')))

    return query.offset(skip).limit(limit).all()


def get_user_by_name(db: Session, first_name: str, last_name: str):
    return db.query(models.User).filter(
        models.User.first_name == first_name,
        models.User.last_name == last_name
    ).first()


def withdraw_balance(db: Session, user: schemas.User, amount: int):
    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    user.balance -= amount
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(db: Session, user: schemas.User, new_first_name: str, new_last_name: str):
    user.first_name = new_first_name
    user.last_name = new_last_name
    db.commit()
    db.refresh(user)
    return user
