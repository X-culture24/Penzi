import { useState } from "react";
import axios from "axios";

function MatchRequest({ userPhone }) {
    const [ageRange, setAgeRange] = useState("");
    const [town, setTown] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem("token"); // ✅ Retrieve token

        if (!token) {
            setMessage("You must be logged in to request a match.");
            return;
        }

        try {
            const response = await axios.post(
                "http://localhost:5000/match/request",
                {
                    age_range: ageRange,
                    town: town,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`, // ✅ Include JWT token
                    },
                }
            );

            setMessage(response.data.message || "Match request successful!");
            setAgeRange("");
            setTown("");
        } catch (error) {
            setMessage(error.response?.data?.error || "Error submitting match request.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Request a Match</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Age Range</label>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="e.g., 23-25"
                        value={ageRange}
                        onChange={(e) => setAgeRange(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Town</label>
                    <input
                        type="text"
                        className="form-control"
                        value={town}
                        onChange={(e) => setTown(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Submit</button>
            </form>
            {message && <p className="mt-3">{message}</p>}
        </div>
    );
}

export default MatchRequest;
