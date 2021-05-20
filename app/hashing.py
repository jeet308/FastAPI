from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def bcrypt(password: str):
    print('error')
    return pwd_cxt.hash(password)


def verify_password(hashed_password, plain_password):
    return pwd_cxt.verify(plain_password, hashed_password)
