
const recentCourses = [
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    price: '$89',
    students: '48.2k students'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    price: '$89',
    students: '48.2k students'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    price: '$89',
    students: '48.2k students'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    price: '$89',
    students: '48.2k students'
  }
]

const resentSignups = [
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    status: 'active'
  },
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    status: 'active'
  },
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    status: 'active'
  },
  {
    fLetter: 'A',
    name: 'Alex Johnson',
    email: 'alex@example.com',
    status: 'suspended'
  },
]



import './recent-activity.css';

function RecentActivity() {
  return (
    <section>

      <div className='container-dashboard-recent'>
        <div className='recent-grid'>



          <div className="recent-courses-grid">
            <div className='title-courses'>
              <h4>Recent Courses</h4>
              <span>Last 30 days</span>
            </div>
            {recentCourses.map((recentCourse, i) => {
              return (
                <div key={i} className='course-div'>
                  <div className='img-title-inst'>
                    <div className='img-div'>
                      <img className='img-course'
                        src={recentCourse.img}
                        alt="course image"
                      />
                    </div>
                    <div className='title-inst'>
                      <p>{recentCourse.title}</p>
                      <span>{recentCourse.instructor}</span>
                    </div>
                  </div>

                  <div className='price-students-div'>

                    <span className='price-course'>{recentCourse.price}</span>

                    <span className='students-course'>{recentCourse.students}</span>

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
              resentSignups.map((recentSignup,i) => {
                return (
                  <div key={i} className="signups-div">
                    <div className='left-signup'>
                      <div className='f-letter-div'>
                        {recentSignup.fLetter}
                      </div>
                      <div className='name-email-div'>
                        <span className='name-signup'>
                          {recentSignup.name}
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