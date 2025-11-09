from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user")  # admin, user, agent
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rules = relationship("IptablesRule", back_populates="created_by_user")
    nodes = relationship("Node", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hostname = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="offline")  # online, offline
    agent_url = Column(String, nullable=True)
    agent_token = Column(String, unique=True, index=True)
    last_heartbeat = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    rules = relationship("IptablesRule", back_populates="node")
    created_by_user = relationship("User", back_populates="nodes")


class IptablesRule(Base):
    __tablename__ = "iptables_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"))
    chain = Column(String)  # INPUT, OUTPUT, FORWARD
    action = Column(String)  # ACCEPT, DROP, REJECT
    protocol = Column(String, nullable=True)  # tcp, udp, icmp
    source_ip = Column(String, nullable=True)
    destination_ip = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    enabled = Column(Boolean, default=True)
    sync_status = Column(String, default="unknown")  # synced, out_of_sync, unknown
    last_sync = Column(DateTime, nullable=True)
    
    node = relationship("Node", back_populates="rules")
    created_by_user = relationship("User", back_populates="rules")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # create, update, delete
    resource_type = Column(String)  # rule, node, user
    resource_id = Column(Integer)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")
