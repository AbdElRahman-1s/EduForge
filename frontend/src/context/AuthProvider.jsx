import { useState , useEffect} from "react";
import { AuthContext } from "./AuthContext";
 import axios from "axios";



export function AuthProvider({children}){

  const [user,setUser] = useState(null);

const [accessToken, setAccessToken] = useState(null);
const [loading , setLoading] = useState(true);
 

useEffect(() => {
  async function refreshAccessToken() {
    try {
      const response = await axios.post(
        "/api/auth/token/refresh/",
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


 useEffect(() => {
    async function getMe() {
      try {
        const response = await axios.get(
          "/api/auth/me/",
          {
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          }
        );

       
        setUser(response.data);
        
      } catch (error) {
        console.log(error);
      }
    }

    if (accessToken) {
      getMe();
    }
  }, [accessToken]);



  function login(userData , token){
    
    setUser(userData);
    
    setAccessToken(token);
  }

async  function logout(){
     try {
      await axios.post(
        "/api/auth/logout/",
        {},{
         headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        
          withCredentials: true,
        }
      );
    }catch(error){
      console.log(error);
      
    } finally {
    setUser(null);
    setAccessToken(null);
      
    }
    

  }




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