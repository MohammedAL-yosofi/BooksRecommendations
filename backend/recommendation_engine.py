import numpy as np
from typing import List, Dict, Optional
from data_loader import data_loader
from user_manager import user_manager


class RecommendationEngine:
    """Handles all recommendation logic for the book recommendation system."""

    def __init__(self):
        self.data_loader = data_loader
        self.user_manager = user_manager

    def get_item_to_item_recommendations(
        self, book_id: int, limit: int = 10
    ) -> List[Dict]:
        """
        Get item-to-item recommendations for a given book.
        Uses the precomputed similarity matrix.
        """
        try:
            similar_books = self.data_loader.get_similar_books(book_id, limit)
            return similar_books

        except Exception as e:
            print(f"❌ Error getting item-to-item recommendations: {str(e)}")
            return []

    def get_user_based_recommendations(
        self, user_id: str, limit: int = 10
    ) -> List[Dict]:
        """Get recommendations based on user's reading history using collaborative filtering."""
        try:
            # Get user's reading history
            user_history = self.user_manager.get_user_history(user_id)

            if not user_history:
                # If no history, return empty (let hybrid handle popular books)
                return []

            # Collect similarity scores for all books based on user's history
            book_scores = {}

            for read_book_id in user_history:
                # Get similar books for each book in user's history
                similar_books = self.data_loader.get_similar_books(
                    read_book_id, limit * 2
                )

                for similar_book in similar_books:
                    book_id = similar_book["book_id"]
                    similarity = similar_book["similarity"]

                    # Skip books already in user's history
                    if book_id in user_history:
                        continue

                    # Accumulate similarity scores
                    if book_id in book_scores:
                        book_scores[book_id] += similarity
                    else:
                        book_scores[book_id] = similarity

            # Sort books by accumulated similarity scores
            sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)

            # Get book details for top recommendations
            recommendations = []
            for book_id, score in sorted_books[:limit]:
                book_info = self.data_loader.get_book_by_id(book_id)
                if book_info:
                    book_info["similarity"] = float(
                        score / len(user_history)
                    )  # Average similarity
                    recommendations.append(book_info)

            return recommendations

        except Exception as e:
            print(f"❌ Error getting user-based recommendations: {str(e)}")
            return []

    def get_category_based_recommendations(
        self, user_id: str, limit: int = 10
    ) -> List[Dict]:
        """
        Get recommendations based on user's preferred categories.
        """
        try:
            # Get user's reading history
            user_history = self.user_manager.get_user_history(user_id)

            if not user_history:
                return []

            # Find user's preferred categories
            category_counts = {}
            for book_id in user_history:
                book_info = self.data_loader.get_book_by_id(book_id)
                if book_info and "category" in book_info:
                    category = book_info["category"]
                    category_counts[category] = category_counts.get(category, 0) + 1

            # Get top categories
            top_categories = sorted(
                category_counts.items(), key=lambda x: x[1], reverse=True
            )

            recommendations = []
            books_per_category = (
                max(1, limit // len(top_categories)) if top_categories else limit
            )

            for category, _ in top_categories:
                category_books = self.data_loader.get_books_by_category(
                    category, books_per_category * 2
                )

                # Filter out books already read
                for book in category_books:
                    if (
                        book["book_id"] not in user_history
                        and len(recommendations) < limit
                    ):
                        book["similarity"] = (
                            0.8  # Default similarity for category match
                        )
                        recommendations.append(book)

            return recommendations[:limit]

        except Exception as e:
            print(f"❌ Error getting category-based recommendations: {str(e)}")
            return []

    def get_hybrid_recommendations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get hybrid recommendations combining multiple approaches.
        """
        try:
            # Check if user has reading history first
            user_history = self.user_manager.get_user_history(user_id)
            if not user_history:
                # Return empty for new users - let them see trending books instead
                return []

            # Get recommendations from different methods
            user_based = self.get_user_based_recommendations(user_id, limit // 2)
            category_based = self.get_category_based_recommendations(
                user_id, limit // 2
            )

            # Combine and deduplicate
            seen_books = set()
            hybrid_recommendations = []

            # Add user-based recommendations first (higher priority)
            for book in user_based:
                if book["book_id"] not in seen_books:
                    seen_books.add(book["book_id"])
                    hybrid_recommendations.append(book)

            # Add category-based recommendations
            for book in category_based:
                if (
                    book["book_id"] not in seen_books
                    and len(hybrid_recommendations) < limit
                ):
                    seen_books.add(book["book_id"])
                    hybrid_recommendations.append(book)

            # If no recommendations found for user with history, fallback to popular books
            if not hybrid_recommendations:
                return self._get_popular_books(limit)

            return hybrid_recommendations

        except Exception as e:
            print(f"❌ Error getting hybrid recommendations: {str(e)}")
            return []

    def _get_popular_books(self, limit: int = 10) -> List[Dict]:
        """
        Get popular books (fallback when no user history or errors occur).
        For now, returns random books from the dataset.
        """
        try:
            if self.data_loader.book_metadata is None:
                return []

            # Get random sample of books
            sample_books = self.data_loader.book_metadata.sample(
                n=min(limit, len(self.data_loader.book_metadata))
            )
            books = sample_books.to_dict("records")

            # Add default similarity score
            for book in books:
                book["similarity"] = 0.5

            return books

        except Exception as e:
            print(f"❌ Error getting popular books: {str(e)}")
            return []

    def get_book_recommendations_by_title(
        self, title: str, limit: int = 10
    ) -> List[Dict]:
        """
        Get recommendations for a book by its title.
        """
        try:
            # Find the book by title
            book_info = self.data_loader.get_book_by_title(title)
            if not book_info:
                return []

            book_id = book_info["book_id"]
            return self.get_item_to_item_recommendations(book_id, limit)

        except Exception as e:
            print(f"❌ Error getting recommendations by title: {str(e)}")
            return []

    def get_recommendation_explanation(self, user_id: str, book_id: int) -> str:
        """
        Get an explanation for why a book was recommended to a user.
        """
        try:
            user_history = self.user_manager.get_user_history(user_id)
            book_info = self.data_loader.get_book_by_id(book_id)

            if not book_info:
                return "Book not found."

            if not user_history:
                return f"Recommended because '{book_info['title']}' is a popular book in {book_info['category']}."

            # Find most similar book in user's history
            max_similarity = 0
            most_similar_book = None

            for read_book_id in user_history:
                if read_book_id < len(
                    self.data_loader.similarity_matrix
                ) and book_id < len(self.data_loader.similarity_matrix):
                    similarity = self.data_loader.similarity_matrix[read_book_id][
                        book_id
                    ]
                    if similarity > max_similarity:
                        max_similarity = similarity
                        most_similar_book = self.data_loader.get_book_by_id(
                            read_book_id
                        )

            if most_similar_book:
                return f"Recommended because you read '{most_similar_book['title']}' and this book is {max_similarity:.1%} similar."
            else:
                return f"Recommended based on your interest in {book_info['category']} books."

        except Exception as e:
            print(f"❌ Error getting recommendation explanation: {str(e)}")
            return "Recommended for you."


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
