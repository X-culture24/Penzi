import { useState } from "react";
import { addUserDetails } from "../api/api";
import { useNavigate } from "react-router-dom";

function UserDetails() {
  const [formData, setFormData] = useState({
    level_of_education: "",
    profession: "",
    marital_status: "",
    religion: "",
    ethnicity: "",
  });

  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Submitting Data:", formData);  // ✅ Debugging output

    try {
      const response = await addUserDetails(formData);
      console.log("Response:", response.data);
      setMessage(response.data.message);
      setTimeout(() => navigate("/self-description"), 2000);
    } catch (error) {
      console.error("Error Response:", error.response?.data);
      setMessage(error.response?.data?.error || "Submission failed");
    }
  };

  return (
    <div className="container mt-5">
      <h2>Add User Details</h2>
      {message && <div className="alert alert-info">{message}</div>}
      <form onSubmit={handleSubmit} className="mt-3">
        <div className="mb-3">
          <label className="form-label">Level of Education:</label>
          <input type="text" name="level_of_education" className="form-control" value={formData.level_of_education} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Profession:</label>
          <input type="text" name="profession" className="form-control" value={formData.profession} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Marital Status:</label>
          <select name="marital_status" className="form-control" value={formData.marital_status} onChange={handleChange} required>
            <option value="">Select Status</option>
            <option value="Single">Single</option>
            <option value="Married">Married</option>
            <option value="Divorced">Divorced</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Religion:</label>
          <input type="text" name="religion" className="form-control" value={formData.religion} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Ethnicity:</label>
          <input type="text" name="ethnicity" className="form-control" value={formData.ethnicity} onChange={handleChange} required />
        </div>
        <button type="submit" className="btn btn-primary">Save Details</button>
      </form>
    </div>
  );
}

export default UserDetails;
