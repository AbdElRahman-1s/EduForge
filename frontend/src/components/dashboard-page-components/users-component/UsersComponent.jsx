import { useContext, useEffect, useState } from "react";


import { MdOutlineRemoveRedEye } from "react-icons/md";
import { CiSearch } from "react-icons/ci";



import './users-component.css';
import { AuthContext } from "../../../context/AuthContext";
import axios from "axios";




function UsersComponent() {

  const {accessToken} = useContext(AuthContext);


  const [users,setUsers] = useState([]);

  useEffect(() => {
    async function fetchStudents(){
      try{

        const response = await axios.get('/api/instructor/students/',
          {
            headers:{
              Authorization: `Bearer ${accessToken}`
            }
          }
        )

        console.log(response.data);
        setUsers(response.data);


      }catch(error){
        console.log(error.response?.data);
      }
    }

    fetchStudents();

  },[accessToken])




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
            </div>

            <div className="right-head">
              ACTIONS
            </div>


          </div>


          {
            users.map((userDetails) => {
              return (
                <div key={userDetails.username} className="users-user-details">
                  <div className="users-left-details">
                    <div className="users-letter-div">
                      {userDetails.username?.[0]?.toUpperCase()}
                    </div>
                    <div className="users-user-name-email">
                      <span className="users-name-users">{userDetails.username}</span>
                      <span className="users-email-users">{userDetails.email}</span>
                    </div>

                  </div>

                  <div className="users-mid-details">
                    <span className="users-joined-users">{userDetails.joined_at}</span>
                    <span className="users-courses-users">{userDetails.course_count}</span>
                  </div>


                  <div className="users-right-details">
                    <span title="Student Profile" className="users-eye-span">
                      <MdOutlineRemoveRedEye />
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