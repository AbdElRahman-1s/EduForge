import { useContext, useEffect } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";

function ProfilePage() {
  console.log('profile render');
  

  const { accessToken } = useContext(AuthContext);


  useEffect(() => {
    async function getProfile() {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/auth/me/",
          {
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          }
        );

        console.log(response);
      } catch (error) {
        console.log(error);
      }
    }

    if (accessToken) {
      getProfile();
    }
  }, [accessToken]);

  return <h1>Profile Page</h1>;
}

export default ProfilePage;