


import { FaRegTimesCircle, FaRegCheckCircle } from "react-icons/fa";
import { MdOutlineRemoveRedEye } from "react-icons/md";
import { CiSearch } from "react-icons/ci";



import './users-component.css';
import { useState } from "react";




const usersDetails = [
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    joined: 'Jan 12, 2025',
    courses: '3',
    status: 'active',
     id: crypto.randomUUID()
  },
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    joined: 'Jan 12, 2025',
    courses: '3',
    status: 'active',
    id: crypto.randomUUID()
  },
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    joined: 'Jan 12, 2025',
    courses: '3',
    status: 'active',
     id: crypto.randomUUID()
  },
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    joined: 'Jan 12, 2025',
    courses: '3',
    status: 'suspended',
     id: crypto.randomUUID()
  },
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    joined: 'Jan 12, 2025',
    courses: '3',
    status: 'active',
     id: crypto.randomUUID()
  },

]



function UsersComponent() {

  const [users,setUsers] = useState(usersDetails);



  function toggleStatus(id) {
  setUsers(
    users.map((user) =>
      user.id === id
        ? {
            ...user,
            status: user.status === "active" ? "suspended" : "active",
          }
        : user
    )
  );
}


  return (
    <section>

      <div className='users-top-part'>
        <div className="search-div">
          <CiSearch />
          <input type="text" placeholder="Search users…" />
        </div>
      </div>

      <div className="users-bottom-part">
        <div className="users-grid-users">

          <div className="users-users-head">
            <div className="left-header">
              STUDENTS
            </div>

            <div className="mid-head">
              <span className="joined-users">JOINED</span>
              <span className="course-users">COURSES</span>
              <span className="status-users">STATUS</span>
            </div>

            <div className="right-head">
              ACTIONS
            </div>


          </div>


          {
            users.map((userDetails) => {
              return (
                <div key={userDetails.id} className="users-user-details">
                  <div className="users-left-details">
                    <div className="users-letter-div">
                      {userDetails.fLetter}
                    </div>
                    <div className="users-user-name-email">
                      <span className="users-name-users">{userDetails.name}</span>
                      <span className="users-email-users">{userDetails.email}</span>
                    </div>

                  </div>

                  <div className="users-mid-details">
                    <span className="users-joined-users">{userDetails.joined}</span>
                    <span className="users-courses-users">{userDetails.courses}</span>
                    <span
                      className={userDetails.status === 'active' ? 'status-users-active' : 'status-users-suspended'}>
                      {userDetails.status}</span>
                  </div>


                  <div className="users-right-details">
                    <span className="users-eye-span">
                      <MdOutlineRemoveRedEye />
                    </span>
                    <span  
                    className={userDetails.status === 'active'? "x-span" : "y-span"}
                    onClick={() => {toggleStatus(userDetails.id)}}
                    >
                      {userDetails.status === 'active' ? <FaRegTimesCircle /> : <FaRegCheckCircle />}
                    </span>
                  </div>



                </div>
              )
            })
          }


        </div>
      </div>


    </section>
  )
}

export default UsersComponent