import { useState, useEffect } from 'react'
import { Search, BookOpen, Heart, Star, Filter, X } from 'lucide-react'
import axios from 'axios'

const BookSearch = ({ currentUser }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [selectedBook, setSelectedBook] = useState(null)
  const [loading, setLoading] = useState(false)
  const [searchType, setSearchType] = useState('title') // 'title' or 'category'
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
    // Load categories on component mount
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      // For now, we'll use static categories based on your data
      setCategories(['الأدب والخيال', 'التاريخ', 'العلوم', 'الفلسفة', 'الدين'])
    } catch (error) {
      console.error('Error loading categories:', error)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await axios.get(`http://localhost:8000/books/search?query=${encodeURIComponent(searchQuery)}&limit=20`)
      if (response.data && response.data.books) {
        setSearchResults(response.data.books)
      } else {
        setSearchResults([])
      }
    } catch (error) {
      console.error('Error searching books:', error)
      setSearchResults([])
    } finally {
      setLoading(false)
    }
  }

  const getRecommendations = async (bookId) => {
    setLoading(true)
    try {
      const response = await axios.get(`http://localhost:8000/books/${bookId}/recommendations`)
      if (response.data && response.data.recommendations) {
        setRecommendations(response.data.recommendations)
      } else {
        setRecommendations([])
      }
      setSelectedBook(bookId)
    } catch (error) {
      console.error('Error getting recommendations:', error)
      setRecommendations([])
    } finally {
      setLoading(false)
    }
  }

  const addToReadingList = async (bookId) => {
    try {
      await axios.post(`http://localhost:8000/users/${currentUser.id}/read`, {
        book_id: bookId
      })
      alert('Book added to your reading history!')
    } catch (error) {
      console.error('Error adding book to reading list:', error)
      alert('Error adding book to reading list')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="book-search animate-fade-in">
      <div className="search-header">
        <h1>Discover Books</h1>
        <p>Search for books and get personalized recommendations</p>
      </div>

      {/* Search Section */}
      <div className="search-section card">
        <div className="search-controls">
          <div className="search-input-group">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Search for books..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="search-input"
            />
            <button onClick={handleSearch} className="btn btn-primary" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          <div className="search-filters">
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
              className="filter-select"
            >
              <option value="title">Search by Title</option>
              <option value="category">Search by Category</option>
            </select>

            {searchType === 'category' && (
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="filter-select"
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            )}
          </div>
        </div>
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="search-results">
          <h2>Search Results ({searchResults.length})</h2>
          <div className="books-grid grid grid-3">
            {searchResults.map((book) => (
              <div key={book.book_id} className="book-card card">
                <div className="book-header">
                  <h3>{book.title}</h3>
                  <span className="book-category">{book.category}</span>
                </div>

                <div className="book-description">
                  <p>{book.description_to_display.substring(0, 150)}...</p>
                </div>

                <div className="book-actions">
                  <button
                    onClick={() => getRecommendations(book.book_id)}
                    className="btn btn-primary"
                  >
                    <Star size={16} />
                    Get Similar Books
                  </button>
                  <button
                    onClick={() => addToReadingList(book.book_id)}
                    className="btn btn-secondary"
                  >
                    <Heart size={16} />
                    Add to List
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="recommendations-section">
          <div className="recommendations-header">
            <h2>Books Similar to Your Selection</h2>
            <button
              onClick={() => {
                setRecommendations([])
                setSelectedBook(null)
              }}
              className="btn btn-secondary"
            >
              <X size={16} />
              Clear
            </button>
          </div>

          <div className="recommendations-grid grid grid-4">
            {recommendations.map((book, index) => (
              <div key={index} className="recommendation-card card">
                <div className="recommendation-header">
                  <h4>{book.title}</h4>
                  <div className="similarity-badge">
                    <Star size={14} />
                    {(book.similarity * 100).toFixed(0)}%
                  </div>
                </div>

                <p className="book-category">{book.category}</p>

                <div className="recommendation-actions">
                  <button
                    onClick={() => addToReadingList(book.book_id)}
                    className="btn btn-primary btn-sm"
                  >
                    <Heart size={14} />
                    Add
                  </button>
                  <button
                    onClick={() => getRecommendations(book.book_id)}
                    className="btn btn-secondary btn-sm"
                  >
                    <Search size={14} />
                    Similar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {searchResults.length === 0 && !loading && searchQuery && (
        <div className="empty-state card">
          <BookOpen size={64} />
          <h3>No books found</h3>
          <p>Try adjusting your search terms or browse by category</p>
        </div>
      )}

      {/* Initial State */}
      {!searchQuery && searchResults.length === 0 && (
        <div className="initial-state">
          <div className="featured-categories">
            <h2>Browse by Category</h2>
            <div className="categories-grid grid grid-3">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => {
                    setSearchType('category')
                    setSelectedCategory(category)
                    setSearchQuery(category)
                    handleSearch()
                  }}
                  className="category-card card"
                >
                  <BookOpen size={24} />
                  <span>{category}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BookSearch
