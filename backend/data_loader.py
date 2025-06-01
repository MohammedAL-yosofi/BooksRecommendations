import pandas as pd
import numpy as np
import pickle
import os
from typing import Dict, List, Optional


class DataLoader:
    """Handles loading and managing all data artifacts for the book recommendation system."""

    def __init__(self, data_dir: str = "../data"):
        self.data_dir = data_dir
        self.book_metadata = None
        self.similarity_matrix = None
        self.title_to_index = None
        self.index_to_title = None
        self.book_embeddings = None

    def load_all_data(self):
        """Load all data artifacts from the data directory."""
        try:
            print("Loading book recommendation data...")

            # Load book metadata
            metadata_path = os.path.join(self.data_dir, "book_metadata.csv")
            self.book_metadata = pd.read_csv(metadata_path)
            print(f"✅ Loaded {len(self.book_metadata)} books from metadata")

            # Load similarity matrix
            similarity_path = os.path.join(self.data_dir, "similarity_matrix.npy")
            self.similarity_matrix = np.load(similarity_path)
            print(f"✅ Loaded similarity matrix: {self.similarity_matrix.shape}")

            # Load title to index .. from pkl file we saved after embedding .... see read me file for more details
            title_to_index_path = os.path.join(self.data_dir, "title_to_index.pkl")
            with open(title_to_index_path, "rb") as f:
                self.title_to_index = pickle.load(f)
            print(
                f"✅ Loaded title to index mapping: {len(self.title_to_index)} entries"
            )

            #? Load index to title .....
            index_to_title_path = os.path.join(self.data_dir, "index_to_title.pkl")
            with open(index_to_title_path, "rb") as f:
                self.index_to_title = pickle.load(f)
            print(
                f"✅ Loaded index to title mapping: {len(self.index_to_title)} entries"
            )

            #? Try to load book embeddings 
            embeddings_path = os.path.join(self.data_dir, "book_embeddings.npy")
            if os.path.exists(embeddings_path):
                self.book_embeddings = np.load(embeddings_path)
                print(f" Loaded book embeddings: {self.book_embeddings.shape}")
            else:
                print("  Book embeddings not found - will use similarity matrix only")

            print(" All data loaded successfully!")
            return True

        except Exception as e:
            print(f" Error loading data: {str(e)}")
            return False

    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        """Get book information by book_id."""
        if self.book_metadata is None:
            return None

        book_row = self.book_metadata[self.book_metadata["book_id"] == book_id]
        if book_row.empty:
            return None

        return book_row.iloc[0].to_dict()

    def get_book_by_title(self, title: str) -> Optional[Dict]:
        """Get book information by title."""
        if self.book_metadata is None:
            return None

        book_row = self.book_metadata[
            self.book_metadata["title"].str.contains(title, case=False, na=False)
        ]
        if book_row.empty:
            return None

        return book_row.iloc[0].to_dict()

    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Search books by title or category."""
        if self.book_metadata is None:
            return []

        #? If query is empty, return random books ..
        if not query or query.strip() == "":
            return self.get_random_books_from_categories(limit)

        #? Search by  title and category
        mask = self.book_metadata["title"].str.contains(
            query, case=False, na=False
        ) | self.book_metadata["category"].str.contains(query, case=False, na=False)

        results = self.book_metadata[mask].head(limit)
        return results.to_dict("records")

    def get_similar_books(self, book_id: int, limit: int = 10) -> List[Dict]:
        """Get similar books using the similarity matrix."""
        
        if self.similarity_matrix is None or book_id >= len(self.similarity_matrix):
            return []

        #? Get similarity scores for the given book ..
        similarities = self.similarity_matrix[book_id]

        #? get indices of most similar books 
        similar_indices = np.argsort(similarities)[::-1][1 : limit + 1]

        # get book information for similar books
        similar_books = []
        
        for idx in similar_indices:
            if idx < len(self.book_metadata):
                book_info = self.book_metadata.iloc[idx].to_dict()
                book_info["similarity"] = float(similarities[idx])
                similar_books.append(book_info)

        return similar_books

    def get_books_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get books by category."""
        if self.book_metadata is None:
            return []

        books = self.book_metadata[
            self.book_metadata["category"].str.contains(category, case=False, na=False)
        ].head(limit)

        return books.to_dict("records")

    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        if self.book_metadata is None:
            return []

        return self.book_metadata["category"].unique().tolist()

    def get_stats(self) -> Dict:
        """Get general statistics about the dataset."""
        if self.book_metadata is None:
            return {}

        return {
            "total_books": len(self.book_metadata),
            "total_categories": len(self.book_metadata["category"].unique()),
            "similarity_matrix_shape": (
                self.similarity_matrix.shape
                if self.similarity_matrix is not None
                else None
            ),
            "has_embeddings": self.book_embeddings is not None,
        }

    def get_random_books_from_categories(self, limit: int = 10) -> List[Dict]:
        """Get random books from different categories for discovery."""
        try:
            if self.book_metadata is None:
                return []

            #?? Get all unique categories
            categories = self.book_metadata["category"].unique()

            #? Calculate books per category
            books_per_category = max(1, limit // len(categories))
            
            selected_books = []
            used_book_ids = set()

            
            np.random.shuffle(categories)

            for category in categories:
                if len(selected_books) >= limit:
                    break

                #?.. Get books from this category ->
                category_books = self.book_metadata[
                    self.book_metadata["category"] == category
                ]

               
                remaining_slots = limit - len(selected_books)
                sample_size = min(
                    books_per_category, len(category_books), remaining_slots
                )

                if sample_size > 0:
                    sampled_books = category_books.sample(n=sample_size)

                    for _, book in sampled_books.iterrows():
                        if (
                            book["book_id"] not in used_book_ids
                            and len(selected_books) < limit
                        ):
                            book_dict = book.to_dict()
                            selected_books.append(book_dict)
                            used_book_ids.add(book["book_id"])

            #! if we still need more books ... give random books ->
            if len(selected_books) < limit:
                remaining_books = self.book_metadata[
                    ~self.book_metadata["book_id"].isin(used_book_ids)
                ]
                if len(remaining_books) > 0:
                    additional_needed = limit - len(selected_books)
                    additional_books = remaining_books.sample(
                        n=min(additional_needed, len(remaining_books))
                    )

                    for _, book in additional_books.iterrows():
                        selected_books.append(book.to_dict())

            return selected_books

        except Exception as e:
            print(f" Error getting random books from categories: {str(e)}")
            return []

    def get_random_books(self, limit: int = 10) -> List[Dict]:
        """Get completely random books (for trending/popular section)."""
        try:
            if self.book_metadata is None:
                return []

            # ? Sample random books
            sample_size = min(limit, len(self.book_metadata))
            sampled_books = self.book_metadata.sample(n=sample_size)

            return sampled_books.to_dict("records")

        except Exception as e:
            print(f" Error getting random books: {str(e)}")
            return []



data_loader = DataLoader()
