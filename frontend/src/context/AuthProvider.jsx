import { useState } from "react";
import { AuthContext } from "./AuthContext";



export function AuthProvider({children}){

  const [user,setUser] = useState(() => {
  const savedUser = localStorage.getItem("user");

  return savedUser ? JSON.parse(savedUser) : null;
});

  function login(userData){
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  }

  function logout(){
    setUser(null);
    localStorage.removeItem("user");
  }


  return(
    <AuthContext.Provider
    value={{
      user,
      login,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );


}