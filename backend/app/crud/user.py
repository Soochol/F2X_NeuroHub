"""
CRUD operations for the User entity.

This module implements Create, Read, Update, Delete operations for user management
in the F2X NeuroHub MES system. Provides standard CRUD functions plus specialized
queries for authentication, role-based filtering, and user activity tracking.

Security:
    - Passwords are hashed using bcrypt (cost factor 12) via passlib
    - Plain text passwords are never stored or logged
    - Password verification uses constant-time comparison to prevent timing attacks
    - All password-related operations occur server-side only

Functions:
    get: Get a single user by ID
    get_multi: Get multiple users with pagination and filtering
    create: Create a new user with hashed password
    update: Update user information (excluding password)
    delete: Delete a user account (soft or hard delete)
    get_by_username: Get user by unique username
    get_by_email: Get user by unique email
    authenticate: Verify credentials and return authenticated user
    is_active: Check if user account is active
    update_last_login: Update last_login_at timestamp for user
    get_by_role: Filter and retrieve users by role with pagination
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from passlib.context import CryptContext

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserInDB


# Password hashing context configuration
# Uses bcrypt algorithm with default cost factor of 12
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Security: Uses passlib's bcrypt implementation with default cost factor (12),
    which is resistant to brute-force attacks.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string (format: $2b$12$...)

    Raises:
        ValueError: If password is empty or None

    Example:
        hashed = get_password_hash("SecurePassword123")
        # Returns: $2b$12$... (60 character bcrypt hash)
    """
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.

    Security: Uses constant-time comparison to prevent timing attacks.
    This function blocks timing side-channel attacks where an attacker
    could measure response time to infer password correctness.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        is_valid = verify_password("SecurePassword123", user.password_hash)
        if is_valid:
            print("Password is correct")
    """
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get(db: Session, user_id: int) -> Optional[User]:
    """
    Get a single user by ID.

    Retrieves a user record from the database by its primary key.
    This is the fastest lookup method for user retrieval.

    Args:
        db: SQLAlchemy database session
        user_id: Primary key ID of the user to retrieve

    Returns:
        User instance if found, None otherwise

    Example:
        user = get(db, user_id=1)
        if user:
            print(f"User: {user.username}")
    """
    return db.query(User).filter(User.id == user_id).first()


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
) -> List[User]:
    """
    Get multiple users with pagination and optional filtering.

    Retrieves a paginated list of users from the database with optional
    filtering by role and active status. Results are ordered by creation
    timestamp (newest first).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100, max: 1000)
        role: Optional filter by UserRole enum (ADMIN, MANAGER, OPERATOR)
        is_active: Optional filter by active status (True/False/None for all)

    Returns:
        List of User instances matching the criteria (may be empty)

    Raises:
        ValueError: If skip or limit values are negative

    Example:
        # Get first 10 active users
        active_users = get_multi(db, skip=0, limit=10, is_active=True)

        # Get all MANAGER role users
        managers = get_multi(db, role=UserRole.MANAGER)

        # Pagination: Get users 20-30
        users_page_3 = get_multi(db, skip=20, limit=10)
    """
    if skip < 0 or limit < 0:
        raise ValueError("skip and limit must be non-negative integers")

    # Enforce reasonable limit to prevent resource exhaustion
    if limit > 1000:
        limit = 1000

    query = db.query(User)

    # Apply optional filters
    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Order by creation date (newest first) and apply pagination
    return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


def create(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user with password hashing.

    Creates a new user record in the database with the provided information.
    The password is automatically hashed using bcrypt before storage.
    Username and email must be unique (enforced by database constraints).

    Security:
        - Password is hashed with bcrypt (cost factor 12) before storage
        - Plain text password is never stored or logged
        - Unique constraints on username and email prevent duplicates

    Args:
        db: SQLAlchemy database session
        user_in: UserCreate schema containing user data and plain text password

    Returns:
        Created User instance with generated ID and timestamps

    Raises:
        IntegrityError: If username or email already exists
        SQLAlchemyError: If database operation fails
        ValueError: If password is invalid or empty

    Example:
        user_data = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="SecurePassword123",
            full_name="John Doe",
            role=UserRole.OPERATOR
        )
        new_user = create(db, user_data)
        db.commit()
        print(f"Created user: {new_user.username} with ID {new_user.id}")
    """
    try:
        # Hash the password before storing
        password_hash = get_password_hash(user_in.password)

        # Create user instance
        db_user = User(
            username=user_in.username.lower(),  # Normalize username
            email=user_in.email.lower() if user_in.email else None,
            password_hash=password_hash,
            full_name=user_in.full_name,
            role=user_in.role,
            department=user_in.department,
            is_active=user_in.is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Add to session and flush to generate ID
        db.add(db_user)
        db.flush()  # Execute INSERT but don't commit

        return db_user

    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def update(db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """
    Update user information (excluding password).

    Updates the specified user record with provided fields. Only fields
    provided in the schema are updated (other fields remain unchanged).
    Password changes are handled separately via a dedicated function.

    Security:
        - Password field is explicitly excluded from updates via UserUpdate schema
        - Allows admin password resets via separate dedicated endpoint
        - Timestamps are automatically updated by database

    Args:
        db: SQLAlchemy database session
        user_id: Primary key ID of user to update
        user_in: UserUpdate schema with fields to update (all optional)

    Returns:
        Updated User instance if found, None if user doesn't exist

    Raises:
        IntegrityError: If username or email conflicts with existing user
        SQLAlchemyError: If database operation fails

    Example:
        user_update = UserUpdate(
            full_name="Jane Doe",
            department="Engineering",
            is_active=False
        )
        updated_user = update(db, user_id=1, user_update)
        if updated_user:
            db.commit()
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    try:
        # Update only provided fields
        update_data = user_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                # Normalize username and email to lowercase
                if field == "username":
                    value = value.lower()
                elif field == "email":
                    value = value.lower()

                setattr(db_user, field, value)

        # Update timestamp
        db_user.updated_at = datetime.now(timezone.utc)

        # Flush changes
        db.flush()

        return db_user

    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def delete(db: Session, user_id: int) -> bool:
    """
    Delete a user account from the database.

    Deletes the specified user record. This is a hard delete operation.
    For soft deletes, use the is_active flag instead.

    Security Considerations:
        - Consider soft deletes for audit compliance
        - Ensure proper authorization checks before calling this function
        - May trigger cascade delete on related records (audit logs, etc.)

    Args:
        db: SQLAlchemy database session
        user_id: Primary key ID of user to delete

    Returns:
        True if user was deleted, False if user not found

    Raises:
        SQLAlchemyError: If database operation fails

    Example:
        # Hard delete
        deleted = delete(db, user_id=5)
        if deleted:
            db.commit()
            print("User deleted")

        # Soft delete (preferred)
        user = get(db, user_id=5)
        if user:
            user.is_active = False
            db.commit()
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.flush()
        return True

    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to delete user: {str(e)}") from e


def get_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get user by unique username.

    Retrieves a user record by their unique username. Username lookup
    is case-insensitive as usernames are normalized to lowercase.

    Args:
        db: SQLAlchemy database session
        username: Username to search for (case-insensitive)

    Returns:
        User instance if found, None otherwise

    Example:
        user = get_by_username(db, username="john_doe")
        if user:
            print(f"Found: {user.full_name}")
    """
    if not username:
        return None

    return db.query(User).filter(
        User.username == username.lower()
    ).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by unique email address.

    Retrieves a user record by their unique email. Email lookup is
    case-insensitive as emails are normalized to lowercase.

    Args:
        db: SQLAlchemy database session
        email: Email address to search for (case-insensitive)

    Returns:
        User instance if found, None otherwise

    Example:
        user = get_by_email(db, email="john@example.com")
        if user:
            print(f"Found user: {user.username}")
    """
    if not email:
        return None

    return db.query(User).filter(
        User.email == email.lower()
    ).first()


def authenticate(
    db: Session, *, username: str, password: str
) -> Optional[User]:
    """
    Authenticate user with username and password.

    Verifies user credentials and returns the authenticated user if valid.
    Uses constant-time password comparison to prevent timing attacks.
    Returns None for both invalid username and invalid password (consistent
    for security).

    Security:
        - Uses constant-time password comparison (prevents timing attacks)
        - Returns None for both invalid username and password (prevents user enumeration)
        - Last login timestamp is NOT updated here (call update_last_login separately)
        - Password verification uses passlib's bcrypt implementation

    Args:
        db: SQLAlchemy database session
        username: Username to authenticate (required, keyword-only)
        password: Plain text password to verify (required, keyword-only)

    Returns:
        Authenticated User instance if credentials valid, None otherwise

    Example:
        user = authenticate(db, username="john_doe", password="SecurePassword123")
        if user and user.is_active:
            # Generate JWT token or session
            update_last_login(db, user.id)
            print("Login successful")
        else:
            print("Invalid credentials or inactive account")
    """
    if not username or not password:
        return None

    # Get user by username (case-insensitive)
    db_user = get_by_username(db, username=username)
    if not db_user:
        return None

    # Verify password using constant-time comparison
    if not verify_password(password, db_user.password_hash):
        return None

    return db_user


def is_active(user: Optional[User]) -> bool:
    """
    Check if user account is active.

    Verifies that the user exists and has an active status.
    Use this to prevent disabled accounts from accessing the system.

    Args:
        user: User instance to check (may be None)

    Returns:
        True if user exists and is_active flag is True, False otherwise

    Example:
        user = authenticate(db, username="john_doe", password="SecurePassword123")
        if is_active(user):
            print("User account is active")
        else:
            print("User account is disabled or not found")
    """
    if user is None:
        return False
    return user.is_active


def update_last_login(db: Session, user_id: int) -> Optional[User]:
    """
    Update user's last login timestamp to current time.

    Records when the user last successfully logged in. Call this after
    successful authentication and session creation.

    Args:
        db: SQLAlchemy database session
        user_id: Primary key ID of user to update

    Returns:
        Updated User instance if found, None otherwise

    Raises:
        SQLAlchemyError: If database operation fails

    Example:
        user = authenticate(db, username="john_doe", password="password123")
        if user:
            # Generate JWT token...
            update_last_login(db, user.id)
            db.commit()
            print("Login recorded")
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        db_user.last_login_at = datetime.now(timezone.utc)
        db.flush()

        return db_user

    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to update last login: {str(e)}") from e


def get_by_role(
    db: Session,
    role: UserRole,
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """
    Get users filtered by role with pagination.

    Retrieves all users with the specified role, useful for admin operations
    like sending notifications to all managers or getting list of operators.
    Results are ordered by creation timestamp (newest first).

    Args:
        db: SQLAlchemy database session
        role: UserRole enum to filter by (ADMIN, MANAGER, OPERATOR)
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100, max: 1000)

    Returns:
        List of User instances with specified role (may be empty)

    Raises:
        ValueError: If skip or limit values are negative

    Example:
        # Get all active managers
        managers = get_by_role(db, role=UserRole.MANAGER, limit=1000)

        # Get first 10 operators
        operators = get_by_role(db, role=UserRole.OPERATOR, skip=0, limit=10)

        # Paginate through admins (10 per page)
        page = 1
        page_size = 10
        admins = get_by_role(
            db,
            role=UserRole.ADMIN,
            skip=(page - 1) * page_size,
            limit=page_size
        )
    """
    if skip < 0 or limit < 0:
        raise ValueError("skip and limit must be non-negative integers")

    if limit > 1000:
        limit = 1000

    return (
        db.query(User)
        .filter(User.role == role)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
