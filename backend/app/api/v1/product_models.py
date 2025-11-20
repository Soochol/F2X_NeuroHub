"""FastAPI router for ProductModel entity endpoints.

This module provides RESTful API endpoints for managing product model master data
in the F2X NeuroHub MES system. It implements standard CRUD operations plus
additional query endpoints for filtering and searching product models.

Provides:
    - GET /: List all product models with pagination
    - GET /{id}: Get product model by primary key
    - GET /code/{model_code}: Get product model by unique model code
    - GET /active: List active product models only
    - GET /category/{category}: Filter product models by category
    - POST /: Create new product model
    - PUT /{id}: Update existing product model
    - DELETE /{id}: Delete product model

All endpoints include:
    - Comprehensive docstrings with operation descriptions
    - Pydantic schema validation for request/response
    - OpenAPI documentation metadata
    - Proper HTTP status codes
    - Error handling with descriptive HTTPException responses
    - Dependency injection for database sessions
"""

from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.crud import product_model as crud
from app.schemas.product_model import (
    ProductModelCreate,
    ProductModelUpdate,
    ProductModelInDB,
)
from app.core.exceptions import (
    ProductModelNotFoundException,
    DuplicateResourceException,
)


router = APIRouter(
    prefix="/product-models",
    tags=["Product Models"],
    responses={
        404: {"description": "Product model not found"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict (e.g., duplicate model code)"},
    },
)


@router.get(
    "/",
    response_model=List[ProductModelInDB],
    summary="List all product models",
    description="Retrieve a paginated list of all product models ordered by creation date (newest first)",
)
def list_product_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProductModelInDB]:
    """List all product models with pagination.

    Retrieves a paginated list of all product models from the database, ordered
    by creation date in descending order (newest first). Supports configurable
    offset and limit for pagination control.

    Args:
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[ProductModelInDB]: List of product model records with database fields.
            Empty list if no records match criteria.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get first 10 product models:
        >>> GET /api/v1/product-models/?skip=0&limit=10

        Get next page (items 10-20):
        >>> GET /api/v1/product-models/?skip=10&limit=10

        Get all records (large limit):
        >>> GET /api/v1/product-models/?skip=0&limit=10000

    OpenAPI Parameters:
        skip: Query parameter, non-negative integer
        limit: Query parameter, positive integer (1-10000)
    """
    return crud.get_multi(db, skip=skip, limit=limit)


@router.get(
    "/active",
    response_model=List[ProductModelInDB],
    summary="List active product models",
    description="Retrieve paginated list of product models with ACTIVE status only",
)
def get_active_product_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProductModelInDB]:
    """Get active product models with pagination.

    Retrieves only product models with ACTIVE status, indicating they are currently
    available for production operations. Supports pagination for managing large
    result sets.

    Args:
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[ProductModelInDB]: List of active product model records.
            Empty list if no active records exist.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get all active product models:
        >>> GET /api/v1/product-models/active

        Paginate through active products (10 per page):
        >>> GET /api/v1/product-models/active?skip=0&limit=10
        >>> GET /api/v1/product-models/active?skip=10&limit=10

    Response Example (200 OK):
        [
            {
                "id": 1,
                "model_code": "NH-F2X-001",
                "model_name": "NeuroHub F2X Standard",
                "status": "ACTIVE",
                ...
            },
            {
                "id": 2,
                "model_code": "NH-F2X-002",
                "model_name": "NeuroHub F2X Premium",
                "status": "ACTIVE",
                ...
            }
        ]
    """
    return crud.get_active(db, skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=ProductModelInDB,
    summary="Get product model by ID",
    description="Retrieve a specific product model using its primary key identifier",
    responses={404: {"description": "Product model not found"}},
)
def get_product_model(
    id: int = Path(..., gt=0, description="Primary key identifier of the product model"),
    db: Session = Depends(deps.get_db),
) -> ProductModelInDB:
    """Get product model by primary key ID.

    Retrieves a single product model record from the database using its unique
    primary key identifier.

    Args:
        id: Primary key identifier of the product model to retrieve.
            Must be a positive integer.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        ProductModelInDB: Product model record with all database fields.

    Raises:
        HTTPException: 404 Not Found if product model does not exist with given ID.

    Examples:
        Get product model with ID 1:
        >>> GET /api/v1/product-models/1

        Get product model with ID 42:
        >>> GET /api/v1/product-models/42

    Response Example (200 OK):
        {
            "id": 1,
            "model_code": "NH-F2X-001",
            "model_name": "NeuroHub F2X Standard",
            "category": "Standard",
            "production_cycle_days": 5,
            "specifications": {
                "dimensions": {"width_mm": 100, "height_mm": 50},
                "weight_grams": 250
            },
            "status": "ACTIVE",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00"
        }
    """
    obj = crud.get(db, id=id)
    if not obj:
        raise ProductModelNotFoundException(model_id=id)
    return obj


@router.get(
    "/code/{model_code}",
    response_model=ProductModelInDB,
    summary="Get product model by model code",
    description="Retrieve a product model using its unique model code identifier",
    responses={404: {"description": "Product model not found"}},
)
def get_product_model_by_code(
    model_code: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProductModelInDB:
    """Get product model by unique model code.

    Retrieves a product model using its globally unique code identifier
    (e.g., "NH-F2X-001"). Model codes are case-sensitive and provide an
    alternative way to retrieve product models.

    Args:
        model_code: Unique model code identifier (e.g., "NH-F2X-001").
            Case-sensitive, must be 1-50 characters.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        ProductModelInDB: Product model record with all database fields.

    Raises:
        HTTPException: 404 Not Found if product model does not exist with given code.

    Examples:
        Get product model by code:
        >>> GET /api/v1/product-models/code/NH-F2X-001

        Get product model with different code:
        >>> GET /api/v1/product-models/code/NH-PRO-002

    Response Example (200 OK):
        {
            "id": 1,
            "model_code": "NH-F2X-001",
            "model_name": "NeuroHub F2X Standard",
            ...
        }
    """
    obj = crud.get_by_code(db, model_code=model_code)
    if not obj:
        raise ProductModelNotFoundException(model_id=f"code='{model_code}'")
    return obj


@router.get(
    "/category/{category}",
    response_model=List[ProductModelInDB],
    summary="List product models by category",
    description="Retrieve paginated list of product models filtered by category",
)
def get_product_models_by_category(
    category: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProductModelInDB]:
    """Get product models filtered by category with pagination.

    Retrieves product models belonging to a specific category or family classification.
    Category filtering uses exact match and is case-sensitive.

    Args:
        category: Product category to filter by (e.g., "Standard", "Premium", "Enterprise").
            Case-sensitive, exact match required.
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[ProductModelInDB]: List of product models in specified category.
            Empty list if no models exist in category.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get all Standard category products:
        >>> GET /api/v1/product-models/category/Standard

        Get Premium products with pagination:
        >>> GET /api/v1/product-models/category/Premium?skip=0&limit=20

        Get Enterprise products:
        >>> GET /api/v1/product-models/category/Enterprise

    Response Example (200 OK):
        [
            {
                "id": 1,
                "model_code": "NH-F2X-001",
                "model_name": "NeuroHub F2X Standard",
                "category": "Standard",
                "status": "ACTIVE",
                ...
            }
        ]
    """
    return crud.get_by_category(db, category=category, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=ProductModelInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new product model",
    description="Create a new product model with provided specifications",
    responses={409: {"description": "Product model code already exists"}},
)
def create_product_model(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: ProductModelCreate,
) -> ProductModelInDB:
    """Create new product model.

    Creates a new ProductModel record with validated data from the request body.
    The model_code must be globally unique; duplicate codes will result in a
    409 Conflict error. Database-generated fields (id, created_at, updated_at)
    are automatically populated.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        obj_in: ProductModelCreate schema with validated product data.
            Required: model_code, model_name.
            Optional: category, production_cycle_days, specifications, status.

    Returns:
        ProductModelInDB: Newly created product model record with all fields
            including database-generated values.

    Raises:
        HTTPException: 409 Conflict if model_code already exists.
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Create minimal product model:
        >>> POST /api/v1/product-models/
        >>> {
        ...     "model_code": "NH-F2X-001",
        ...     "model_name": "NeuroHub F2X Standard"
        ... }

        Create full product model with specifications:
        >>> POST /api/v1/product-models/
        >>> {
        ...     "model_code": "NH-F2X-002",
        ...     "model_name": "NeuroHub F2X Premium",
        ...     "category": "Premium",
        ...     "production_cycle_days": 7,
        ...     "specifications": {
        ...         "dimensions": {"width_mm": 120, "height_mm": 60},
        ...         "weight_grams": 350,
        ...         "materials": ["aluminum", "composite"]
        ...     },
        ...     "status": "ACTIVE"
        ... }

    Response Example (201 Created):
        {
            "id": 1,
            "model_code": "NH-F2X-001",
            "model_name": "NeuroHub F2X Standard",
            "category": null,
            "production_cycle_days": null,
            "specifications": {},
            "status": "ACTIVE",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00"
        }
    """
    try:
        return crud.create(db, obj_in=obj_in)
    except Exception as e:
        # Handle database constraint violations
        if "unique constraint" in str(e).lower():
            raise DuplicateResourceException(
                resource_type="Product model",
                identifier=f"code='{obj_in.model_code}'"
            )
        # Re-raise other exceptions
        raise


@router.put(
    "/{id}",
    response_model=ProductModelInDB,
    summary="Update product model",
    description="Update existing product model with new values",
    responses={
        404: {"description": "Product model not found"},
        409: {"description": "Conflict (e.g., duplicate model code)"},
    },
)
def update_product_model(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0, description="Primary key identifier of product model to update"),
    obj_in: ProductModelUpdate,
) -> ProductModelInDB:
    """Update existing product model.

    Updates specific fields in an existing ProductModel record. All fields are
    optional, supporting partial updates. Only provided fields are modified;
    unspecified fields retain their current values.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        id: Primary key identifier of product model to update.
        obj_in: ProductModelUpdate schema with field updates.
            All fields are optional. Only provided fields are updated.

    Returns:
        ProductModelInDB: Updated product model record with all fields.

    Raises:
        HTTPException: 404 Not Found if product model does not exist.
        HTTPException: 409 Conflict if model_code update violates unique constraint.
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Update product name only:
        >>> PUT /api/v1/product-models/1
        >>> {
        ...     "model_name": "Updated Name"
        ... }

        Update status to inactive:
        >>> PUT /api/v1/product-models/1
        >>> {
        ...     "status": "INACTIVE"
        ... }

        Update multiple fields:
        >>> PUT /api/v1/product-models/1
        >>> {
        ...     "model_name": "Updated Name",
        ...     "category": "Premium",
        ...     "status": "INACTIVE"
        ... }

    Response Example (200 OK):
        {
            "id": 1,
            "model_code": "NH-F2X-001",
            "model_name": "Updated Name",
            "category": "Premium",
            "status": "INACTIVE",
            ...
        }
    """
    obj = crud.get(db, id=id)
    if not obj:
        raise ProductModelNotFoundException(model_id=id)

    try:
        return crud.update(db, db_obj=obj, obj_in=obj_in)
    except Exception as e:
        # Handle database constraint violations
        if "unique constraint" in str(e).lower():
            raise DuplicateResourceException(
                resource_type="Product model",
                identifier=f"code='{obj_in.model_code}'"
            )
        # Re-raise other exceptions
        raise


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product model",
    description="Delete an existing product model",
    responses={404: {"description": "Product model not found"}},
)
def delete_product_model(
    id: int = Path(..., gt=0, description="Primary key identifier of product model to delete"),
    db: Session = Depends(deps.get_db),
):
    """Delete product model by ID.

    Removes a ProductModel record from the database. Note: If the product model
    has dependent records (via foreign keys), deletion may fail with a constraint
    violation error.

    Args:
        id: Primary key identifier of product model to delete.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 404 Not Found if product model does not exist.
        HTTPException: 409 Conflict if deletion violates foreign key constraint.
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Delete product model with ID 1:
        >>> DELETE /api/v1/product-models/1

        Delete product model with ID 42:
        >>> DELETE /api/v1/product-models/42

    Response: 204 No Content
    """
    obj = crud.delete(db, id=id)
    if not obj:
        raise ProductModelNotFoundException(model_id=id)
