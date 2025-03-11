import axios from "axios";

const API_URL = "http://localhost:5000";

// ✅ Function to get token from localStorage
const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
};

// ✅ User Registration
export const registerUser = (data) => axios.post(`${API_URL}/register`, data);

// ✅ User Login (Stores JWT Token)
export const loginUser = async (data) => {
    try {
        const response = await axios.post(`${API_URL}/login`, data);
        if (response.data.token) {
            localStorage.setItem("token", response.data.token); // ✅ Store token
        }
        return response;
    } catch (error) {
        console.error("Login error:", error.response ? error.response.data : error);
        throw error;
    }
};

// ✅ Add User Details (Requires JWT Token)
export const addUserDetails = (data) => 
    axios.post(`${API_URL}/user/details`, data, { headers: getAuthHeaders() });

// ✅ Add Self Description
export const addSelfDescription = (data) => 
    axios.post(`${API_URL}/user/self-description`, data, { headers: getAuthHeaders() });

// ✅ Request Match
export const requestMatch = (data) => 
    axios.post(`${API_URL}/match/request`, data, { headers: getAuthHeaders() });

// ✅ Get Match Results
export const getMatches = () => 
    axios.get(`${API_URL}/match/results`, { headers: getAuthHeaders() });

// ✅ Send Message
export const sendMessage = (data) => 
    axios.post(`${API_URL}/message`, data, { headers: getAuthHeaders() });

// ✅ Approve Match
export const approveMatch = (data) => 
    axios.post(`${API_URL}/approve`, data, { headers: getAuthHeaders() });

// ✅ Logout (Clears Token)
export const logoutUser = () => {
    localStorage.removeItem("token");
};
