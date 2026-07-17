import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { IoBookOutline } from "react-icons/io5";
import { IoIosNotificationsOutline, IoIosArrowDown,  IoIosArrowUp} from "react-icons/io";
import { FiLogOut } from "react-icons/fi";
import { CiSettings } from "react-icons/ci";

import './navbar.css';

function Navbar() {

  const [showProfileList , setShowProfileList] = useState(false);


  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/auth')
  }



  return (
    <>
      <nav>

        <div className="nav-div">

          <div className="left-section">
            <div className="title">
              <span><IoBookOutline /></span>
              <h2>EduForge</h2>
            </div>
          </div>

          <div className="middle-section">
            <span>Browse</span>
            <span>My Courses</span>

          </div>


          <div className="right-section">

            <div className="notification-div">
              <span className="notification-icon">
                <IoIosNotificationsOutline />
              </span>
              <span className="notification-num">
                4
              </span>
            </div>

            <div 
            className="profile"
            onClick={() => {setShowProfileList(!showProfileList)}}
            >
              <img src="https://media.istockphoto.com/id/2151669184/vector/vector-flat-illustration-in-grayscale-avatar-user-profile-person-icon-gender-neutral.jpg?s=612x612&w=0&k=20&c=UEa7oHoOL30ynvmJzSCIPrwwopJdfqzBs0q69ezQoM8=" alt="" />
              {!showProfileList ? <IoIosArrowDown/> : <IoIosArrowUp />  }
            </div>

            <div className={showProfileList ? "more-info" : "hide-info"}>

              <div className="move-to">
                <CiSettings />
                <span>Move to</span>
              </div>
              <div className="logout" onClick={handleLogout}>
                <FiLogOut />
                <span>
                  Sign out
                </span>
              </div>

            </div>

          </div>




        </div>

      </nav>

    </>
  )
}

export default Navbar