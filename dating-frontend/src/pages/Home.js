import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="container mt-5 text-center">
      <h1>Welcome to Penzi Dating Service 💕</h1>
      <p>Find your perfect match today!</p>
      <Link to="/register" className="btn btn-success">Get Started</Link>
    </div>
  );
}

export default Home;
