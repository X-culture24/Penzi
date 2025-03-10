import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import { useContext } from "react";
import { AuthContext, AuthProvider } from "./context/AuthContext";
import ProtectedRoutes from "./routes/ProtectedRoutes";
import Register from "./components/Register";
import UserDetails from "./components/UserDetails";
import SelfDescription from "./components/SelfDescription";
import MatchRequest from "./components/MatchRequest";
import MatchResults from "./components/MatchResults";
import Messaging from "./components/Messaging";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

function Navigation() {
    const { user, logout } = useContext(AuthContext);

    return (
        <nav className="nav nav-pills nav-fill mb-4">
            <Link className="nav-link" to="/">Home</Link>
            {!user ? (
                <>
                    <Link className="nav-link" to="/login">Login</Link>
                    <Link className="nav-link" to="/register">Register</Link>
                </>
            ) : (
                <>
                    <Link className="nav-link" to="/dashboard">Dashboard</Link>
                    <Link className="nav-link" to="/user-details">User Details</Link>
                    <Link className="nav-link" to="/self-description">Self-Description</Link>
                    <Link className="nav-link" to="/match-request">Match Request</Link>
                    <Link className="nav-link" to="/match-results">Match Results</Link>
                    <Link className="nav-link" to="/messaging">Messaging</Link>
                    <button className="btn btn-danger ms-2" onClick={logout}>Logout</button>
                </>
            )}
        </nav>
    );
}

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="container mt-4">
                    <h1 className="text-center">Penzi Dating Service ❤️</h1>
                    <Navigation />

                    <Routes>
                        <Route path="/" element={<h2 className="text-center">Welcome to Penzi Dating Service! 💕</h2>} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />

                        {/* Protected Routes */}
                        <Route element={<ProtectedRoutes />}>
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/user-details" element={<UserDetails />} />
                            <Route path="/self-description" element={<SelfDescription />} />
                            <Route path="/match-request" element={<MatchRequest />} />
                            <Route path="/match-results" element={<MatchResults />} />
                            <Route path="/messaging" element={<Messaging />} />
                        </Route>
                    </Routes>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
