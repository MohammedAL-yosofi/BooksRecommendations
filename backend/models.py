from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Models
class CreateUserRequest(BaseModel):
    user_id: str = Field(..., description="Unique user ID")
    username: str = Field(..., min_length=1, max_length=50, description="Username")

class AddBookToHistoryRequest(BaseModel):
    book_id: int = Field(..., description="Book ID to add to history")

class SearchBooksRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Number of results to return")

# Response Models
class BookInfo(BaseModel):
    book_id: int
    title: str
    category: str
    description_to_display: str
    similarity: Optional[float] = None

class UserInfo(BaseModel):
    id: str
    username: str
    created_at: str

class UserStats(BaseModel):
    user_id: str
    username: str
    created_at: str
    books_read: int
    reading_history: List[int]

class SystemStats(BaseModel):
    total_users: int
    total_reading_entries: int
    total_books: int
    total_categories: int

class RecommendationResponse(BaseModel):
    recommendations: List[BookInfo]
    total_count: int
    user_id: str
    recommendation_type: str

class SearchResponse(BaseModel):
    books: List[BookInfo]
    total_count: int
    query: str

class HistoryResponse(BaseModel):
    books: List[BookInfo]
    total_count: int
    user_id: str

# Error Response Models
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int

class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
