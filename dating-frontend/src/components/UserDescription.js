import { useState } from "react";
import axios from "axios";

function UserDescription() {
    const [phoneNumber, setPhoneNumber] = useState("");
    const [description, setDescription] = useState("");
    const [message, setMessage] = useState("");

    const fetchDescription = async () => {
        try {
            const response = await axios.get(`http://localhost:5000/user/describe/${phoneNumber}`);
            if (response.data.description) {
                setDescription(response.data.description);
                setMessage("");
            } else {
                setMessage("No description found for this user.");
            }
        } catch (error) {
            setMessage("Error fetching description.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Get User Description</h2>
            <div className="mb-3">
                <label className="form-label">User Phone Number</label>
                <input
                    type="text"
                    className="form-control"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    required
                />
            </div>
            <button className="btn btn-primary" onClick={fetchDescription}>Describe</button>

            {message && <p className="mt-3">{message}</p>}

            {description && (
                <div className="mt-4">
                    <h3>User Self-Description:</h3>
                    <p className="alert alert-info">{description}</p>
                </div>
            )}
        </div>
    );
}

export default UserDescription;
