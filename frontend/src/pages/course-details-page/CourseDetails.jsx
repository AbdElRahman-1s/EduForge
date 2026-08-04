import { Link } from "react-router-dom";

import Navbar from "../../components/Navbar"


import { FaPlay } from "react-icons/fa";
import { FaArrowLeft, FaStar } from "react-icons/fa6";
import { RxPeople } from "react-icons/rx";
import { MdOutlineAccessTime } from "react-icons/md";
import { FiBookOpen } from "react-icons/fi";
import { LuCircleCheckBig } from "react-icons/lu";



import './course-details.css';

import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import CurriculumAccordion from "../../components/Course-Curriculum-component/CurriculumAccordion";





function CourseDetails() {
  const [courseDetails, setCourseDetails] = useState();
  const [isEnrolled, setIsEnrolled] = useState(false);




  const { id } = useParams();

  useEffect(() => {
    async function fetchCourseDetails() {
      try {
        const response = await axios.get(` /api/courses/${id}/`);


        setCourseDetails(response.data);
        console.log(response.data);

      } catch (error) {
        console.log(error);
      }

    }

    fetchCourseDetails();


  }, [id])



  const categoryClasses = {
    bestseller: "best-category",
    hot: "hot-category",
    new: "new-category",
    none: "none-category"
  };

  function selectClassCategory(categoryName) {
    return categoryClasses[categoryName] || "none-category";
  }





  if (!courseDetails) return <h1>loading</h1>


  return (
    <>
      <Navbar />

      <div className="course-details-page-content">
        <div className="details-container">
          <div className="details-flex">
            <div className="left-details">
              <Link to="/courses">
                <div className="back-div">
                  <FaArrowLeft />
                  Back to courses
                </div>
              </Link>
              <div className="type-category-div">
                <span className="type-details">{courseDetails.category}</span>
                .
                <span className={selectClassCategory(courseDetails.badge)}>{courseDetails.badge}</span>
              </div>
              <h1 className="title-details">{courseDetails.title}</h1>

              <p className="desc-details">{courseDetails.description}</p>
              <div className="more-details">
                <div className="rating-div">
                  <span className="stars-rating">
                    <FaStar />
                    <FaStar />
                    <FaStar />
                    <FaStar />
                  </span>
                  <div className="num-rating">
                    <span className="num-star">4.8</span>
                    <span className="num-people">(31.6k)</span>
                  </div>
                </div>
                <div className="students-details">
                  <span><RxPeople /></span>
                  <span>31,600 students</span>
                </div>
                <div className="time-details">
                  <span><MdOutlineAccessTime /></span>
                  <span>58h total</span>
                </div>
                <div className="lessons-details">
                  <span><FiBookOpen /></span>
                  <span>130 lessons</span>
                </div>
              </div>

              <div className="ins-details">
                <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=64&h=64&fit=crop&auto=format" alt="" />
                <span className="ins-word">Instructor:</span>
                <span>{courseDetails.instructor.username}</span>
              </div>
            </div>

            <div className="right-details">
              <div className="card-details">
                <div className="img-details">
                  <img src={courseDetails.thumbnail} alt="" />
                  <span><FaPlay /></span>
                </div>
                <div className="bot-content">
                  <h2 className="price-details">${courseDetails.price}</h2>
                  <div className="btns-details">
                    <button className="purple-btn">Enroll Now - ${courseDetails.price}</button>
                    <button className="white-btn">Try free preview</button>
                  </div>

                  <div className="more-benefits">
                    <div>
                      <LuCircleCheckBig />
                      <span>Full lifetime access
                      </span>
                    </div>
                    <div>
                      <LuCircleCheckBig />
                      <span>Certificate of completion

                      </span>
                    </div>
                    <div>
                      <LuCircleCheckBig />
                      <span>Downloadable resources

                      </span>
                    </div>
                    <div>
                      <LuCircleCheckBig />
                      <span>Access on mobile & desktop
                      </span>
                    </div>
                  </div>

                </div>

              </div>
            </div>


          </div>
        </div>
      </div>

      <div className="course-details-">
        <div className="details-bot-container">
          <div className="details-bot-flex">

            <div className="things-in-course">
              <span>{courseDetails.topics[0] || 'Topic 1'}</span>
              <span>{courseDetails.topics[1] || 'Topic 2'}</span>
              <span>{courseDetails.topics[2] || 'Topic 3'}</span>
              <span>{courseDetails.topics[3] || 'Topic 4'}</span>
            </div>

            <div className="bot-before-enroll-div">
              <h3>Course Curriculum</h3>
              {
                isEnrolled ? <CurriculumAccordion />
                  : (
                    <div className="Curriculum-div">
                      <span>Curriculum details coming soon.</span>
                    </div>
                  )
              }

            </div>


          </div>
        </div>
      </div>

    </>
  )
}

export default CourseDetails