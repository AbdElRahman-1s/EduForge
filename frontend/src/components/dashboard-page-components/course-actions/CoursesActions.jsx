import { useState } from "react";
import { LuPenLine } from "react-icons/lu";
import { FaRegTrashCan } from "react-icons/fa6";



import { IoMdClose } from "react-icons/io";
import { AiOutlinePicture } from "react-icons/ai";
import { LiaFileVideo } from "react-icons/lia";

import './courses-actions.css';



const recentCoursesActions = [
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: 89,
    courseCategory: 'development',
    courseLevel: 'beginner',
    courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: 89,
    courseCategory: 'development',
    courseLevel: 'beginner',
    courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'New',
    students: '48,200',
    price: 89,
    courseCategory: 'development',
    courseLevel: 'beginner',
    courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: 89,
    courseCategory: 'development',
    courseLevel: 'beginner',
    courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Hot',
    students: '48,200',
    price: 89,
    courseCategory: 'development',
    courseLevel: 'beginner',
    courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
  },
  {
    img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
    title: 'Complete React & Next.js Development',
    instructor: 'Marcus Reid',
    category: 'Bestseller',
    students: '48,200',
    price: 89,
    courseCategory: 'development',
    courseLevel: 'beginner',
    courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.frfr'
  },

 

]


function CoursesActions() {

  const [isEdit, setISEdit] = useState(false);
  const [selectedCourseEdit, setSelectedCourseEdit] = useState(null);

  const [categorySelectEdit, setCategorySelectEdit] = useState("");
  const [levelSelectEdit, setLevelSelectEdit] = useState("");

  function handleEdit(course) {
    setSelectedCourseEdit(course);
    setISEdit(true);
  }


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
            recentCoursesActions.map((courseAction, i) => {
              return (
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
                    <span>${courseAction.price}</span>
                  </div>
                  <div className="right-details">
                    <span
                      onClick={() => { handleEdit(courseAction) }}
                      className="edit-course">
                      <LuPenLine />
                    </span>

                    <span className="delete-course"><FaRegTrashCan /></span>
                  </div>
                </div>
              )
            })
          }

          {
            isEdit &&
            <div className="modal-overlay">
              <div className="modal">
                <div className="modal-content">
                  <div className="top-desc">
                    <h2>Edit Course</h2>
                    <span
                      onClick={() => { setISEdit(false) }}
                    ><IoMdClose /></span>
                  </div>
                  <div className="title-div">
                    <label>Course Title</label>
                    <input
                     defaultValue={selectedCourseEdit?.title}
                     type="text" placeholder="Complete React Bootcamp" />
                  </div>
                  <div className="ins-div">
                    <label>Instructor Name</label>
                    <input
                    defaultValue={selectedCourseEdit?.instructor} 
                    type="text" placeholder="Marcus Reid" />
                  </div>
                  <div className="category-level-div">
                    <select
                      defaultValue={selectedCourseEdit?.courseCategory}
                      onChange={(e) => setCategorySelectEdit(e.target.value)}
                      className="category-select">
                      <option value="">Choose Category</option>
                      <option value="development">Development</option>
                      <option value="data science">Data Science</option>
                      <option value="design">Design</option>
                      <option value="business">Business</option>
                      <option value="Marketing">Marketing</option>
                    </select>
                    <select
                      defaultValue={selectedCourseEdit?.courseLevel}
                      onChange={(e) => setLevelSelectEdit(e.target.value)}
                      className="level-select">
                      <option value="">Choose Level</option>
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                      <option value="all levels">All levels</option>
                    </select>
                  </div>

                  <div className="price-div">
                    <label>Price(USD)</label>
                    <input
                    defaultValue={selectedCourseEdit?.price}
                     type="number" placeholder="89" />
                  </div>

                  <div className="desc-div">
                    <label>Description</label>
                    <textarea
                      defaultValue={selectedCourseEdit?.courseDesc}
                      className="area-desc"
                      placeholder="Brief course description"></textarea>
                  </div>
                  <div className="big-div-uploads">
                    <div className="thumb-div">
                      <AiOutlinePicture /> Upload Thumbnail
                    </div>
                    <div className="video-div">
                      <LiaFileVideo /> Upload Video/URL
                    </div>
                  </div>

                  <div className="btns-div">
                    <button
                      className="cancel-btn"
                      onClick={() => { setISEdit(false) }}>
                      Cancel
                    </button>
                    <button className="add-new-btn">
                      Add Course
                    </button>
                  </div>
                </div>
              </div>
            </div>
          }



        </div>
      </div>
    </section>
  )
}

export default CoursesActions