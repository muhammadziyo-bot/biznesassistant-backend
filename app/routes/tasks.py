"""
Task management routes for BiznesAssistant
Complete CRUD operations for tasks with assignment and filtering
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority, TaskComment
from app.models.tenant import Tenant
from app.models.company import Company
from app.utils.auth import get_current_active_user, get_current_tenant
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for request/response
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = TaskPriority.MEDIUM.value
    assigned_to: Optional[int] = None
    due_date: Optional[str] = None
    status: str = TaskStatus.TODO.value

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    created_by: int
    tenant_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Include related user info
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class TaskCommentCreate(BaseModel):
    content: str

class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    content: str
    created_by: int
    created_at: datetime
    author_name: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    due_date_from: Optional[str] = Query(None, description="Filter due date from"),
    due_date_to: Optional[str] = Query(None, description="Filter due date to"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get tasks with filtering and pagination."""
    company_id = current_user.company_id or 1
    
    # Build query
    query = db.query(Task).filter(
        Task.tenant_id == tenant_id,
        Task.company_id == company_id
    )
    
    # Apply filters
    if status:
        query = query.filter(Task.status == status)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)
    
    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)
    
    # Get tasks with user relationships
    tasks = query.offset(skip).limit(limit).all()
    
    # Enrich with user names
    task_responses = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status,
            "created_by": task.created_by,
            "tenant_id": task.tenant_id,
            "company_id": task.company_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at,
            "assignee_name": None,
            "creator_name": None
        }
        
        # Get assignee name
        if task.assigned_to:
            assignee = db.query(User).filter(User.id == task.assigned_to).first()
            if assignee:
                task_dict["assignee_name"] = assignee.full_name or assignee.username
        
        # Get creator name
        if task.created_by:
            creator = db.query(User).filter(User.id == task.created_by).first()
            if creator:
                task_dict["creator_name"] = creator.full_name or creator.username
        
        task_responses.append(TaskResponse(**task_dict))
    
    return task_responses

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create a new task."""
    company_id = current_user.company_id or 1
    
    # Validate assigned user exists and belongs to same company
    if task.assigned_to:
        assignee = db.query(User).filter(
            User.id == task.assigned_to,
            User.company_id == company_id
        ).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user not found or not in same company"
            )
    
    # Parse due date
    due_date = None
    if task.due_date:
        try:
            due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid due date format. Use ISO format."
            )
    
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        assigned_to=task.assigned_to,
        due_date=due_date,
        status=task.status,
        created_by=current_user.id,
        tenant_id=tenant_id,
        company_id=company_id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Enrich with user names
    task_dict = {
        "id": db_task.id,
        "title": db_task.title,
        "description": db_task.description,
        "priority": db_task.priority,
        "assigned_to": db_task.assigned_to,
        "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
        "status": db_task.status,
        "created_by": db_task.created_by,
        "tenant_id": db_task.tenant_id,
        "company_id": db_task.company_id,
        "created_at": db_task.created_at,
        "updated_at": db_task.updated_at,
        "completed_at": db_task.completed_at,
        "assignee_name": None,
        "creator_name": current_user.full_name or current_user.username
    }
    
    if db_task.assigned_to:
        assignee = db.query(User).filter(User.id == db_task.assigned_to).first()
        if assignee:
            task_dict["assignee_name"] = assignee.full_name or assignee.username
    
    return TaskResponse(**task_dict)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get a specific task by ID."""
    company_id = current_user.company_id or 1
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.tenant_id == tenant_id,
        Task.company_id == company_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Enrich with user names
    task_dict = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "assigned_to": task.assigned_to,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "created_by": task.created_by,
        "tenant_id": task.tenant_id,
        "company_id": task.company_id,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at,
        "assignee_name": None,
        "creator_name": None
    }
    
    # Get assignee name
    if task.assigned_to:
        assignee = db.query(User).filter(User.id == task.assigned_to).first()
        if assignee:
            task_dict["assignee_name"] = assignee.full_name or assignee.username
    
    # Get creator name
    if task.created_by:
        creator = db.query(User).filter(User.id == task.created_by).first()
        if creator:
            task_dict["creator_name"] = creator.full_name or creator.username
    
    return TaskResponse(**task_dict)

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Update a task."""
    company_id = current_user.company_id or 1
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.tenant_id == tenant_id,
        Task.company_id == company_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    
    # Handle due date parsing
    if "due_date" in update_data and update_data["due_date"]:
        try:
            update_data["due_date"] = datetime.fromisoformat(update_data["due_date"].replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid due date format. Use ISO format."
            )
    
    # Handle status change to completed
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED.value:
        update_data["completed_at"] = datetime.utcnow()
    
    # Validate assigned user
    if "assigned_to" in update_data and update_data["assigned_to"]:
        assignee = db.query(User).filter(
            User.id == update_data["assigned_to"],
            User.company_id == company_id
        ).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user not found or not in same company"
            )
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Enrich with user names
    task_dict = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "assigned_to": task.assigned_to,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "created_by": task.created_by,
        "tenant_id": task.tenant_id,
        "company_id": task.company_id,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at,
        "assignee_name": None,
        "creator_name": None
    }
    
    # Get assignee name
    if task.assigned_to:
        assignee = db.query(User).filter(User.id == task.assigned_to).first()
        if assignee:
            task_dict["assignee_name"] = assignee.full_name or assignee.username
    
    # Get creator name
    if task.created_by:
        creator = db.query(User).filter(User.id == task.created_by).first()
        if creator:
            task_dict["creator_name"] = creator.full_name or creator.username
    
    return TaskResponse(**task_dict)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Delete a task."""
    company_id = current_user.company_id or 1
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.tenant_id == tenant_id,
        Task.company_id == company_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get comments for a task."""
    company_id = current_user.company_id or 1
    
    # Verify task exists
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.tenant_id == tenant_id,
        Task.company_id == company_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).all()
    
    comment_responses = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.created_by).first()
        comment_dict = {
            "id": comment.id,
            "task_id": comment.task_id,
            "content": comment.content,
            "created_by": comment.created_by,
            "created_at": comment.created_at,
            "author_name": author.full_name or author.username if author else "Unknown"
        }
        comment_responses.append(TaskCommentResponse(**comment_dict))
    
    return comment_responses

@router.post("/{task_id}/comments", response_model=TaskCommentResponse)
async def create_task_comment(
    task_id: int,
    comment: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Add a comment to a task."""
    company_id = current_user.company_id or 1
    
    # Verify task exists
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.tenant_id == tenant_id,
        Task.company_id == company_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db_comment = TaskComment(
        task_id=task_id,
        content=comment.content,
        created_by=current_user.id
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    comment_dict = {
        "id": db_comment.id,
        "task_id": db_comment.task_id,
        "content": db_comment.content,
        "created_by": db_comment.created_by,
        "created_at": db_comment.created_at,
        "author_name": current_user.full_name or current_user.username
    }
    
    return TaskCommentResponse(**comment_dict)
