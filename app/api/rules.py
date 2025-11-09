from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import IptablesRuleCreate, IptablesRuleResponse
from app.models import IptablesRule, Node

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/", response_model=IptablesRuleResponse)
def create_rule(rule: IptablesRuleCreate, created_by_id: int, db: Session = Depends(get_db)):
    # Verify node exists
    db_node = db.query(Node).filter(Node.id == rule.node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db_rule = IptablesRule(
        node_id=rule.node_id,
        chain=rule.chain,
        action=rule.action,
        protocol=rule.protocol,
        source_ip=rule.source_ip,
        destination_ip=rule.destination_ip,
        port=rule.port,
        description=rule.description,
        created_by_id=created_by_id
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/", response_model=list[IptablesRuleResponse])
def list_rules(node_id: int = None, db: Session = Depends(get_db)):
    query = db.query(IptablesRule)
    if node_id:
        query = query.filter(IptablesRule.node_id == node_id)
    rules = query.all()
    return rules


@router.get("/{rule_id}", response_model=IptablesRuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = db.query(IptablesRule).filter(IptablesRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return db_rule


@router.put("/{rule_id}", response_model=IptablesRuleResponse)
def update_rule(rule_id: int, rule: IptablesRuleCreate, db: Session = Depends(get_db)):
    db_rule = db.query(IptablesRule).filter(IptablesRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db_rule.chain = rule.chain
    db_rule.action = rule.action
    db_rule.protocol = rule.protocol
    db_rule.source_ip = rule.source_ip
    db_rule.destination_ip = rule.destination_ip
    db_rule.port = rule.port
    db_rule.description = rule.description
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = db.query(IptablesRule).filter(IptablesRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(db_rule)
    db.commit()
    return {"message": "Rule deleted"}
