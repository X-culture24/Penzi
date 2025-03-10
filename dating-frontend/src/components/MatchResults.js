import { useState } from "react";
import axios from "axios";

function MatchResults({ userPhone }) {
    const [matches, setMatches] = useState([]);
    const [message, setMessage] = useState("");

    const fetchMatches = async () => {
        try {
            const response = await axios.get(`http://localhost:5000/match/results?phone_number=${userPhone}`);
            setMatches(response.data.matches);
            setMessage("");
        } catch (error) {
            setMessage("No matches found.");
            setMatches([]);
        }
    };

    return (
        <div className="container mt-4">
            <h2>View Your Matches</h2>
            <button className="btn btn-primary" onClick={fetchMatches}>Get Matches</button>

            {message && <p className="mt-3">{message}</p>}

            {matches.length > 0 && (
                <div className="mt-4">
                    <h3>Matches Found:</h3>
                    <ul className="list-group">
                        {matches.map((match, index) => (
                            <li key={index} className="list-group-item">
                                Matched User: {match.matched_user_name} (Phone: {match.matched_user_phone})
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default MatchResults;
