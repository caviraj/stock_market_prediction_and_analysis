import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import User

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    # Try decoding using Supabase JWT Secret if configured
    supabase_secret = os.getenv("SUPABASE_JWT_SECRET")
    if supabase_secret:
        try:
            # Decode using Supabase HS256 JWT key
            payload = jwt.decode(token, supabase_secret, algorithms=["HS256"], options={"verify_aud": False})
            return payload
        except JWTError:
            pass
            
    # Fallback to local JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    
    # Supabase uses 'email' key; fallback to 'sub' key for local tokens
    email: str = payload.get("email") or payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token details")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        # If this is a valid Supabase token, auto-register the user in our public database
        if payload.get("role") == "authenticated" or "iss" in payload:
            user_metadata = payload.get("user_metadata", {})
            full_name = user_metadata.get("full_name") or user_metadata.get("name") or email.split("@")[0]
            
            user = User(
                name=full_name,
                email=email,
                hashed_password="supabase_oauth_login"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(status_code=401, detail="User profile not initialized")
        
    return user
