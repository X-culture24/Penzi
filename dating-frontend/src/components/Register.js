import { useState } from "react";
import { registerUser } from "../api/api";
import { useNavigate } from "react-router-dom";

function Register() {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "",
    county: "",
    town: "",
    phone_number: "",
  });

  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await registerUser(formData);
      setMessage(response.data.message);
      setTimeout(() => navigate("/user-details"), 2000); // Redirect to next step
    } catch (error) {
      setMessage(error.response?.data?.error || "Registration failed");
    }
  };

  return (
    <div className="container mt-5">
      <h2>User Registration</h2>
      {message && <div className="alert alert-info">{message}</div>}
      <form onSubmit={handleSubmit} className="mt-3">
        <div className="mb-3">
          <label className="form-label">Name:</label>
          <input type="text" name="name" className="form-control" value={formData.name} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Age:</label>
          <input type="number" name="age" className="form-control" value={formData.age} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Gender:</label>
          <select name="gender" className="form-control" value={formData.gender} onChange={handleChange} required>
            <option value="">Select Gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">County:</label>
          <input type="text" name="county" className="form-control" value={formData.county} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Town:</label>
          <input type="text" name="town" className="form-control" value={formData.town} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Phone Number:</label>
          <input type="text" name="phone_number" className="form-control" value={formData.phone_number} onChange={handleChange} required />
        </div>
        <button type="submit" className="btn btn-primary">Register</button>
      </form>
    </div>
  );
}

export default Register;
