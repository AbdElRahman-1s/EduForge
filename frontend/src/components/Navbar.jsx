import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import axios from "axios";

function Navbar() {
  

  const { logout , accessToken} = useContext(AuthContext);
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await axios.post(
        "/api/auth/logout/",
        {},{
         headers: {
          Authorization: `Bearer ${accessToken}`,
        }},
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