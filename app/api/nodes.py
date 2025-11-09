from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.schemas import NodeCreate, NodeResponse
from app.models import Node

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.post("/", response_model=NodeResponse)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    db_node = db.query(Node).filter(Node.name == node.name).first()
    if db_node:
        raise HTTPException(status_code=400, detail="Node name already exists")
    
    db_node = Node(
        name=node.name,
        hostname=node.hostname,
        description=node.description,
        status="offline"
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


@router.get("/", response_model=list[NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    nodes = db.query(Node).all()
    return nodes


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: int, db: Session = Depends(get_db)):
    db_node = db.query(Node).filter(Node.id == node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: int, node: NodeCreate, db: Session = Depends(get_db)):
    db_node = db.query(Node).filter(Node.id == node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db_node.name = node.name
    db_node.hostname = node.hostname
    db_node.description = node.description
    db.commit()
    db.refresh(db_node)
    return db_node


@router.delete("/{node_id}")
def delete_node(node_id: int, db: Session = Depends(get_db)):
    db_node = db.query(Node).filter(Node.id == node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db.delete(db_node)
    db.commit()
    return {"message": "Node deleted"}


@router.post("/{node_id}/heartbeat")
def update_heartbeat(node_id: int, db: Session = Depends(get_db)):
    db_node = db.query(Node).filter(Node.id == node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db_node.last_heartbeat = datetime.utcnow()
    db_node.status = "online"
    db.commit()
    db.refresh(db_node)
    return {"message": "Heartbeat updated", "status": "online"}
