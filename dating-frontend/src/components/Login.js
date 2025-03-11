import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";

function Login() {
    const [phoneNumber, setPhoneNumber] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setMessage(""); // Clear previous errors

        try {
            const response = await axios.post("http://localhost:5000/login", {
                phone_number: phoneNumber,
                password: password,
            });

            const token = response.data.token;

            if (token) {
                localStorage.setItem("token", token); // ✅ Store token
                login(token); // ✅ Update AuthContext
                navigate("/dashboard"); // ✅ Redirect
            } else {
                setMessage("Login failed. Please try again.");
            }
        } catch (error) {
            setMessage(error.response?.data?.error || "Invalid phone number or password.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <div className="mb-3">
                    <label className="form-label">Phone Number</label>
                    <input
                        type="text"
                        className="form-control"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Password</label>
                    <input
                        type="password"
                        className="form-control"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Login</button>
            </form>
            {message && <p className="mt-3 text-danger">{message}</p>}
        </div>
    );
}

export default Login;
