from typing import List, Optional, Any, Union, Dict
from pydantic import BaseModel
from datetime import datetime

class DateRange(BaseModel):
    start: datetime
    end: datetime

class SearchFilters(BaseModel):
    process_id: Optional[int] = None
    result: Optional[str] = None
    date_range: Optional[DateRange] = None

class FilterExpression(BaseModel):
    field: str
    operator: str  # eq, gt, lt, contains, in, etc.
    value: Any

class FilterRequest(BaseModel):
    filters: List[FilterExpression]
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    limit: int = 100

class SaveFilterRequest(BaseModel):
    name: str
    description: Optional[str] = None
    filters: List[Dict[str, Any]] # Serialized FilterExpressions
    is_shared: bool = False

# Helper for type checking
from typing import Dict
