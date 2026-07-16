import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { Link } from "react-router-dom";

function Dashboard() {

    const { user } = useContext(AuthContext);

   

 if(!user) return <h2></h2>
 

    return (
        <>
            <h1>Dashboard</h1>
            <div>
                <h1>Hello {user.username}</h1>
                <h3>your role is {user.role}</h3>
            </div>
            <Link to="/profile">Profile</Link>
        </>

    )

}

export default Dashboard;