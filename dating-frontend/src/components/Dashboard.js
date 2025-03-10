import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

function Dashboard() {
    const { user } = useContext(AuthContext);

    return (
        <div className="container mt-4">
            <h2>Welcome, {user ? user.phone_number : "User"}!</h2>
            <p>Explore the dating service and find your perfect match. 💕</p>
        </div>
    );
}

export default Dashboard;
