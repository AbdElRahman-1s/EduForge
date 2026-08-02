import { useContext, useEffect, useState } from "react";
import { LuPenLine } from "react-icons/lu";
import { FaRegTrashCan } from "react-icons/fa6";



import { IoMdClose } from "react-icons/io";
import { AiOutlinePicture } from "react-icons/ai";
import { LiaFileVideo } from "react-icons/lia";

import './courses-actions.css';
import axios from "axios";
import { AuthContext } from "../../../context/AuthContext";



// const recentCoursesActions = [
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'New',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Hot',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.frfr'
//   },



// ]


function CoursesActions() {


  const { accessToken } = useContext(AuthContext);


  const [isEdit, setISEdit] = useState(false);
  const [selectedCourseEdit, setSelectedCourseEdit] = useState(null);

  const [categorySelectEdit, setCategorySelectEdit] = useState("");
  const [levelSelectEdit, setLevelSelectEdit] = useState("");
  const [mineCourseResults, setmineCourseResults] = useState({
    results: [],
  });

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [published, setPublished] = useState(false);
  const [disabledToggle, setDisabledToggle] = useState(false);


  useEffect(() => {

    async function fetchInsmineCourseResults() {

      try {
        const response = await axios.get('/api/courses/mine/',
          {
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          }
        );

        setmineCourseResults(response.data);
        console.log(response.data);
      } catch (error) {
        console.log(error);

      }


    }

    fetchInsmineCourseResults();

  }, [accessToken]);


  async function patchEditCourse() {

    try {

      setDisabledToggle(true);

      const response = await axios.patch(`/api/courses/${selectedCourseEdit.id}/`,
        {
          title,
          description,
          published
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          }
        }
      )

      console.log(response.data);

      setmineCourseResults((prev) => ({
        ...prev,
        results: prev.results.map((course) =>
          course.id === response.data.id ? response.data : course
        ),
      }));

    } catch (error) {
      console.log(error.response.status);
      console.log(error.response.data);

    } finally {
      setDisabledToggle(false);
    }


  }


  async function deleteCourse(id) {

    try {

      setDisabledToggle(true);

      const response = await axios.delete(`/api/courses/${id}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          }
        }
      );

      console.log(response.status);

      setmineCourseResults((prev) => ({
        ...prev,
        results: prev.results.filter((course) => course.id !== id),
      }));

    } catch (error) {
      console.log(error);

    } finally {
      setDisabledToggle(false);
    }

  }



  function handleEdit(course) {
    setSelectedCourseEdit(course);
    setPublished(course.published);
    setISEdit(true);
  }


  const categoryClasses = {
    bestseller: "best-category",
    hot: "hot-category",
    new: "new-category",
    none: "none-category"
  };

  function selectClassCategory(categoryName) {
    return categoryClasses[categoryName] || "none-category";
  }


  useEffect(() => {
  if (selectedCourseEdit) {
    setDescription(selectedCourseEdit.description);
    setTitle(selectedCourseEdit.title);
  }
}, [selectedCourseEdit]);



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
            mineCourseResults.results.map((mineCourseResult) => {
              return (
                <div key={mineCourseResult.id} className="course-details">
                  <div className="left-details-dash">
                    <img src='https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format' alt="" />
                    <div className='title-inst-course'>
                      <p className="title-course">{mineCourseResult.title}</p>
                      <span className="inst-course">{mineCourseResult.instructor.username}</span>
                    </div>
                  </div>
                  <div className='mid-details-dash'>
                    <span className={selectClassCategory(mineCourseResult.badge)}>{mineCourseResult.badge}</span>
                    <span className="hide-students">48,200</span>
                    <span className="price-course-api">${mineCourseResult.price}</span>
                  </div>
                  <div className="right-details-dash">
                    <span
                      onClick={() => { handleEdit(mineCourseResult) }}
                      className="edit-course">
                      <LuPenLine />
                    </span>

                    <span
                      disabled={disabledToggle}
                      onClick={() => deleteCourse(mineCourseResult.id)}
                      className="delete-course"><FaRegTrashCan /></span>
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
                      Value={title}
                      onChange={(e) => setTitle(e.target.value)}
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
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
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
                  <p className="note">note:you need to update every thing to edit course correctly</p>
                  <div className="btns-div">
                    <button
                      className="cancel-btn"
                      onClick={() => { setISEdit(false) }}>
                      Cancel
                    </button>
                    <button
                      disabled={disabledToggle}
                      onClick={patchEditCourse}
                      className="add-new-btn">
                      Edit Course
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