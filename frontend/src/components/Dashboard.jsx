import { useState, useEffect } from 'react'
import { TrendingUp, BookOpen, Users, Star, Heart, Clock, ChevronRight, X } from 'lucide-react'
import axios from 'axios'

const Dashboard = ({ currentUser }) => {
  const [stats, setStats] = useState({
    totalBooks: 0,
    readBooks: 0,
    recommendations: 0
  })
  const [recentRecommendations, setRecentRecommendations] = useState([])

  // const [popularBooks, setPopularBooks] = useState([])
  const [trendingBooks, setTrendingBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [discoveryBooks, setDiscoveryBooks] = useState([])
  const [loadingBooks, setLoadingBooks] = useState(false)
  const [favoriteBooks, setFavoriteBooks] = useState(new Set())
  const [selectedBook, setSelectedBook] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [loadedBookIds, setLoadedBookIds] = useState(new Set())

  useEffect(() => {
    fetchDashboardData()
  }, [currentUser])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)



      //? Fetch user stats ..
      const statsResponse = await axios.get(`http://localhost:8000/users/${currentUser.id}/stats`)

      // Fetch personalized recommendations
      const recommendationsResponse = await axios.get(`http://localhost:8000/users/${currentUser.id}/recommendations`)

      // Update stats and recommendations sec..
      if (statsResponse.data) {
        setStats({
          totalBooks: 4013,
          readBooks: statsResponse.data.books_read || 0,
          recommendations: 0 
        })
      } else {
        setStats({ totalBooks: 4013, readBooks: 0, recommendations: 0 })
      }

      if (recommendationsResponse.data && recommendationsResponse.data.recommendations) {
        const recommendations = recommendationsResponse.data.recommendations
        setRecentRecommendations(recommendations.slice(0, 6))
        setStats(prev => ({ ...prev, recommendations: recommendations.length }))
      } else {
        setRecentRecommendations([])
      }

      
      // setPopularBooks([])

      // // load user favorits
      // const favoritesResponse = await axios.get(`http://localhost:8000/users/${currentUser.id}/favorites`)
      // if (favoritesResponse.data && favoritesResponse.data.books) {
      //   const favoriteIds = favoritesResponse.data.books.map(book => book.book_id)
      //   setFavoriteBooks(new Set(favoriteIds))
      // }


      // we did this as static data ..
      const staticTrendingBooks = [
        { book_id: 1, title: 'في فقه الصراع على القدس وفلسطين', category: 'الأدب والخيال' },
        { book_id: 2, title: 'عذراء قريش', category: 'الأدب والخيال' },
        { book_id: 3, title: 'نفحات من الأدب الإسلامي', category: 'الأدب والخيال' },
        { book_id: 4, title: 'تاريخ الحضارة الإسلامية', category: 'التاريخ' },
        { book_id: 5, title: 'الفلسفة الإسلامية', category: 'الفلسفة' },
        { book_id: 6, title: 'علوم القرآن', category: 'الدين' }
      ]
      setTrendingBooks(staticTrendingBooks)

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      // Set default values on error 0
      setStats({ totalBooks: 4013, readBooks: 0, recommendations: 0 })
      setRecentRecommendations([])
    } finally {
      setLoading(false)
    }
  }


  // load random books in . ..home 
  const loadRandomBooks = async (replace = false) => {
    setLoadingBooks(true)
    try {
      const response = await axios.get(`http://localhost:8000/books/search?query=&limit=10`)

      if (response.data && response.data.books) {
        const randomBooks = response.data.books

        if (replace) {
          
          // replace all books with new books
          setDiscoveryBooks(randomBooks)
          setLoadedBookIds(new Set(randomBooks.map(book => book.book_id)))
        } else {
          
          const availableBooks = randomBooks.filter(book => !loadedBookIds.has(book.book_id))

          if (availableBooks.length > 0) {
            setDiscoveryBooks(prev => [...prev, ...availableBooks])
            setLoadedBookIds(prev => {
              const newSet = new Set(prev)
              availableBooks.forEach(book => newSet.add(book.book_id))
              return newSet
            })
          }
        }
      }
    } catch (error) {
      console.error('Error loading random books:', error)
      alert('Error loading books. Please try again.')
    } finally {
      setLoadingBooks(false)
    }
  }

  // ?favorite button click
  const handleFavorite = async (book) => {
    try {
      const isFavorite = favoriteBooks.has(book.book_id)

      if (isFavorite) {
        // remove from favorites
        const response = await axios.delete(
          `http://localhost:8000/users/${currentUser.id}/favorites/${book.book_id}`
        )

        if (response.data.success) {
          setFavoriteBooks(prev => {
            const newSet = new Set(prev)
            newSet.delete(book.book_id)
            return newSet
          })


          // alert(`"${book.title}" remove from fav `)
        }
      } else {

        // Add to favorites
        const response = await axios.post(
          `http://localhost:8000/users/${currentUser.id}/favorites`,
          { book_id: book.book_id }
        )

        if (response.data.success) {
          setFavoriteBooks(prev => new Set([...prev, book.book_id]))
          //test
          // alert(`"${book.title}" added to favorite s  `)
        }
      }
    } catch (error) {
      console.error('Error handling favorite:', error)
      alert('Error updating favorites')
    }
  }

  // ? card click show modal and automatically mark as read
  const handleCardClick = async (book) => {
    setSelectedBook(book)
    setShowModal(true)

    // auto... as read 
    try {
      const response = await axios.post(
        `http://localhost:8000/users/${currentUser.id}/read`,
        { book_id: book.book_id }


      )

      if (response.data.success) {
        // updat stats for ... read books
        setStats(prev => ({
          ...prev,
          readBooks: prev.readBooks + 1 
        }))



        // alert( ' added to reading history');
      }
    } catch (error) {
      console.error('erro when make book as read', error)
      
    
      setStats(prev => ({
        ...prev,
        readBooks: prev.readBooks + 1
      }))
    }
  }



  // 
  useEffect(() => {
    if (currentUser) {
      loadRandomBooks(true) 
    }
  }, [currentUser])

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your personalized dashboard...</p>
      </div>
    )
  }

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <h1>Welcome to SorryForTheAbsence!</h1>
        <p>a personal book recommendations system</p>
        <div className="user-welcome">
          <span className="welcome-text">Hello, {currentUser.username}!</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid grid grid-3">
        <div className="stat-card card">
          <div className="stat-icon">
            <BookOpen className="icon" />
          </div>
          <div className="stat-content">
            <h3>{stats.totalBooks.toLocaleString()}</h3>
            <p>Total Books</p>
          </div>
        </div>

        <div className="stat-card card">
          <div className="stat-icon">
            <Heart className="icon" />
          </div>
          <div className="stat-content">
            <h3>{stats.readBooks}</h3>
            <p>Books Read</p>
          </div>
        </div>

        <div className="stat-card card">
          <div className="stat-icon">
            <TrendingUp className="icon" />
          </div>
          <div className="stat-content">
            <h3>{stats.recommendations}</h3>
            <p>Recommendations</p>
          </div>
        </div>
      </div>

      {/* Book Discovery Section */}
      <div className="discovery-section">
        <div className="section-header">
          <h2>Discover Books</h2>
          
        </div>

        {discoveryBooks.length > 0 ? (
          <>
            <div className="books-grid discovery-books-grid grid grid-3">
              {discoveryBooks.map((book) => (
                <div
                  key={book.book_id}
                  className="book-card discovery-book-card"
                  onClick={() => handleCardClick(book)}
                >
                  <div className="book-card-header">
                    <button
                      className={`favorite-btn ${
                        favoriteBooks.has(book.book_id) ? 'favorited' : ''
                      }`}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleFavorite(book)
                      }}
                    >
                      <Heart
                        size={20}
                        fill={favoriteBooks.has(book.book_id) ? 'currentColor' : 'none'}
                      />
                    </button>
                  </div>
                  <div className="book-card-content">
                    <h3 className="book-title">{book.title}</h3>
                    <span className="book-category">{book.category}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="discovery-actions">
              <button
                className="btn btn-primary"
                onClick={() => loadRandomBooks(false)}
                disabled={loadingBooks}
              >
                {loadingBooks ? (
                  <>
                    <div className="loading-spinner"></div>
                    Loading...
                  </>
                ) : (
                  'Load More Books'
                )}
              </button>
            </div>
          </>
        ) : (
          <div className="empty-discovery">
            <BookOpen size={64} />
            <h3>No books loaded</h3>
            <p>Click "Load Books" to discover new books!</p>
            <button
              className="btn btn-primary"
              onClick={() => loadRandomBooks(true)}
              disabled={loadingBooks}
            >
              {loadingBooks ? (
                <>
                  <div className="loading-spinner"></div>
                  Loading...
                </>
              ) : (
                'Load Books'
              )}
            </button>
          </div>
        )}
      </div>

      <div className="dashboard-content grid grid-2">
        {/* Recent Recommendations */}
        <div className="recommendations-section">
          <div className="section-header">
            <h2>Recommended for You</h2>
            <p>Based on your reading history</p>
          </div>
          
          <div className="recommendations-list">
            {recentRecommendations.length > 0 ? (
              recentRecommendations.map((book, index) => (
                <div key={index} className="recommendation-item card">
                  <div className="book-info">
                    <h4>{book.title}</h4>
                    <p className="book-category">{book.category}</p>
                    <div className="book-meta">
                      <span className="similarity-score">
                        <Star size={16} />
                        {(book.similarity * 100).toFixed(0)}% match
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <BookOpen size={48} />
                <h3>No recommendations yet</h3>
                <p>Start reading some books to get personalized recommendations!</p>
              </div>
            )}
          </div>
        </div>

        {/* Popular Books */}
        <div className="popular-section">
          <div className="section-header">
            <h2>Trending Books</h2>
            <p>Popular among readers</p>
          </div>

          <div className="popular-list">
            {trendingBooks.length > 0 ? (
              trendingBooks.map((book) => (
                <div key={book.book_id} className="popular-item card">
                  <div className="book-info">
                    <h4>{book.title}</h4>
                    <p className="book-category">{book.category}</p>
                    <div className="book-rating">
                      <Star size={16} fill="currentColor" />
                      <span>Popular</span>
                    </div>
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleCardClick(book)}
                  >
                    View Details
                  </button>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <BookOpen size={48} />
                <h3>Loading trending books...</h3>
              </div>
            )}
          </div>
        </div>
      </div>



      {/* Book Details Modal */}
      {showModal && selectedBook && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedBook.title}</h2>
              <button
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                <X size={24} />
              </button>
            </div>

            <div className="modal-body">
              <div className="book-details">
                <p className="book-category">
                  <strong>Category:</strong> {selectedBook.category}
                </p>
                <div className="book-description">
                  <strong>Description:</strong>
                  <p>{selectedBook.description_to_display}</p>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-primary"
                onClick={() => setShowModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
