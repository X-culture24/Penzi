import { useState } from "react";
import axios from "axios";

function MatchRequest({ userPhone }) {
    const [ageRange, setAgeRange] = useState("");
    const [town, setTown] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await axios.post("http://localhost:5000/match/request", {
                phone_number: userPhone,  // Use phone number instead of user_id
                age_range: ageRange,
                town: town,
            });

            setMessage(response.data.message);
            setAgeRange("");
            setTown("");
        } catch (error) {
            setMessage("Error submitting match request.");
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
