import uuid

import shortuuid
from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session

from app import database, hashing, models, oauth2
from app import schema_client as sch
from app import utils

router = APIRouter(tags=["Client"])


ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/create-client")
async def create_client(
    # current_user: models.Client = Depends(oauth2.get_current_user),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db),
):

    logger.debug({"username": username})

    try:

        input_data = sch.ClientSchema(username=username, password=password)

    except sch.ValidationError as e:
        raise utils.ValidationException(e)

    hashed_password = hashing.bcrypt(input_data.password)
    client_id = str(uuid.uuid4())
    client_secret = shortuuid.ShortUUID().random(length=30)

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
    }

    client_data = models.Client(
        username=username,
        hashed_password=hashed_password,
        client_id=client_id,
        client_secret=client_secret,
    )
    db.add(client_data)
    db.commit()
    db.refresh(client_data)

    return JSONResponse({"data": data, "status": "success"}, status_code=200)


@router.get("/client-list")
def get_client(
    db: Session = Depends(database.get_db),
    current_user: models.Client = Depends(oauth2.get_current_user),
):
    client = db.query(models.Client).all()
    return client
