from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models import Owner
from ..schemas import (
    OwnerCreate,
    OwnerUpdate, 
    OwnerResponse
)

router = APIRouter(prefix="/api/v1/owners", tags=["owners"])


@router.get("/", response_model=List[OwnerResponse])
def list_owners(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all owners with pagination"""
    owners = db.query(Owner).filter(Owner.is_active == True).offset(skip).limit(limit).all()
    return owners


@router.post("/", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
def create_owner(
    owner_data: OwnerCreate,
    db: Session = Depends(get_db)
):
    """Create new owner"""
    
    # Check if name already exists
    existing = db.query(Owner).filter(Owner.name == owner_data.name).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Owner with name '{owner_data.name}' already exists"
        )
    
    # Create owner
    db_owner = Owner(
        name=owner_data.name,
        display_name=owner_data.display_name,
        email=owner_data.email,
        is_active=owner_data.is_active
    )
    
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    
    return db_owner


@router.get("/{owner_name}", response_model=OwnerResponse)
def get_owner(
    owner_name: str,
    db: Session = Depends(get_db)
):
    """Get owner by name"""
    owner = db.query(Owner).filter(Owner.name == owner_name).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner '{owner_name}' not found"
        )
    
    return owner


@router.put("/{owner_name}", response_model=OwnerResponse)
def update_owner(
    owner_name: str,
    owner_data: OwnerUpdate,
    db: Session = Depends(get_db)
):
    """Update owner data"""
    owner = db.query(Owner).filter(Owner.name == owner_name).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner '{owner_name}' not found"
        )
    
    # Update only provided fields
    for field, value in owner_data.dict(exclude_unset=True).items():
        setattr(owner, field, value)
    
    db.commit()
    db.refresh(owner)
    
    return owner


@router.delete("/{owner_name}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_owner(
    owner_name: str,
    db: Session = Depends(get_db)
):
    """Deactivate owner (soft delete)"""
    owner = db.query(Owner).filter(Owner.name == owner_name).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner '{owner_name}' not found"
        )
    
    owner.is_active = False
    db.commit()