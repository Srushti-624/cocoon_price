import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'

function App() {
    const [token, setToken] = useState(localStorage.getItem('token'))

    useEffect(() => {
        const storedToken = localStorage.getItem('token')
        if (storedToken) {
            setToken(storedToken)
        }
    }, [])

    return (
        <Router>
            <Routes>
                <Route
                    path="/login"
                    element={!token ? <Login setToken={setToken} /> : <Navigate to="/" />}
                />
                <Route
                    path="/register"
                    element={!token ? <Register /> : <Navigate to="/" />}
                />
                <Route
                    path="/"
                    element={token ? <Dashboard setToken={setToken} /> : <Navigate to="/login" />}
                />
            </Routes>
        </Router>
    )
}

export default App
