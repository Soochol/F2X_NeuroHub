"""CRUD operations for ProductModel entity.

This module provides comprehensive CRUD (Create, Read, Update, Delete) operations
for managing product model master data in the F2X NeuroHub MES system.

Provides:
    - get: Retrieve product model by primary key
    - get_multi: Retrieve multiple product models with pagination
    - get_by_code: Retrieve product model by unique model code
    - get_active: Retrieve active product models with pagination
    - get_by_category: Retrieve product models filtered by category
    - create: Create new product model record
    - update: Update existing product model record
    - delete: Delete product model record

All operations include:
    - Type hints for full type safety
    - Comprehensive docstrings with examples
    - Error handling for edge cases
    - SQLAlchemy ORM pattern compliance
    - Pydantic schema validation
"""

from typing import Optional, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models import ProductModel
from app.schemas.product_model import (
    ProductModelCreate,
    ProductModelUpdate,
    ProductStatusEnum,
)


def get(db: Session, id: int) -> Optional[ProductModel]:
    """Get product model by primary key ID.

    Retrieves a single product model record from the database using its
    primary key identifier.

    Args:
        db: SQLAlchemy database session for executing queries.
        id: Primary key identifier of the product model to retrieve.

    Returns:
        ProductModel instance if found, None if not found.

    Raises:
        Exception: May raise SQLAlchemy exceptions on database errors.

    Examples:
        >>> product = get(db, 1)
        >>> if product:
        ...     print(f"Found: {product.model_code}")
        ... else:
        ...     print("Product not found")

        >>> product = get(db, 99999)
        >>> product is None
        True
    """
    return db.query(ProductModel).filter(ProductModel.id == id).first()


def get_multi(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[ProductModel]:
    """Get multiple product models with pagination support.

    Retrieves a paginated list of all product models from the database,
    ordered by creation date in descending order (newest first).

    Args:
        db: SQLAlchemy database session for executing queries.
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0 (start from beginning).
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive integer.

    Returns:
        List of ProductModel instances. Empty list if no records match criteria.

    Raises:
        Exception: May raise SQLAlchemy exceptions on database errors.

    Examples:
        >>> products = get_multi(db)
        >>> print(f"Retrieved {len(products)} products")

        >>> first_page = get_multi(db, skip=0, limit=10)
        >>> second_page = get_multi(db, skip=10, limit=10)

        >>> all_products = get_multi(db, limit=10000)
        >>> for product in all_products:
        ...     print(product.model_code)
    """
    return (
        db.query(ProductModel)
        .order_by(ProductModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_code(db: Session, model_code: str) -> Optional[ProductModel]:
    """Get product model by unique model code.

    Retrieves a product model using its unique identifier code (e.g., "NH-F2X-001").
    Model codes are case-sensitive and globally unique in the system.

    Args:
        db: SQLAlchemy database session for executing queries.
        model_code: Unique model code identifier (e.g., "NH-F2X-001").

    Returns:
        ProductModel instance if found, None if not found.

    Raises:
        Exception: May raise SQLAlchemy exceptions on database errors.

    Examples:
        >>> product = get_by_code(db, "NH-F2X-001")
        >>> if product:
        ...     print(product.model_name)

        >>> product = get_by_code(db, "NONEXISTENT")
        >>> product is None
        True

        >>> product = get_by_code(db, "NH-F2X-002")
        >>> print(f"Category: {product.category}")
    """
    return (
        db.query(ProductModel)
        .filter(ProductModel.model_code == model_code)
        .first()
    )


def get_active(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[ProductModel]:
    """Get active product models with pagination.

    Retrieves only product models with ACTIVE status. Useful for listing
    products available for current production operations.

    Args:
        db: SQLAlchemy database session for executing queries.
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0 (start from beginning).
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive integer.

    Returns:
        List of active ProductModel instances. Empty list if no active records found.

    Raises:
        Exception: May raise SQLAlchemy exceptions on database errors.

    Examples:
        >>> active_products = get_active(db)
        >>> print(f"Found {len(active_products)} active products")

        >>> # Paginate through active products
        >>> for page_num in range(5):
        ...     products = get_active(db, skip=page_num * 20, limit=20)
        ...     if not products:
        ...         break
        ...     for product in products:
        ...         print(product.model_code)

        >>> # Check if specific product is active
        >>> active = get_active(db, limit=10000)
        >>> model_codes = [p.model_code for p in active]
        >>> "NH-F2X-001" in model_codes
    """
    return (
        db.query(ProductModel)
        .filter(ProductModel.status == ProductStatusEnum.ACTIVE)
        .order_by(ProductModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_category(
    db: Session,
    category: str,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[ProductModel]:
    """Get product models filtered by category with pagination.

    Retrieves product models belonging to a specific category or family.
    Supports pagination for large category result sets.

    Args:
        db: SQLAlchemy database session for executing queries.
        category: Product category to filter by (e.g., "Standard", "Premium").
            Filter is case-sensitive and exact match.
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0 (start from beginning).
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive integer.

    Returns:
        List of ProductModel instances matching category. Empty list if no matches.

    Raises:
        Exception: May raise SQLAlchemy exceptions on database errors.

    Examples:
        >>> premium_products = get_by_category(db, "Premium")
        >>> for product in premium_products:
        ...     print(f"{product.model_code}: {product.model_name}")

        >>> # Paginate through category results
        >>> all_category_products = get_by_category(db, "Standard", limit=10000)
        >>> print(f"Total Standard products: {len(all_category_products)}")

        >>> # Check count of products in category
        >>> category_products = get_by_category(db, "Enterprise", limit=100)
        >>> if len(category_products) == 0:
        ...     print("No Enterprise products found")
    """
    return (
        db.query(ProductModel)
        .filter(ProductModel.category == category)
        .order_by(ProductModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, *, obj_in: ProductModelCreate) -> ProductModel:
    """Create new product model record.

    Creates a new ProductModel record in the database with validated data from
    the Pydantic schema. All input data is validated before insertion.

    Args:
        db: SQLAlchemy database session for executing queries.
        obj_in: ProductModelCreate Pydantic schema with validated product data.
            Must include: model_code, model_name. Optional fields have defaults.

    Returns:
        ProductModel instance of newly created record with database-generated values
        (id, created_at, updated_at) populated.

    Raises:
        sqlalchemy.exc.IntegrityError: If model_code already exists (unique constraint).
        sqlalchemy.exc.IntegrityError: If status value is invalid (check constraint).
        Exception: May raise other SQLAlchemy exceptions on database errors.

    Examples:
        >>> create_data = ProductModelCreate(
        ...     model_code="NH-F2X-001",
        ...     model_name="NeuroHub F2X Standard",
        ...     category="Standard",
        ...     production_cycle_days=5,
        ...     specifications={"dimensions": {"width_mm": 100}}
        ... )
        >>> product = create(db, obj_in=create_data)
        >>> print(f"Created product with ID: {product.id}")

        >>> # Minimal creation with required fields only
        >>> minimal_data = ProductModelCreate(
        ...     model_code="NH-TEST-001",
        ...     model_name="Test Product"
        ... )
        >>> product = create(db, obj_in=minimal_data)
        >>> print(product.status)  # Will be "ACTIVE" by default
        ACTIVE
    """
    db_obj = ProductModel(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session,
    *,
    db_obj: ProductModel,
    obj_in: ProductModelUpdate,
) -> ProductModel:
    """Update existing product model record.

    Updates specific fields in an existing ProductModel record. Supports partial
    updates where only provided fields are modified. Uses Pydantic's
    `exclude_unset=True` to preserve unspecified fields.

    Args:
        db: SQLAlchemy database session for executing queries.
        db_obj: Existing ProductModel instance to update (must be attached to session).
        obj_in: ProductModelUpdate Pydantic schema with updated values.
            All fields are optional. Only provided fields will be updated.

    Returns:
        ProductModel instance of updated record with changes committed to database.
        The updated_at timestamp is automatically updated by database trigger.

    Raises:
        sqlalchemy.exc.IntegrityError: If model_code update violates unique constraint.
        sqlalchemy.exc.IntegrityError: If status update is invalid (check constraint).
        Exception: May raise other SQLAlchemy exceptions on database errors.

    Examples:
        >>> product = get(db, 1)
        >>> update_data = ProductModelUpdate(
        ...     model_name="Updated Name",
        ...     status=ProductStatusEnum.INACTIVE
        ... )
        >>> updated = update(db, db_obj=product, obj_in=update_data)
        >>> print(updated.model_name)
        Updated Name

        >>> # Partial update - only change category
        >>> product = get(db, 1)
        >>> partial_update = ProductModelUpdate(category="Premium")
        >>> updated = update(db, db_obj=product, obj_in=partial_update)
        >>> # model_name and other fields remain unchanged

        >>> # Update specifications (JSON field)
        >>> product = get(db, 1)
        >>> spec_update = ProductModelUpdate(
        ...     specifications={"new_field": "new_value"}
        ... )
        >>> updated = update(db, db_obj=product, obj_in=spec_update)
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, id: int) -> Optional[ProductModel]:
    """Delete product model record by ID.

    Removes a ProductModel record from the database. Returns the deleted
    record instance before deletion.

    Args:
        db: SQLAlchemy database session for executing queries.
        id: Primary key identifier of the product model to delete.

    Returns:
        ProductModel instance of deleted record, or None if record not found.

    Raises:
        Exception: May raise SQLAlchemy exceptions on database errors.
        sqlalchemy.exc.IntegrityError: May raise if foreign key constraints exist
            and dependent records reference this product model.

    Examples:
        >>> product = delete(db, id=1)
        >>> if product:
        ...     print(f"Deleted product: {product.model_code}")
        ... else:
        ...     print("Product not found")

        >>> # Delete non-existent product
        >>> deleted = delete(db, id=99999)
        >>> deleted is None
        True

        >>> # Verify deletion
        >>> product = delete(db, id=1)
        >>> retrieved = get(db, 1)
        >>> retrieved is None
        True
    """
    obj = db.query(ProductModel).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
