import { useState } from "react";
import axios from "axios";

function Approval() {
    const [matchedUserId, setMatchedUserId] = useState("");
    const [requestingUserId, setRequestingUserId] = useState("");
    const [status, setStatus] = useState("approved"); // Default to "approved"
    const [message, setMessage] = useState("");

    const handleApproval = async () => {
        try {
            const response = await axios.post("http://localhost:5000/approve", {
                matched_user_id: matchedUserId,
                requesting_user_id: requestingUserId,
                status: status
            });

            setMessage(response.data.message);
        } catch (error) {
            setMessage("Error processing approval request.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Approve or Reject Match</h2>
            <div className="mb-3">
                <label className="form-label">Matched User ID</label>
                <input
                    type="text"
                    className="form-control"
                    value={matchedUserId}
                    onChange={(e) => setMatchedUserId(e.target.value)}
                    required
                />
            </div>

            <div className="mb-3">
                <label className="form-label">Requesting User ID</label>
                <input
                    type="text"
                    className="form-control"
                    value={requestingUserId}
                    onChange={(e) => setRequestingUserId(e.target.value)}
                    required
                />
            </div>

            <div className="mb-3">
                <label className="form-label">Approval Status</label>
                <select
                    className="form-select"
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                >
                    <option value="approved">Approve</option>
                    <option value="rejected">Reject</option>
                </select>
            </div>

            <button className="btn btn-primary" onClick={handleApproval}>
                Submit Approval
            </button>

            {message && <p className="mt-3 alert alert-info">{message}</p>}
        </div>
    );
}

export default Approval;
