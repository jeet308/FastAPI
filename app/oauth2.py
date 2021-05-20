from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models,  database, tokens, hashing


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

get_db = database.get_db


def get_user(db, username: str):
    return db.query(models.Client).filter(models.Client.username == username).first()


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not hashing.verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, tokens.SECRET_KEY, algorithms=[tokens.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data)
    if user is None:
        raise credentials_exception
    return user
