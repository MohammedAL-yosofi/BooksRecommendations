import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional
import csv


class UserManager:
    """Manages user data and reading history using CSV files."""

    def __init__(self, data_dir: str = "../data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.csv")
        self.history_file = os.path.join(data_dir, "user_history.csv")
        self.favorites_file = os.path.join(data_dir, "user_favorites.csv")
        self._ensure_csv_files()

    def _ensure_csv_files(self):
        """Create CSV files if they don't exist."""
        # Create users.csv file for n users 
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "username", "created_at"])
            print(f" Created users file: {self.users_file}")

        # Create user_history.csv file ... 
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["user_id", "book_id", "timestamp"])
            print(f" Created user history file: {self.history_file}")

        #? create user_favorites.csv ..
        if not os.path.exists(self.favorites_file):
            with open(self.favorites_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["user_id", "book_id", "timestamp"])
            print(f" Created user favorites file: {self.favorites_file}")

    def create_user(self, user_id: str, username: str) -> Dict:
        """Create a new user and save to csv"""
        try:
            # Check if user already exists
            if self.get_user(user_id):
                raise ValueError(f"User with ID {user_id} already exists")

           
            user_data = {
                "id": user_id,
                "username": username,
                "created_at": datetime.now().isoformat(),
            }

            # save to csv file 
            with open(self.users_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [user_data["id"], user_data["username"], user_data["created_at"]]
                )

            print(f" Created user: {username} ({user_id})")
            return user_data

        except Exception as e:
            print(f" Error creating user: {str(e)}")
            raise

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information by user_id."""
        try:
            if not os.path.exists(self.users_file):
                return None

            df = pd.read_csv(self.users_file)
            user_row = df[df["id"] == user_id]

            if user_row.empty:
                return None

            return user_row.iloc[0].to_dict()

        except Exception as e:
            print(f" Error getting user: {str(e)}")
            return None

    def get_all_users(self) -> List[Dict]:
        """Get all users."""
        try:
            if not os.path.exists(self.users_file):
                return []

            df = pd.read_csv(self.users_file)
            return df.to_dict("records")

        except Exception as e:
            print(f" Error getting all users: {str(e)}")
            return []

    def add_book_to_history(self, user_id: str, book_id: int) -> bool:
        """Add a book to user's reading history."""
        try:
            # ? check if user exists
            if not self.get_user(user_id):
                raise ValueError(f"User {user_id} does not exist")

            # ? check if book is already in history
            if self.is_book_in_history(user_id, book_id):
                print(f" Book {book_id} already in history for user {user_id}")
                return True

            # add to history
            with open(self.history_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([user_id, book_id, datetime.now().isoformat()])

            print(f" Added book {book_id} to history for user {user_id}")
            return True

        except Exception as e:
            print(f" Error adding book to history: {str(e)}")
            return False

    def get_user_history(self, user_id: str) -> List[int]:
        """Get list of book IDs that user has read."""
        try:
            if not os.path.exists(self.history_file):
                return []

            df = pd.read_csv(self.history_file)
            user_history = df[df["user_id"] == user_id]

            return user_history["book_id"].tolist()

        except Exception as e:
            print(f" Error getting user history: {str(e)}")
            return []

    def get_user_history_with_details(self, user_id: str) -> List[Dict]:
        """Get user history with timestamps."""
        try:
            if not os.path.exists(self.history_file):
                return []

            df = pd.read_csv(self.history_file)
            user_history = df[df["user_id"] == user_id]

            return user_history.to_dict("records")

        except Exception as e:
            print(f" Error getting user history with details: {str(e)}")
            return []

    def is_book_in_history(self, user_id: str, book_id: int) -> bool:
        """Check if a book is already in user's history."""
        try:
            history = self.get_user_history(user_id)
            return book_id in history

        except Exception as e:
            print(f" Error checking book in history: {str(e)}")
            return False

    def remove_book_from_history(self, user_id: str, book_id: int) -> bool:
       
        try:
            if not os.path.exists(self.history_file):
                return False

            
            df = pd.read_csv(self.history_file)

            # remove the specific book
            df = df[~((df["user_id"] == user_id) & (df["book_id"] == book_id))]

            # Save back to file
            df.to_csv(self.history_file, index=False)

            print(f" Removed book {book_id} from history for user {user_id}")
            return True

        except Exception as e:
            print(f" Error removing book from history: {str(e)}")
            return False

    def get_user_stats(self, user_id: str) -> Dict:
        """get statistics for a specific user."""
        try:
            history = self.get_user_history(user_id)
            user_info = self.get_user(user_id)

            if not user_info:
                return {}

            return {
                "user_id": user_id,
                "username": user_info.get("username", ""),
                "created_at": user_info.get("created_at", ""),
                "books_read": len(history),
                "reading_history": history,
            }

        except Exception as e:
            print(f" Error getting user stats: {str(e)}")
            return {}

    def get_system_stats(self) -> Dict:
        
        try:
            users = self.get_all_users()

            # count total reading books
            total_readings = 0
            if os.path.exists(self.history_file):
                df = pd.read_csv(self.history_file)
                total_readings = len(df)

            return {
                "total_users": len(users),
                "total_reading_entries": total_readings,
                "users_file": self.users_file,
                "history_file": self.history_file,
            }

        except Exception as e:
            print(f" Error getting system stats: {str(e)}")
            return {}

    def add_book_to_favorites(self, user_id: str, book_id: int) -> bool:
        
        try:
            # check if already in favorites
            if self.is_book_favorited(user_id, book_id):
                return True 

            # Add to favorites CSV
            with open(self.favorites_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([user_id, book_id, datetime.now().isoformat()])

            # print(f" added book {book_id} to favorites for user {user_id}")
            return True

        except Exception as e:
            print(f" errorr adding book to favorites: {str(e)}")
            return False

    def remove_book_from_favorites(self, user_id: str, book_id: int) -> bool:
        """Remove a book from user's favorites"""
        try:
            if not os.path.exists(self.favorites_file):
                return False

            # read current favorites
            df = pd.read_csv(self.favorites_file)

            # remove the specific entry
            df = df[~((df["user_id"] == user_id) & (df["book_id"] == book_id))]

            # Write back to file
            df.to_csv(self.favorites_file, index=False)

            # print(f" removed book {book_id} from favorites for user {user_id}")
            return True

        except Exception as e:
            print(f" err.. removing book from favorites : {str(e)}")
            return False

    def get_user_favorites(self, user_id: str) -> List[int]:
        """Get list of book IDs that user has favorited."""
        try:
            if not os.path.exists(self.favorites_file):
                return []

            df = pd.read_csv(self.favorites_file)
            user_favorites = df[df["user_id"] == user_id]["book_id"].tolist()

            return user_favorites

        except Exception as e:
            print(f" err.. getting user favorites ; {str(e)}")
            return []

    def is_book_favorited(self, user_id: str, book_id: int) -> bool:
        
        try:
            if not os.path.exists(self.favorites_file):
                return False

            df = pd.read_csv(self.favorites_file)
            return len(df[(df["user_id"] == user_id) & (df["book_id"] == book_id)]) > 0

        except Exception as e:
            print(f" errorr when checking if book is favorited: {str(e)}")
            return False



user_manager = UserManager()
