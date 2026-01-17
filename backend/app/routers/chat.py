from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatLog
from app.schemas import ChatQuery, ChatResponse, ChatLogResponse
from app.services.workflow_executor import WorkflowExecutor
from typing import List

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    chat_query: ChatQuery,
    db: Session = Depends(get_db)
):
    """Execute workflow and return response"""
    try:
        executor = WorkflowExecutor(db)
        result = executor.execute_workflow(
            query=chat_query.query,
            nodes=chat_query.nodes,
            edges=chat_query.edges
        )
        
        # Save chat log
        chat_log = ChatLog(
            workflow_id=chat_query.workflow_id,
            query=chat_query.query,
            response=result["response"],
            execution_log=result["execution_log"]
        )
        db.add(chat_log)
        db.commit()
        
        return ChatResponse(
            response=result["response"],
            execution_log=result["execution_log"]
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"Chat query error: {error_detail}")
        print(f"Traceback: {traceback_str}")
        
        # If it's a rate limit error, return it as a friendly response instead of 500
        if "rate limit" in error_detail.lower() or "quota" in error_detail.lower():
            return ChatResponse(
                response=f"⚠️ {error_detail}",
                execution_log=[{"node_id": "error", "node_type": "error", "status": "failed", "output": error_detail}]
            )
            
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/logs", response_model=List[ChatLogResponse])
async def get_chat_logs(
    workflow_id: int = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat logs"""
    query = db.query(ChatLog)
    if workflow_id:
        query = query.filter(ChatLog.workflow_id == workflow_id)
    logs = query.order_by(ChatLog.created_at.desc()).limit(limit).all()
    return logs

@router.get("/logs/{log_id}", response_model=ChatLogResponse)
async def get_chat_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific chat log"""
    log = db.query(ChatLog).filter(ChatLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Chat log not found")
    return log
