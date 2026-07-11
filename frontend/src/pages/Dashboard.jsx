import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";


function Dashboard() {

    const { user ,logout} = useContext(AuthContext);

    function handelLogout(){
        logout();
    }

    return (
        <>
            <h1>Dashboard</h1>
            <div>
                <h1>Hello {user.name}</h1>
                <button onClick={handelLogout}>Logout</button>
            </div>
        </>

    )

}

export default Dashboard;