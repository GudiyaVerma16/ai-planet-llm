from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Workflow
from app.schemas import WorkflowCreate, WorkflowResponse
from typing import List

router = APIRouter()

@router.post("", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow"""
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        nodes=[node.dict() for node in workflow.nodes],
        edges=[edge.dict() for edge in workflow.edges]
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.get("", response_model=List[WorkflowResponse])
async def get_workflows(db: Session = Depends(get_db)):
    """Get all workflows"""
    workflows = db.query(Workflow).all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get a specific workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Update a workflow"""
    db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db_workflow.name = workflow.name
    db_workflow.description = workflow.description
    db_workflow.nodes = [node.dict() for node in workflow.nodes]
    db_workflow.edges = [edge.dict() for edge in workflow.edges]
    
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Delete a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted successfully"}
