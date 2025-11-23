from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User, ProcessData, SavedFilter
from app.schemas.search import (
    SearchFilters, 
    FilterRequest, 
    DateRange, 
    SaveFilterRequest
)
from app.crud import search as search_crud

router = APIRouter()

@router.get("/process-data")
def search_process_data(
    q: Optional[str] = Query(None, min_length=2, description="Search query"),
    process_id: Optional[int] = None,
    result: Optional[str] = None,
    # Simple date range params for GET convenience
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Search process data using full-text search and basic filters.
    """
    filters = SearchFilters(
        process_id=process_id,
        result=result
    )
    
    results = search_crud.search_process_data(db, q, filters)
    return results

@router.post("/process-data/filter")
def filter_process_data(
    request: FilterRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Apply complex dynamic filters to process data.
    """
    results = search_crud.apply_dynamic_filters(
        db, 
        ProcessData, 
        request.filters,
        request.sort_by,
        request.sort_order,
        request.limit
    )
    return results

@router.post("/filters/save")
def save_filter(
    request: SaveFilterRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Save a filter configuration for later use.
    """
    saved_filter = SavedFilter(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        filters=request.filters, # Store raw dict/list
        is_shared=request.is_shared
    )
    db.add(saved_filter)
    db.commit()
    db.refresh(saved_filter)
    return saved_filter

@router.get("/filters/my-filters")
def get_my_filters(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all filters saved by the current user.
    """
    return db.query(SavedFilter).filter(
        SavedFilter.user_id == current_user.id
    ).all()

@router.post("/filters/{filter_id}/apply")
def apply_saved_filter(
    filter_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Load and apply a saved filter.
    """
    saved_filter = db.query(SavedFilter).get(filter_id)
    if not saved_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
        
    # Convert stored dict back to FilterExpression objects if needed
    # For now, we assume the stored JSON structure matches what apply_dynamic_filters expects
    # We might need to deserialize properly if strict typing is enforced
    
    # Simple deserialization attempt (assuming stored as list of dicts)
    from app.schemas.search import FilterExpression
    filter_exprs = [FilterExpression(**f) for f in saved_filter.filters]
    
    results = search_crud.apply_dynamic_filters(
        db,
        ProcessData,
        filter_exprs
    )
    return results
