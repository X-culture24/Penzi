import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./ChatBox.css";

const ChatBox = ({ phoneNumber }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to latest message
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = {
      content: input,
      sender: "user",
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages([...messages, newMessage]);
    setInput("");

    try {
      const response = await axios.post("http://localhost:5000/penzi", {
        phone_number: phoneNumber,
        message: input,
      });

      const systemResponse = {
        content: response.data.response,
        sender: "system",
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, systemResponse]);
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Failed to send message. Please try again.");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">💌 Penzi Chat</div>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender === "user" ? "user" : "system"}`}
          >
            <span className="message-content">{msg.content}</span>
            <span className="timestamp">🕒 {msg.timestamp}</span>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
        />
        <button onClick={handleSendMessage}>🚀 Send</button>
      </div>
    </div>
  );
};

export default ChatBox;
