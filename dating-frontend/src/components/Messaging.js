import { useState } from "react";
import axios from "axios";

function Messaging({ userPhone }) {
    const [toPhoneNumber, setToPhoneNumber] = useState("");
    const [messageContent, setMessageContent] = useState("");
    const [message, setMessage] = useState("");

    const handleSendMessage = async () => {
        try {
            const response = await axios.post("http://localhost:5000/message", {
                from_phone: userPhone,
                to_phone: toPhoneNumber,
                message_content: messageContent
            });

            setMessage(response.data.message);
            setMessageContent(""); // Clear the input field after sending
        } catch (error) {
            setMessage("Error sending message.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Send a Message</h2>

            <div className="mb-3">
                <label className="form-label">Recipient's Phone Number</label>
                <input
                    type="text"
                    className="form-control"
                    value={toPhoneNumber}
                    onChange={(e) => setToPhoneNumber(e.target.value)}
                    required
                />
            </div>

            <div className="mb-3">
                <label className="form-label">Message</label>
                <textarea
                    className="form-control"
                    value={messageContent}
                    onChange={(e) => setMessageContent(e.target.value)}
                    required
                />
            </div>

            <button className="btn btn-success" onClick={handleSendMessage}>
                Send Message
            </button>

            {message && <p className="mt-3 alert alert-info">{message}</p>}
        </div>
    );
}

export default Messaging;
