import { FaPlay } from "react-icons/fa";
import { FaStar } from "react-icons/fa6";
import { IoTimeOutline, IoBookOutline } from "react-icons/io5";
import './course-section.css';

import axios from "axios";
import { useEffect, useState } from "react";
import { Link } from 'react-router-dom';


// const detailsCourseCard = [
//   {
//     absolute: 'Bestseller',
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     category: 'Development',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     rating: '4.9',
//     numrating: '(48.2k)',
//     duration: '62',
//     lessons: '148',
//     level: 'Beginner',
//     price: '$89',
//     id: crypto.randomUUID()
//   },
//   {
//     absolute: 'Bestseller',
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     category: 'Development',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     rating: '4.9(48.2k)',
//     duration: '62',
//     lessons: '148',
//     level: 'Beginner',
//     price: '$89',
//     id: crypto.randomUUID()
//   },
//   {
//     absolute: 'Bestseller',
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     category: 'Development',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     rating: '4.9(48.2k)',
//     duration: '62',
//     lessons: '148',
//     level: 'Beginner',
//     price: '$89',
//     id: crypto.randomUUID()
//   },
//   {
//     absolute: 'Bestseller',
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     category: 'Development',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     rating: '4.9(48.2k)',
//     duration: '62',
//     lessons: '148',
//     level: 'Beginner',
//     price: '$89',
//     id: crypto.randomUUID()
//   },
//   {
//     absolute: 'Bestseller',
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     category: 'Development',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     rating: '4.9(48.2k)',
//     duration: '62',
//     lessons: '148',
//     level: 'Beginner',
//     price: '$89',
//     id: crypto.randomUUID()
//   },
//   {
//     absolute: 'Bestseller',
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     category: 'Development',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     rating: '4.9(48.2k)',
//     duration: '62',
//     lessons: '148',
//     level: 'Beginner',
//     price: '$89',
//     id: crypto.randomUUID()
//   }
// ]




function CourseSection() {


  const [courses, setCourses] = useState([]);
  const [next, setNext] = useState(null);
  const [previous, setPrevious] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);





  useEffect(() => {

    
  const fetchCourses = async (page = 1) => {
    try {
      const response = await axios.get(`/api/courses/?page=${page}`);

      setCourses(response.data.results);
      setNext(response.data.next);
      setPrevious(response.data.previous);
      setCurrentPage(page);
      setTotalPages(Math.ceil(response.data.count / 10)); // 10 = Page Size

      console.log(response.data);

    } catch (error) {
      console.log(error);
    }
  };


    fetchCourses(currentPage);

  }, [currentPage]);


  const pages = [];

  for (let i = 1; i <= totalPages; i++) {
    pages.push(i);
  }



  return (
    <section>

      <div className='contain'>
        <h3 className='num-courses'>All Courses <span>(6)</span></h3>

        <div className='course-cards'>

          {
            courses.map((courseCard) => {
              return (
                <Link
                  key={courseCard.id}
                  className="link"
                  to={`/course/details/${courseCard.id}`}>
                  <div key={courseCard.id} className='course-card'>

                    <div className="imgs-course">
                      <img src='https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format' alt="big course image" />
                      <div className="big-play-abs">

                        <div className="play-div">
                          <FaPlay />

                        </div>

                      </div>

                      <div className="abs-catch">Bestseller</div>

                      <div className="big-abs-bar">
                        <div className="back-bar">
                          <div className="front-bar">

                          </div>
                        </div>

                        <div className="text-bar">68% complete</div>
                      </div>

                    </div>



                    <div className="details-course">

                      <div className="category-div">Development</div>


                      <h3 className="title">{courseCard.title}</h3>


                      <div className="creator">{courseCard.instructor.username}</div>

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
                        <button className="enroll-btn">
                          Enroll
                        </button>

                      </div>




                    </div>



                  </div>
                </Link>
              )
            })
          }


        </div>


        <div className="next-prev-div">
          <button
            disabled={!previous}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Previous
          </button>

          <div className="num-switch-pages-div">
            {
              pages.slice(0, 10).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={currentPage === page ? "active-num" : "off-num"}
                >
                  {page}
                </button>
              ))
            }
          </div>

          <button
            disabled={!next}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </button>
        </div>



      </div>


    </section>
  )
}

export default CourseSection