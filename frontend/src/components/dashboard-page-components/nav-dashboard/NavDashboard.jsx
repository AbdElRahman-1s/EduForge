
import { IoIosNotificationsOutline } from 'react-icons/io';
import { MdOutlineSecurity } from "react-icons/md";
import './nav-dashboard.css'

function NavDashboard({ switchSidebar , selected}) {
  return (
    <nav>
      <div className={switchSidebar ? 'nav-dashboard-big' :
        'nav-dashboard-sm'
      }>
        <div className='flex-nav-dashboard'>
          <h2>{selected.charAt(0).toUpperCase() + selected.slice(1)}</h2>
          <div className='right-nav-dashboard'>
            <div className="noti-dash">
              <span className="noti-icon">
                <IoIosNotificationsOutline />
              </span>
              <span className="noti-num">
                4
              </span>
            </div>

            <div className='secure-admin'>
              <MdOutlineSecurity />
              <span>Admin</span>
            </div>


          </div>
        </div>
      </div>
    </nav>
  )
}

export default NavDashboard