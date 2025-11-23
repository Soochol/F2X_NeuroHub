from typing import List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc, asc
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.models.process_data import ProcessData
from app.schemas.search import SearchFilters, FilterExpression

def search_process_data(
    db: Session,
    query: str,
    filters: Optional[SearchFilters] = None
):
    """
    Full-text search across process data notes/metadata.
    Uses PostgreSQL to_tsvector/plainto_tsquery.
    """
    # Base query
    search_query = db.query(ProcessData)
    
    # Apply Full-Text Search if query is provided
    if query and len(query.strip()) > 0:
        # Note: This assumes 'notes' or similar text field exists and is indexed.
        # If notes is JSONB or not indexed, this might be slow or need adjustment.
        # For now, we'll use a simple ILIKE for compatibility if TS vector isn't set up,
        # or try the TS syntax if we assume Postgres.
        
        # Using simple ILIKE for broader compatibility in this phase without migration
        # search_query = search_query.filter(ProcessData.notes.ilike(f"%{query}%"))
        
        # Proper Postgres TS Search (commented out until migration adds index)
        search_query = search_query.filter(
            func.to_tsvector('english', func.coalesce(ProcessData.notes, ''))
            .match(func.plainto_tsquery('english', query))
        )

    # Apply additional static filters
    if filters:
        if filters.process_id:
            search_query = search_query.filter(
                ProcessData.process_id == filters.process_id
            )
        if filters.result:
            search_query = search_query.filter(
                ProcessData.result == filters.result
            )
        if filters.date_range:
            search_query = search_query.filter(
                ProcessData.created_at.between(
                    filters.date_range.start,
                    filters.date_range.end
                )
            )

    return search_query.limit(100).all()

def apply_dynamic_filters(
    db: Session, 
    model: Type[DeclarativeMeta], 
    filters: List[FilterExpression],
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    limit: int = 100
):
    """
    Build query from dynamic filters list.
    """
    query = db.query(model)

    for filter_expr in filters:
        if not hasattr(model, filter_expr.field):
            continue
            
        column = getattr(model, filter_expr.field)
        val = filter_expr.value
        op = filter_expr.operator
        
        if op == "eq":
            query = query.filter(column == val)
        elif op == "neq":
            query = query.filter(column != val)
        elif op == "gt":
            query = query.filter(column > val)
        elif op == "gte":
            query = query.filter(column >= val)
        elif op == "lt":
            query = query.filter(column < val)
        elif op == "lte":
            query = query.filter(column <= val)
        elif op == "contains":
            query = query.filter(column.contains(val))
        elif op == "icontains":
            query = query.filter(column.ilike(f"%{val}%"))
        elif op == "in":
            query = query.filter(column.in_(val))
        elif op == "startswith":
            query = query.filter(column.startswith(val))
        elif op == "endswith":
            query = query.filter(column.endswith(val))

    # Sorting
    if sort_by and hasattr(model, sort_by):
        sort_col = getattr(model, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(asc(sort_col))
            
    return query.limit(limit).all()
