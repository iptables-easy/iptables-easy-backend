from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class NodeCreate(BaseModel):
    name: str
    hostname: str
    description: Optional[str] = None


class NodeResponse(BaseModel):
    id: int
    name: str
    hostname: str
    status: str
    agent_url: Optional[str]
    agent_token: Optional[str]
    description: Optional[str]
    last_heartbeat: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class IptablesRuleCreate(BaseModel):
    node_id: int
    chain: str
    action: str
    protocol: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    port: Optional[int] = None
    description: Optional[str] = None


class IptablesRuleResponse(BaseModel):
    id: int
    node_id: int
    chain: str
    action: str
    protocol: Optional[str]
    source_ip: Optional[str]
    destination_ip: Optional[str]
    port: Optional[int]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentRegisterRequest(BaseModel):
    name: str
    hostname: str
    description: Optional[str] = None
    agent_url: Optional[str] = None
