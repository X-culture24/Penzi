import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const registerUser = (data) => axios.post(`${API_URL}/register`, data);
export const addUserDetails = (data) => axios.post(`${API_URL}/user/details`, data);
export const addSelfDescription = (data) => axios.post(`${API_URL}/user/self-description`, data);
export const requestMatch = (data) => axios.post(`${API_URL}/match/request`, data);
export const getMatches = (userId) => axios.get(`${API_URL}/match/results/${userId}`);
export const sendMessage = (data) => axios.post(`${API_URL}/message`, data);
export const approveMatch = (data) => axios.post(`${API_URL}/approve`, data);
