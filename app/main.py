import asyncio
import uvloop
import uvicorn
from datetime import timedelta
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from app import crud, schemas
from app.auth import verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    authenticate_user, get_current_active_user
from app.log_save.celery_logger import logger
from app.log_save.celery_tasks import send_notification
from app.schemas import UserChangePassword, UserChangeName, Token, UserAuth
from app.database import get_db
from app.cache_token import get_token, set_token
from app.log_save.log_middlware import LogMiddleware


app = FastAPI()
app.add_middleware(LogMiddleware)

@app.get("/push/{device_token}")
async def notify(device_token: str):
    logger.info("Sending notification in background")
    send_notification.delay(device_token)
    return {"message": "Notification sent"}

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    stored_token = await get_token(form_data.username)
    if stored_token:
        logger.info("Returning stored token for user: %s", form_data.username)
        return Token(access_token=stored_token, token_type="bearer")

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error("Failed login attempt for user: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    await set_token(user.username, access_token, ttl=ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.info("User %s logged in successfully, token created", user.username)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[UserAuth, Depends(get_current_active_user)],
):
    logger.info("Getting current user's information")
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[UserAuth, Depends(get_current_active_user)],
):
    logger.info("Getting items for user: %s", current_user.username)
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.post('/register', response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info("Registering new user with email: %s", user.email)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.error("Registration failed: Email already registered for %s", user.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post('/login')
async def login(user: schemas.UserBase, db: Session = Depends(get_db)):
    logger.info("User login attempt with email: %s", user.email)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.info("User %s logged in successfully", user.email)
        return {"message": "You are now logged in"}
    logger.error("Login failed: Invalid email %s", user.email)
    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.post("/logout")
async def logout():
    logger.info("User logged out")
    return {"message": "User logged out successfully"}


@app.post('/change_password')
async def change_password(user: UserChangePassword, db: Session = Depends(get_db)):
    logger.info("Changing password for user: %s", user.email)
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user:
        logger.error("Password change failed: User not found for email %s", user.email)
        raise HTTPException(status_code=404, detail='User not found')
    if not verify_password(user.password, db_user.hashed_password):
        logger.error("Password change failed: Old password is incorrect for user %s", user.email)
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    if user.new_password != user.confirm_new_password:
        logger.error("Password change failed: New passwords do not match for user %s", user.email)
        raise HTTPException(status_code=400, detail="New passwords do not match")
    crud.update_user_password(db=db, db_user=db_user, new_password=user.new_password)
    logger.info("Password changed successfully for user: %s", user.email)
    return {"message": "Password changed successfully"}


@app.get('/get_users')
async def get_users(db: Session = Depends(get_db)):
    logger.info("Getting all users")
    return crud.get_users(db=db)


@app.get("/balance")
async def get_balance(first_name: str, last_name: str, db: Session = Depends(get_db)):
    logger.info("Getting balance for user: %s %s", first_name, last_name)
    user = crud.get_user_by_name(db, first_name, last_name)
    if not user:
        logger.error("Balance get failed: User not found for %s %s", first_name, last_name)
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("Fetched balance for user %s %s: %s", first_name, last_name, user.balance)
    return {"balance": user.balance}


@app.put("/withdraw_balance")
async def withdraw_balance(first_name: str, last_name: str, amount: int, db: Session = Depends(get_db)):
    logger.info("Withdraw balance attempt for user: %s %s, amount: %d", first_name, last_name, amount)
    user = crud.get_user_by_name(db=db, first_name=first_name, last_name=last_name)
    if not user:
        logger.error("Withdrawal failed: User not found for %s %s", first_name, last_name)
        raise HTTPException(status_code=404, detail="User not found")
    crud.withdraw_balance(db=db, user=user, amount=amount)
    logger.info("Withdrawal successful for user: %s %s, new balance: %s", first_name, last_name, user.balance)
    return {"message": "Balance updated", "new_balance": user.balance}


@app.put("/update_profile")
async def update_profile(user: UserChangeName, db: Session = Depends(get_db)):
    logger.info("Updating profile for user: %s %s", user.first_name, user.last_name)
    db_user = crud.get_user_by_name(db=db, first_name=user.first_name, last_name=user.last_name)
    if not db_user:
        logger.error("Profile update failed: User not found for %s %s", user.first_name, user.last_name)
        raise HTTPException(status_code=404, detail="User not found")
    crud.update_user_profile(db=db, user=db_user, new_first_name=user.new_first_name, new_last_name=user.new_last_name)
    logger.info("Profile updated successfully for user: %s %s", user.first_name, user.last_name)
    return {"message": "Profile updated", "first_name": user.first_name, "last_name": user.last_name}


@app.get("/profile")
async def get_profile(first_name: str, last_name: str, db: Session = Depends(get_db)):
    logger.info("Fetching profile for user: %s %s", first_name, last_name)
    user = crud.get_user_by_name(db=db, first_name=first_name, last_name=last_name)
    if not user:
        logger.error("Profile fetch failed: User not found for %s %s", first_name, last_name)
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_profile(db=db, first_name=first_name, last_name=last_name)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
