from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn

# Import our modules
from data_loader import data_loader
from user_manager import user_manager
from recommendation_engine import recommendation_engine
from models import *

# Create FastAPI app
app = FastAPI(
    title="BookWise Recommendation API",
    description="A book recommendation system with personalized suggestions",
    version="1.0.0",
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global startup event
@app.on_event("startup")
async def startup_event():
    """Load all data when the server starts."""
    print("🚀 Starting BookWise Recommendation API...")

    # Load book data
    success = data_loader.load_all_data()
    if not success:
        print("❌ Failed to load book data!")
        raise Exception("Failed to load book data")

    print("✅ BookWise API is ready!")


# Health check endpoint
@app.get("/", response_model=Dict)
async def root():
    """Health check endpoint."""
    stats = data_loader.get_stats()
    system_stats = user_manager.get_system_stats()

    return {
        "message": "BookWise Recommendation API is running!",
        "status": "healthy",
        "data_stats": stats,
        "user_stats": system_stats,
    }


# User Management Endpoints
@app.post("/users", response_model=UserInfo)
async def create_user(request: CreateUserRequest):
    """Create a new user."""
    try:
        user_data = user_manager.create_user(request.user_id, request.username)
        return UserInfo(**user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@app.get("/users/{user_id}", response_model=UserInfo)
async def get_user(user_id: str):
    """Get user information."""
    user_data = user_manager.get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return UserInfo(**user_data)


@app.get("/users/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: str):
    """Get user statistics."""
    stats = user_manager.get_user_stats(user_id)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")

    return UserStats(**stats)


# User History Endpoints
@app.post("/users/{user_id}/read", response_model=SuccessResponse)
async def add_book_to_history(user_id: str, request: AddBookToHistoryRequest):
    """Add a book to user's reading history."""
    # Check if book exists
    book_info = data_loader.get_book_by_id(request.book_id)
    if not book_info:
        raise HTTPException(status_code=404, detail="Book not found")

    # Add to history
    success = user_manager.add_book_to_history(user_id, request.book_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add book to history")

    return SuccessResponse(
        success=True,
        message=f"Book '{book_info['title']}' added to reading history",
        data={"book_id": request.book_id, "user_id": user_id},
    )


@app.get("/users/{user_id}/history", response_model=HistoryResponse)
async def get_user_history(user_id: str):
    """Get user's reading history with book details."""
    # Check if user exists
    user_data = user_manager.get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Get history
    history_book_ids = user_manager.get_user_history(user_id)

    # Get book details
    books = []
    for book_id in history_book_ids:
        book_info = data_loader.get_book_by_id(book_id)
        if book_info:
            books.append(BookInfo(**book_info))

    return HistoryResponse(books=books, total_count=len(books), user_id=user_id)


@app.delete("/users/{user_id}/history/{book_id}", response_model=SuccessResponse)
async def remove_book_from_history(user_id: str, book_id: int):
    """Remove a book from user's reading history."""
    success = user_manager.remove_book_from_history(user_id, book_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to remove book from history"
        )

    return SuccessResponse(
        success=True,
        message="Book removed from reading history",
        data={"book_id": book_id, "user_id": user_id},
    )


# User Favorites Endpoints
@app.post("/users/{user_id}/favorites", response_model=SuccessResponse)
async def add_book_to_favorites(user_id: str, request: AddBookToHistoryRequest):
    """Add a book to user's favorites."""
    # Check if book exists
    book_info = data_loader.get_book_by_id(request.book_id)
    if not book_info:
        raise HTTPException(status_code=404, detail="Book not found")

    # Add to favorites
    success = user_manager.add_book_to_favorites(user_id, request.book_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add book to favorites")

    return SuccessResponse(
        success=True,
        message=f"Book '{book_info['title']}' added to favorites",
        data={"book_id": request.book_id, "user_id": user_id},
    )


@app.delete("/users/{user_id}/favorites/{book_id}", response_model=SuccessResponse)
async def remove_book_from_favorites(user_id: str, book_id: int):
    """Remove a book from user's favorites."""
    success = user_manager.remove_book_from_favorites(user_id, book_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to remove book from favorites"
        )

    return SuccessResponse(
        success=True,
        message="Book removed from favorites",
        data={"book_id": book_id, "user_id": user_id},
    )


@app.get("/users/{user_id}/favorites")
async def get_user_favorites(user_id: str):
    """Get user's favorite books with details."""
    # Check if user exists
    user_data = user_manager.get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # ? get favorites
    favorite_book_ids = user_manager.get_user_favorites(user_id)

    # ? get book details
    books = []
    for book_id in favorite_book_ids:
        book_info = data_loader.get_book_by_id(book_id)
        if book_info:
            books.append(BookInfo(**book_info))

    return {"books": books, "total_count": len(books), "user_id": user_id}



@app.get("/books/search", response_model=SearchResponse)
async def search_books(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="num of results"),
):
    
   # """Search for books by title or category"""
    if category:
        # Search within specific category
        books = data_loader.get_books_by_category(category, limit)
    else:
        # General search
        books = data_loader.search_books(query, limit)

    book_infos = [BookInfo(**book) for book in books]

    return SearchResponse(books=book_infos, total_count=len(book_infos), query=query)


@app.get("/books/{book_id}", response_model=BookInfo)
async def get_book(book_id: int):
    """Get book details by ID."""
    book_info = data_loader.get_book_by_id(book_id)
    if not book_info:
        raise HTTPException(status_code=404, detail="Book not found")

    return BookInfo(**book_info)


@app.get("/books/categories", response_model=List[str])
async def get_categories():
    """Get all available book categories."""
    return data_loader.get_all_categories()


# Recommendation 
@app.get("/books/{book_id}/recommendations", response_model=RecommendationResponse)
async def get_item_recommendations(
    book_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
):
    """Get item-to-item recommendations for a book."""
    # Check if book exists
    book_info = data_loader.get_book_by_id(book_id)
    if not book_info:
        raise HTTPException(status_code=404, detail="Book not found")

    # ? get recommendations
    recommendations = recommendation_engine.get_item_to_item_recommendations(
        book_id, limit
    )
    book_infos = [BookInfo(**book) for book in recommendations]

    return RecommendationResponse(
        recommendations=book_infos,
        total_count=len(book_infos),
        user_id="",  # Not applicable for item-to-item
        recommendation_type="item_to_item",
    )


@app.get("/users/{user_id}/recommendations", response_model=RecommendationResponse)
async def get_user_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    method: str = Query(
        "hybrid",
        description="Recommendation method: user_based, category_based, or hybrid",
    ),
):
    """Get personalized recommendations for a user."""
    # ?check if user exists
    user_data = user_manager.get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # get recommendations based on method type
    if method == "user_based":
        recommendations = recommendation_engine.get_user_based_recommendations(
            user_id, limit
        )
    elif method == "category_based":
        recommendations = recommendation_engine.get_category_based_recommendations(
            user_id, limit
        )
    else: 
        recommendations = recommendation_engine.get_hybrid_recommendations(
            user_id, limit
        )# d

    book_infos = [BookInfo(**book) for book in recommendations]

    return RecommendationResponse(
        recommendations=book_infos,
        total_count=len(book_infos),
        user_id=user_id,
        recommendation_type=method,
    )


@app.get("/recommendations/explain/{user_id}/{book_id}")
async def get_recommendation_explanation(user_id: str, book_id: int):
    """Get explanation for why a book was recommended."""
    explanation = recommendation_engine.get_recommendation_explanation(user_id, book_id)
    return {"explanation": explanation}


#! sys Statistics
@app.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system-wide statistics."""
    data_stats = data_loader.get_stats()
    user_stats = user_manager.get_system_stats()

    return SystemStats(
        total_users=user_stats.get("total_users", 0),
        total_reading_entries=user_stats.get("total_reading_entries", 0),
        total_books=data_stats.get("total_books", 0),
        total_categories=data_stats.get("total_categories", 0),
    )


#! err handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Exception", message=exc.detail, status_code=exc.status_code
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error", message=str(exc), status_code=500
        ).dict(),
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
