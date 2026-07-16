 import { useContext} from "react";
// import axios from "axios";
import { AuthContext } from "../context/AuthContext";

function ProfilePage() {
  console.log('profile render');
  

  const { user } = useContext(AuthContext);

//move it to authProvider and put the values into 'user state ' then use the user with context her or in any page need personal info
/*
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
  }, [accessToken]);*/

 if(!user) return <h2></h2>


  return <h1>Profile Page hi <span>{user.username}</span></h1>;
}

export default ProfilePage;