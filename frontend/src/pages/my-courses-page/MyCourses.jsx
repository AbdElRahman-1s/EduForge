import Navbar from '../../components/Navbar';
import { Link } from 'react-router-dom';
import { FaPlay } from "react-icons/fa";
import { FaStar } from "react-icons/fa6";
import { IoTimeOutline, IoBookOutline } from "react-icons/io5";


import './my-courses.css';
import { useContext, useEffect, useState } from 'react';
import axios from 'axios';
import { AuthContext } from '../../context/AuthContext';






function MyCourses() {

  const {accessToken} = useContext(AuthContext);

const [myCourses,setMyCourses] = useState({
  results:[],
})




  useEffect(() => {

    async function fetchMyCourses() {

      try {

        const response = await axios.get(`/api/enrollments/mine/`,
          {
            headers:{
              Authorization: `Bearer ${accessToken}`,
            }
          }
        )

        console.log(response.data);
        setMyCourses(response.data);

      } catch (error) {
        console.log(error.response.data);

      }


    }

    fetchMyCourses();

  },[accessToken])





  return (
    <>
      <Navbar />

      <div className="body-my-courses">
        <div className='contain'>
          <div className='my-learning'>
            <h1>My Learning</h1>
            <p>
              Continue where you left off
            </p>
          </div>

          <div className='course-cards'>

            {
              myCourses.results.map((deatailsCard) => {
                return (
                  <Link
                  key={deatailsCard.id}
                  className="link"
                  to={`/course/details/${deatailsCard.id}`}>
                  <div  className='course-card'>

                    <div className="imgs-course">
                      <img src={deatailsCard.thumbnail} alt="big course image" />
                      <div className="big-play-abs">

                        <div className="play-div">
                          <FaPlay />

                        </div>

                      </div>

                      <div className="abs-catch">{deatailsCard.absolute}</div>

                      <div className="big-abs-bar">
                        <div className="back-bar">
                          <div className="front-bar">

                          </div>
                        </div>

                        <div className="text-bar">68% complete</div>
                      </div>

                    </div>



                    <div className="details-course">

                      <div className="category-div">{deatailsCard.category}</div>


                      <h3 className="title">{deatailsCard.title}</h3>


                      <div className="creator">{deatailsCard.instructor.username}</div>

                      <div className="rating-div">
                        <FaStar />
                        <FaStar />
                        <FaStar />
                        <FaStar />
                        <span className="star-num">4.9</span>
                        <span className="num-rating">(48.2k)</span>
                      </div>


                      <div className="course-stats">
                        <span>
                          <IoTimeOutline />
                          62
                        </span>
                        <span>
                          <IoBookOutline />
                          148 Lessons
                        </span>
                        <span>
                          Beginner
                        </span>
                      </div>


                      <div className="course-action">

                        <div className="price-div">
                          <span className="price">
                            $89
                          </span>

                        </div>
                        <button className="continue-btn">
                          Continue
                        </button>

                      </div>




                    </div>



                  </div>
                  </Link>
                )
              })
            }


          </div>


        </div>
      </div>

    </>
  )
}

export default MyCourses