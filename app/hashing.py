from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def bcrypt(password: str):
    print("error")
    return pwd_cxt.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_cxt.verify(plain_password, hashed_password)


# def verify_client_secret(plain_secret, hashed_secret):
#    return pwd_cxt.verify(plain_secret, hashed_secret)
