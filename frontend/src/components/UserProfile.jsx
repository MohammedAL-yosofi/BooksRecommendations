import { useState, useEffect } from 'react'
import { User, BookOpen, Heart, Clock, Star, Trash2 } from 'lucide-react'
import axios from 'axios'

const UserProfile = ({ currentUser }) => {
  const [userHistory, setUserHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUserData()
  }, [currentUser])

  const fetchUserData = async () => {
    setLoading(true)
    try {
      // Fetch user reading history
      const historyResponse = await axios.get(`http://localhost:8000/users/${currentUser.id}/history`)
      if (historyResponse.data && historyResponse.data.books) {
        setUserHistory(historyResponse.data.books)
      } else {
        setUserHistory([])
      }
    } catch (error) {
      console.error('Error fetching user data:', error)
      setUserHistory([])
    } finally {
      setLoading(false)
    }
  }

  const removeFromHistory = async (bookId) => {
    try {
      // This would need to be implemented in the backend
      // For now, we'll just remove it from the local state
      setUserHistory(userHistory.filter(book => book.book_id !== bookId))
      alert('Book removed from reading history!')
    } catch (error) {
      console.error('Error removing book from history:', error)
      alert('Error removing book from history')
    }
  }



  if (loading) {
    return (
      <div className="profile-loading">
        <div className="loading-spinner"></div>
        <p>Loading your profile...</p>
      </div>
    )
  }

  return (
    <div className="user-profile animate-fade-in">
      <div className="profile-header">
        <div className="profile-info">
          <div className="profile-avatar">
            <User size={48} />
          </div>
          <div className="profile-details">
            <h1>{currentUser.username}</h1>
            <p>Book enthusiast and avid reader</p>
            <div className="user-id-display">
              <span>User ID: {currentUser.id}</span>
            </div>
            <div className="user-id-display">
              <span>Joined: {new Date(currentUser.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        <div className="profile-stats">
          <div className="stat">
            <BookOpen size={20} />
            <span>{userHistory.length} Books Read</span>
          </div>
        </div>
      </div>

      {/* Reading History Section */}
      <div className="section-header">
        <h2>
          <Clock size={20} />
          Reading History
        </h2>
      </div>

      {/* Reading History Content */}
      <div className="history-section">
        <div className="section-description">
          <p>Books you've read and enjoyed</p>
        </div>

            {userHistory.length > 0 ? (
              <div className="history-grid grid grid-2">
                {userHistory.map((book) => (
                  <div key={book.book_id} className="history-item card">
                    <div className="book-info">
                      <h3>{book.title}</h3>
                      <p className="book-category">{book.category}</p>
                      <div className="book-description">
                        <p>{book.description_to_display.substring(0, 120)}...</p>
                      </div>
                    </div>

                    <div className="book-actions">
                      <button
                        onClick={() => removeFromHistory(book.book_id)}
                        className="btn btn-secondary btn-sm"
                        title="Remove from history"
                      >
                        <Trash2 size={16} />
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state card">
                <BookOpen size={64} />
                <h3>No reading history yet</h3>
                <p>Start exploring books to build your reading history!</p>
                <button className="btn btn-primary">
                  <BookOpen size={16} />
                  Discover Books
                </button>
              </div>
            )}
      </div>

      {/* Reading Insights */}
      {userHistory.length > 0 && (
        <div className="reading-insights">
          <h2>Reading Insights</h2>
          <div className="insights-grid grid grid-3">
            <div className="insight-card card">
              <div className="insight-icon">
                <BookOpen size={24} />
              </div>
              <div className="insight-content">
                <h3>{userHistory.length}</h3>
                <p>Total Books Read</p>
              </div>
            </div>

            <div className="insight-card card">
              <div className="insight-icon">
                <Heart size={24} />
              </div>
              <div className="insight-content">
                <h3>{new Set(userHistory.map(book => book.category)).size}</h3>
                <p>Categories Explored</p>
              </div>
            </div>

            <div className="insight-card card">
              <div className="insight-icon">
                <Star size={24} />
              </div>
              <div className="insight-content">
                <h3>{userHistory.length > 0 ? 'Active' : 'New'}</h3>
                <p>Reader Status</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserProfile
