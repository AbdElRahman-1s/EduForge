import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import axios from "axios";

function Navbar() {
  

  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await axios.post(
        "http://127.0.0.1:8000/api/auth/logout/",
        {},
        {
          withCredentials: true,
        }
      );
    } finally {
      logout();
      navigate("/");
    }
  }



  return (
    <>
    
    <div>Navbar</div>
    <button onClick={handleLogout}>Logout</button>
    </>
  )
}

export default Navbar