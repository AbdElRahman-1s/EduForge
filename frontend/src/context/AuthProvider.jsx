import { useState , useEffect} from "react";
import { AuthContext } from "./AuthContext";
 import axios from "axios";



export function AuthProvider({children}){

  const [user,setUser] = useState(() => {
  const savedUser = localStorage.getItem("user");
    
  return savedUser ? JSON.parse(savedUser) : null;
});

const [accessToken, setAccessToken] = useState(null);
const [loading , setLoading] = useState(true);
 

useEffect(() => {
  async function refreshAccessToken() {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/auth/refresh/",
        null,
        {
          withCredentials: true,
        }
      );

      setAccessToken(response.data.access);
      
    } catch (error) {
      console.log(error);
    }finally{
      setLoading(false);
    }
  }

  refreshAccessToken();
}, []);



  function login(userData , token){
    console.log("Token before set:", token);
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
    setAccessToken(token);
  }

  function logout(){
    console.log('loged out');
    
    setUser(null);
    localStorage.removeItem("user");
     setAccessToken(null);
  }


  console.log({
  user,
  accessToken,
});

  return(
    <AuthContext.Provider
    value={{
      user,
      accessToken,
      login,
      logout,
      loading
    }}>
      {children}
    </AuthContext.Provider>
  );


}