
import { useContext, useEffect, useState } from "react";
import axios from "axios";
import { AuthContext } from "../../../context/AuthContext";





import './recent-activity.css';

function RecentActivity() {

  const {accessToken} = useContext(AuthContext);

  const [recentCourses,setRecentCourses] = useState([]);
  const [recentSignups,setRecentSignups] = useState([]);





useEffect(() => {

async function fetchDashboard(){
 try{
   const response = await axios.get('/api/instructor/dashboard/',
    {
      headers:{
        Authorization: `Bearer ${accessToken}`,
      }
    }
  )

  console.log(response.data);
  setRecentCourses(response.data.recent_courses);
  setRecentSignups(response.data.recent_signups);
 }catch(error){
  console.log(error.response?.data);
 }
  
}
fetchDashboard();

},[accessToken]);




  return (
    <section>

      <div className='container-dashboard-recent'>
        <div className='recent-grid'>



          <div className="recent-courses-grid">
            <div className='title-courses'>
              <h4>Recent Courses</h4>
              <span>Last 30 days</span>
            </div>
            {recentCourses.map((recentCourse) => {
              return (
                <div key={recentCourse.id} className='course-div'>
                  <div className='img-title-inst'>
                    <div className='img-div'>
                      <img className='img-course'
                        src={`http://127.0.0.1:8000${recentCourse.thumbnail}`}
                        alt="course image"
                      />
                    </div>
                    <div className='title-inst'>
                      <p>{recentCourse.title}</p>
                    </div>
                  </div>

                  <div className='price-students-div'>

                    <span className='price-course'>{recentCourse.student_count}</span>

                    <span className='students-course'>Students</span>

                  </div>

                </div>
              )
            })

            }

          </div>


          <div className="recent-signups-grid">
            <div className='title-signups'>
              <h4>Recent Signups</h4>
              <span>Last 30 days</span>
            </div>

            {
              recentSignups.map((recentSignup) => {
                return (
                  <div key={recentSignup.enrollment_id} className="signups-div">
                    <div className='left-signup'>
                      <div className='f-letter-div'>
                         {recentSignup.username?.[0]?.toUpperCase()}
                      </div>
                      <div className='name-email-div'>
                        <span className='name-signup'>
                          {recentSignup.username}
                        </span>
                        <span className='email-signup'>
                          {recentSignup.email}
                        </span>
                      </div>
                    </div>

                    <div className={recentSignup.status === 'active' ? 'status-div-active' : 'status-div-suspended'}>
                      {recentSignup.status}
                    </div>
                  </div>
                )
              })
            }


          </div>

        </div>
      </div>


    </section>
  )
}

export default RecentActivity