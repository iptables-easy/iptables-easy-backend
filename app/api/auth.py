from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import secrets
from app.database import get_db
from app.schemas import UserCreate, UserResponse, TokenResponse, AgentRegisterRequest
from app.models import User, Node
from app.security import verify_password, get_password_hash, create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=TokenResponse)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not verify_password(password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user(token: str, db: Session = Depends(get_db)):
    from app.security import verify_token
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/register-agent")
def register_agent(agent_data: AgentRegisterRequest, db: Session = Depends(get_db)):
    # Check if node with this name exists (should be created via dashboard first)
    existing_node = db.query(Node).filter(Node.name == agent_data.name).first()
    if not existing_node:
        raise HTTPException(status_code=404, detail="Node not found. Please create the node in the dashboard first.")
    
    # Update existing node with agent information
    existing_node.agent_url = agent_data.agent_url
    existing_node.agent_token = secrets.token_urlsafe(32)
    existing_node.status = "online"
    existing_node.last_heartbeat = datetime.utcnow()
    
    db.commit()
    db.refresh(existing_node)
    
    return {
        "node_id": existing_node.id,
        "agent_token": existing_node.agent_token,
        "message": "Agent registered successfully. Node status updated to online."
    }
