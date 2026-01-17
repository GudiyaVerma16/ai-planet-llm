from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Workflow Schemas
class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class WorkflowCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: List[Node]
    edges: List[Edge]

class WorkflowResponse(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentUpload(BaseModel):
    filename: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    file_metadata: Optional[Dict[str, Any]]  # Renamed to match model
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Schemas
class ChatQuery(BaseModel):
    workflow_id: Optional[int] = None
    query: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class ChatResponse(BaseModel):
    response: str
    execution_log: Optional[List[Dict[str, Any]]] = None

class ChatLogResponse(BaseModel):
    id: int
    workflow_id: Optional[int]
    query: str
    response: str
    execution_log: Optional[List[Dict[str, Any]]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Component Configuration Schemas
class ComponentConfig(BaseModel):
    component_type: str
    config: Dict[str, Any]
