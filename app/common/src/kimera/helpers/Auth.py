import os
from datetime import datetime, timedelta


from fastapi import HTTPException, status, Request
import jwt
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

from fastapi import Depends
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
api_key_scheme = APIKeyHeader(name="Authorization")

class Auth:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SALT", "your-secret-key-is-not-safe-with-me")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 100

    @staticmethod
    async def socket_auth(self, token):
        user = None
        try:
            user = Auth().decode_token(token)
        except Exception as e:
            raise ConnectionRefusedError('authentication failed')
        return user

    async def get_auth(self, request: Request):

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        api_key = None
        token = None
        try:
            token = await oauth2_scheme(request)
        except HTTPException as e:
            if e.status_code == 401:
                api_key = await api_key_scheme(request)
        finally:
            if api_key is not None:
                pass
                # user = Users().check_api_key(api_key=api_key)
                # if user:
                #    token = Auth().create_access_token({"data": user})



        try:
            # Decode the token and extract user information
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            print(payload)
            sub = payload.get("data")
            if sub is None:
                raise credentials_exception

            # Retrieve user from the database (replace this with your actual user retrieval logic)

        except jwt.ExpiredSignatureError:
            raise credentials_exception
        except jwt.InvalidTokenError:
            raise credentials_exception

        sub["isAdmin"] = True if str(sub["role"]) == "22222" else False


        return sub

    def create_access_token(self, data: dict, expires_delta: timedelta = None):

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=120)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token.strip(), self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


