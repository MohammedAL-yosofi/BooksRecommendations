import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { BookOpen, User, Home } from 'lucide-react'
import './App.css'
import BookSearch from './components/BookSearch'
import UserProfile from './components/UserProfile'
import Dashboard from './components/Dashboard'

// generate a unique ID for curr user
const generateUserId = () => {
  return 'user_' + Math.random().toString(36).substring(2, 11)
}

function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const savedUser = localStorage.getItem('Absentee_user')
    return savedUser ? JSON.parse(savedUser) : null
  })
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('Absentee_theme') || 'light'
  })
  // const [showLogin, setShowLogin] = useState(!currentUser)
  const [username, setUsername] = useState('')
  const [isCreatingUser, setIsCreatingUser] = useState(false)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('Absentee_theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  const createUser = async () => {
    if (!username.trim()) {
      alert('Please enter a username')
      return
    }

    setIsCreatingUser(true)
    try {
      const userId = generateUserId()
      const userData = {
        user_id: userId,
        username: username.trim()
      }

      // creat user in python backend
      const response = await fetch('http://localhost:8000/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      })

      if (!response.ok) {
        throw new Error('Failed to create user')
      }

      const createdUser = await response.json()

      // save user to localStorage
      localStorage.setItem('Absentee_user', JSON.stringify(createdUser))
      setCurrentUser(createdUser)
      // setShowLogin(false)
      setUsername('')
    } catch (error) {
      console.error('Error creating user:', error)
      alert('Error creating user. Please try again.')
    } finally {
      setIsCreatingUser(false)
    }
  }

  const logoutUser = () => {
    localStorage.removeItem('Absentee_user')
    setCurrentUser(null)
    // setShowLogin(true)
  }

  return (
    <Router>
      <div className="app">
        <header className="header">
          <div className="header-content">
            <div className="logo">
              <BookOpen className="logo-icon" />
              <h1>SorryForTheAbsence</h1>
            </div>
            <nav className="nav">
              <Link to="/" className="nav-link">
                <Home size={20} />
                Home
              </Link>
              <Link to="/profile" className="nav-link">
                <User size={20} />
                My Profile
              </Link>
              <Link to="/discover" className="nav-link">
                <BookOpen size={20} />
                Discover
              </Link>
            </nav>
            <div className="header-actions">
              {currentUser ? (
                <div className="user-info">
                  <span className="username">@{currentUser.username}</span>
                  <span className="user-id">ID: {currentUser.id}</span>
                  <button
                    onClick={logoutUser}
                    className="btn btn-secondary btn-sm"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="login-form">
                  <input
                    type="text"
                    placeholder="Enter username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && createUser()}
                    className="username-input"
                    disabled={isCreatingUser}
                  />
                  <button
                    onClick={createUser}
                    className="btn btn-primary btn-sm"
                    disabled={isCreatingUser || !username.trim()}
                  >
                    {isCreatingUser ? "Creating..." : "Join"}
                  </button>
                </div>
              )}
              <button onClick={toggleTheme} className="theme-toggle">
                {theme === "light" ? "🌙" : "☀️"}
              </button>
            </div>
          </div>
        </header>

        <main className="main">
          {currentUser ? (
            <Routes>
              <Route
                path="/"
                element={<Dashboard currentUser={currentUser} />}
              />
              <Route
                path="/profile"
                element={<UserProfile currentUser={currentUser} />}
              />
              <Route
                path="/discover"
                element={<BookSearch currentUser={currentUser} />}
              />
            </Routes>
          ) : (
            <div className="welcome-screen">
              <div className="welcome-content">
                <BookOpen size={64} className="welcome-icon" />
                <h1>Welcome to sorryForTheAbsence!</h1>
                <p> </p>
                <p className="welcome-instruction">
                  Please enter a username in the header to get started!
                </p>
              </div>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>&copy; 2025 SorryForTheAbsence</p>
          
          <p> <span className='' style={{color: 'red'}}>Team Members:</span>   Mohammed Fuad ,Mohammed Ahmed Qaid , Mohanad Tawfiq , Huthifa Hamid, Shaif Gayid , Amer Mansour .</p>
          <p> <span className='' style={{color: 'red'}}>Eng /</span>  <span className='instructor-name'>Rana</span></p>
        </footer>
      </div>
    </Router>
  );
}

export default App
