from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import custom_cre, database, models, oauth2, schema_client, tokens

router = APIRouter(tags=["Authentication"])


get_db = database.get_db


ACCESS_TOKEN_EXPIRE_MINUTES = 10


@router.post("/token", response_model=schema_client.Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: custom_cre.CustomOAuth2PasswordRequestForm = Depends(),
):
    user = oauth2.authenticate_user(
        db,
        form_data.username,
        form_data.password,
        form_data.client_id,
        form_data.client_secret,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = tokens.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/")
async def read_users_me(current_user: models.Client = Depends(oauth2.get_current_user)):
    return current_user
