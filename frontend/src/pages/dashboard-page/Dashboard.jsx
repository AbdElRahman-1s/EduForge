// import { useContext } from "react";
// import { AuthContext } from "../context/AuthContext";
// import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import NavDashboard from "../../components/dashboard-page-components/nav-dashboard/NavDashboard";
import Sidebar from "../../components/dashboard-page-components/sidebar/Sidebar";

import './dashboard.css'
import DashboardStats from "../../components/dashboard-page-components/dashboard-stats/DashboardStats";
import RecentActivity from "../../components/dashboard-page-components/recent-activity/RecentActivity";
import CourseToolbar from "../../components/dashboard-page-components/course-toolbar/CourseToolbar";
import CoursesActions from "../../components/dashboard-page-components/course-actions/CoursesActions";
import UsersComponent from "../../components/dashboard-page-components/users-component/UsersComponent";
import ManageCurriculum from "../../components/dashboard-page-components/manage-curriculum/ManageCurriculum";
function Dashboard() {

    //     const { user } = useContext(AuthContext);

    const [switchSidebar, setSwitchSidebar] = useState(true);
    const [selected, setSelected] = useState(() => {
        return localStorage.getItem("selected") || "dashboard";
    });

    

    useEffect(() => {
        localStorage.setItem("selected", selected);
    }, [selected]);


    //  if(!user) return <h2></h2>


    return (
        <>
            <Sidebar
                switchSidebar={switchSidebar}
                setSwitchSidebar={setSwitchSidebar}
                selected={selected}
                setSelected={setSelected}
            />
            <div className={switchSidebar ? "dashboard-container-big" : "dashboard-container-sm"}>
                <NavDashboard
                    switchSidebar={switchSidebar}
                    selected={selected}
                />

                <div className="dashboard-body">
                    {
                        selected === 'dashboard' &&
                        <>
                            <DashboardStats />
                            <RecentActivity />
                        </>
                    }
                    {
                        selected === 'courses' &&
                        <>
                            <CourseToolbar />
                            <CoursesActions
                                setSelected={setSelected}
                                
                            />
                        </>
                    }
                    {
                        selected === 'users' &&
                        <>
                            <UsersComponent />
                        </>
                    }
                    {
                        selected === 'manage Curriculum' &&
                        <>
                            <ManageCurriculum
                                setSelected={setSelected}
                                
                            />
                        </>
                    }

                </div>
            </div>
        </>

    )

}

export default Dashboard;