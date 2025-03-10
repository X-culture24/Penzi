import { useState } from "react";
import axios from "axios";

function MoreMatches() {
    const [userId, setUserId] = useState("");
    const [matches, setMatches] = useState([]);
    const [message, setMessage] = useState("");

    const fetchMoreMatches = async () => {
        try {
            const response = await axios.get(`http://localhost:5000/match/next/${userId}`);
            if (response.data.matches.length > 0) {
                setMatches([...matches, ...response.data.matches]);
                setMessage("");
            } else {
                setMessage("No more matches available.");
            }
        } catch (error) {
            setMessage("Error fetching more matches.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Get More Matches</h2>
            <div className="mb-3">
                <label className="form-label">User ID</label>
                <input
                    type="text"
                    className="form-control"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    required
                />
            </div>
            <button className="btn btn-primary" onClick={fetchMoreMatches}>Next</button>

            {message && <p className="mt-3">{message}</p>}

            {matches.length > 0 && (
                <div className="mt-4">
                    <h3>More Matches:</h3>
                    <ul className="list-group">
                        {matches.map((match, index) => (
                            <li key={index} className="list-group-item">
                                Matched User ID: {match.matched_user_id}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default MoreMatches;
