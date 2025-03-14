import React, { useState } from "react";
import ChatBox from "./components/ChatBox";
import "./App.css";

const App = () => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handlePhoneSubmit = (number) => {
    setPhoneNumber(number);
    setIsAuthenticated(true);
  };

  return (
    <div className="app-container">
      {!isAuthenticated ? (
        <PhoneInput onSubmit={handlePhoneSubmit} />
      ) : (
        <ChatBox phoneNumber={phoneNumber} />
      )}
    </div>
  );
};

const PhoneInput = ({ onSubmit }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.match(/^07\d{8}$/)) {
      onSubmit(input);
    } else {
      alert("Please enter a valid Kenyan phone number (e.g., 0712345678)");
    }
  };

  return (
    <div className="phone-input-container">
      <h2>Welcome to Penzi 💜</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter your phone number"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          required
        />
        <button type="submit">Start Chat</button>
      </form>
    </div>
  );
};

export default App;

