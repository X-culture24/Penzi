import { useState } from "react";
import axios from "axios";

function SelfDescription({ userPhone }) {
    const [description, setDescription] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await axios.post("http://localhost:5000/user/self-description", {
                phone_number: userPhone,
                description: description,
            });

            setMessage(response.data.message);
            setDescription("");
        } catch (error) {
            setMessage("Error submitting self-description.");
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
