import { IoBookOutline } from "react-icons/io5";
import { LuLayoutDashboard, LuUserCheck } from "react-icons/lu";
import { TiFolderOpen } from "react-icons/ti";
import { MdOutlineSettings, MdOutlineMenu } from "react-icons/md";
import { GoSignOut } from "react-icons/go";

import './sidebar.css';
import './sidebar-sm.css'


function Sidebar({ switchSidebar, setSwitchSidebar , selected , setSelected}) {



  


  return (
    <aside>
      {
        switchSidebar && <div className="side-content">
          <div className="flex-side">
            <div className="logo-title-menu">
              <div className="logo-title">
                <span className="logo-side"><IoBookOutline /></span>
                <span className="title-side">EduForge</span>
              </div>
              <MdOutlineMenu onClick={() => setSwitchSidebar(!switchSidebar)} />
            </div>

            <div className="admin-panel">
              ADMIN PANEL
            </div>

            <div className={selected === 'dashboard' ? 'selected' : "dashboard-side"}
              onClick={() => { setSelected('dashboard') }}
            >
              <LuLayoutDashboard />
              <span>Dashboard</span>
            </div>
            <div className={selected === 'courses' ? 'selected' : "courses-side"}
              onClick={() => { setSelected('courses') }}
            >
              <TiFolderOpen />
              <span>Courses</span>

            </div>

            <div
              className={selected === 'users' ? 'selected' : "users-side"}
              onClick={() => { setSelected('users') }}
            >
              <LuUserCheck />
              <span>Users</span>
            </div>


          </div>

          <div className="logout-setting">

            <div className="setting">
              <MdOutlineSettings />
              <span>Settings</span>
            </div>

            <div className="logout-side">
              <GoSignOut />
              <span>Sign out</span>
            </div>

          </div>

        </div>}

      {!switchSidebar && <div className="side-content-sm">
        <div className="flex-side-sm">
          <div className="logo-title-menu-sm">
            <div className="logo-title-sm">
              <span className="logo-side-sm">
                <IoBookOutline />
              </span>
            </div>
            <span className="span-menu"><MdOutlineMenu onClick={() => { setSwitchSidebar(!switchSidebar) }} /></span>
          </div>

          <div className={selected === 'dashboard' ? 'selected-sm' : "dashboard-side-sm"}
              onClick={() => { setSelected('dashboard') }}>
            <LuLayoutDashboard />
          </div>
          <div className={selected === 'courses' ? 'selected-sm' : "courses-side-sm"}
              onClick={() => { setSelected('courses') }}>
            <TiFolderOpen />
          </div>

          <div className={selected === 'users' ? 'selected-sm' : "users-side-sm"}
              onClick={() => { setSelected('users') }}>
            <LuUserCheck />
          </div>


        </div>

        <div className="logout-setting-sm">

          <div className="setting-sm">
            <MdOutlineSettings />
          </div>

          <div className="logout-side-sm">
            <GoSignOut />
          </div>

        </div>

      </div>}
    </aside>
  )
}

export default Sidebar