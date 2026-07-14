import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

function ProtectedRoute({ children }) {

    const { /*user*/  accessToken , loading} = useContext(AuthContext);
    if(loading){
        return <h1>Loading...</h1>
    }

    if(!accessToken){
        return <Navigate to="/" />;
    }

    return children;
}

export default ProtectedRoute;