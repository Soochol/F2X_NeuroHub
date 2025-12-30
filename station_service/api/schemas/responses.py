"""
Common API response schemas for Station Service.

This module defines the standard response wrappers used across all API endpoints.
"""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail schema for error responses.

    Attributes:
        code: Error code identifier (e.g., 'BATCH_NOT_FOUND')
        message: Human-readable error message
    """
    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper.

    All successful API responses are wrapped in this schema to provide
    a consistent interface for clients.

    Attributes:
        success: Whether the request was successful
        data: The response payload
    """
    success: bool = Field(default=True, description="Whether the request was successful")
    data: T = Field(..., description="Response payload")


class ErrorResponse(BaseModel):
    """Standard error response wrapper.

    All error responses are wrapped in this schema to provide
    a consistent interface for clients.

    Attributes:
        success: Always False for error responses
        error: Error detail containing code and message
    """
    success: bool = Field(default=False, description="Always False for error responses")
    error: ErrorDetail = Field(..., description="Error details")


class PaginationMeta(BaseModel):
    """Pagination metadata for paginated responses.

    Attributes:
        total: Total number of items
        limit: Maximum items per page
        offset: Current offset
    """
    total: int = Field(..., description="Total number of items", ge=0)
    limit: int = Field(..., description="Maximum items per page", ge=1)
    offset: int = Field(..., description="Current offset", ge=0)


class PaginatedData(BaseModel, Generic[T]):
    """Paginated data container.

    Attributes:
        total: Total number of items available
        items: List of items for the current page
    """
    total: int = Field(..., description="Total number of items available", ge=0)
    items: List[T] = Field(default_factory=list, description="List of items")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper.

    Used for endpoints that return lists of items with pagination support.

    Attributes:
        success: Whether the request was successful
        data: Paginated data containing total count and items
    """
    success: bool = Field(default=True, description="Whether the request was successful")
    data: PaginatedData[T] = Field(..., description="Paginated data")
