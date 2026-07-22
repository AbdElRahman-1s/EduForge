

import { LuPenLine } from "react-icons/lu";
import { FaRegTrashCan } from "react-icons/fa6";

import './courses-actions.css';



const recentCoursesActions = [
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: '$89',
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: '$89',
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Hot',
    students: '48,200',
    price: '$89',
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: '$89',
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'New',
    students: '48,200',
    price: '$89',
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: '$89',
  }
 
]


function CoursesActions() {


const categoryClasses = {
  Bestseller: "best-category",
  Hot: "hot-category",
  New: "new-category",
};

function selectClassCategory(categoryName) {
  return categoryClasses[categoryName] || "new-category";
}




  return (
    <section>
      <div className="container-courses-actions">
          <div className="grid-actions">

            <div className='table-header'>
                <div className="left-header">
                  COURSE
                </div>
                <div className="mid-header">
                  <span className="category-course">CATEGORY</span>
                  <span className="students-course">STUDENTS</span>
                  <span className="price-course">PRICE</span>
                </div>
                <div className="right-header">
                  ACTIONS
                </div>
            </div>

            {
              recentCoursesActions.map((courseAction,i) => {
                return(
                <div key={i} className="course-details">
                  <div className="left-details">
                  <img src={courseAction.img} alt="" />
                  <div className='title-inst-course'>
                    <p className="title-course">{courseAction.title}</p>
                    <span className="inst-course">{courseAction.instructor}</span>
                  </div>
                  </div>
                  <div className='mid-details'>
                    <span className={selectClassCategory(courseAction.category)}>{courseAction.category}</span>
                    <span className="hide-students">{courseAction.students}</span>
                    <span>{courseAction.price}</span>
                  </div>
                  <div className="right-details">
                    <span className="edit-course"><LuPenLine /></span>
                    <span className="delete-course"><FaRegTrashCan /></span>
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

export default CoursesActions