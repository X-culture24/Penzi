import { useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:5000";

// ✅ Function to get token from localStorage
const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
};

function SelfDescription() {
    const [description, setDescription] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            // ✅ Add Auth Headers (JWT Token)
            const response = await axios.post(
                `${API_URL}/user/self-description`,
                { description },
                { headers: getAuthHeaders() } // 🔥 Include JWT headers
            );

            setMessage(response.data.message);
            setDescription("");
        } catch (error) {
            setMessage("Error submitting self-description.");
            console.error("Submission error:", error.response ? error.response.data : error);
        }
    };

    return (
        <div className="container mt-4">
            <h2>Self Description</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Describe Yourself</label>
                    <textarea
                        className="form-control"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Submit</button>
            </form>
            {message && <p className="mt-3">{message}</p>}
        </div>
    );
}

export default SelfDescription;
