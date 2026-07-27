import { FaPlay } from "react-icons/fa";
import { FaStar } from "react-icons/fa6";
import { IoTimeOutline, IoBookOutline } from "react-icons/io5";
import './course-section.css';


const detailsCourseCard = [
  {
    absolute: 'Bestseller',
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    category: 'Development',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    rating: '4.9',
    numrating: '(48.2k)',
    duration: '62',
    lessons: '148',
    level: 'Beginner',
    price: '$89',
    id: crypto.randomUUID()
  },
  {
    absolute: 'Bestseller',
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    category: 'Development',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    rating: '4.9(48.2k)',
    duration: '62',
    lessons: '148',
    level: 'Beginner',
    price: '$89',
    id: crypto.randomUUID()
  },
  {
    absolute: 'Bestseller',
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    category: 'Development',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    rating: '4.9(48.2k)',
    duration: '62',
    lessons: '148',
    level: 'Beginner',
    price: '$89',
    id: crypto.randomUUID()
  },
  {
    absolute: 'Bestseller',
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    category: 'Development',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    rating: '4.9(48.2k)',
    duration: '62',
    lessons: '148',
    level: 'Beginner',
    price: '$89',
    id: crypto.randomUUID()
  },
  {
    absolute: 'Bestseller',
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    category: 'Development',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    rating: '4.9(48.2k)',
    duration: '62',
    lessons: '148',
    level: 'Beginner',
    price: '$89',
    id: crypto.randomUUID()
  },
  {
    absolute: 'Bestseller',
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    category: 'Development',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    rating: '4.9(48.2k)',
    duration: '62',
    lessons: '148',
    level: 'Beginner',
    price: '$89',
    id: crypto.randomUUID()
  }
]

function CourseSection() {
  return (
    <section>

      <div className='contain'>
        <h3 className='num-courses'>All Courses <span>(6)</span></h3>

        <div className='course-cards'>

          {
            detailsCourseCard.map((deatailsCard) => {
              return (

                <div key={deatailsCard.id} className='course-card'>

                  <div className="imgs-course">
                    <img src={deatailsCard.img} alt="big course image" />
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


                    <div className="creator">{deatailsCard.instructor}</div>

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

              )
            })
          }


        </div>



      </div>


    </section>
  )
}

export default CourseSection