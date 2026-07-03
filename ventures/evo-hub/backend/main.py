```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
import logging

app = FastAPI(title="Personalized Evo Learning Path API", version="1.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: str = None

@app.post("/token", response_model=TokenData)
async def login(user: User):
    # Placeholder for actual authentication logic
    if user.username != "admin" or user.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_data = TokenData(username=user.username)
    return token_data

@app.get("/users/me", response_model=TokenData)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # Placeholder for actual authorization logic
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"username": "admin"}

# Example route
@app.get("/learnings/{learning_id}", response_model=str)
async def get_learning(learning_id: int):
    # Placeholder for actual learning retrieval logic
    return f"Learning path {learning_id}"

```