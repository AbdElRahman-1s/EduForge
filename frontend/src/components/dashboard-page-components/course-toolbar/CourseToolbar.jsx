import { useState } from "react";
import { FiPlusCircle } from "react-icons/fi";
import { IoIosSearch , IoMdClose} from "react-icons/io";
import { AiOutlinePicture } from "react-icons/ai";
import { LiaFileVideo } from "react-icons/lia";

import './course-toolbar.css';
function CourseToolbar() {

  const [addCourse, setAddCourse] = useState(false);
  const [categorySelect, setCategorySelect] = useState("");
  const [levelSelect, setLevelSelect] = useState("");

  return (

    <section>
      <div className="container-dashboard">
        <div className="search-addbtn-div">
          <div className="search-div">
            <IoIosSearch />
            <input type="text" placeholder="Search courses..." />
          </div>
          <button
            onClick={() => { setAddCourse(true) }}
            className="add-course-btn">
            <FiPlusCircle /> Add Course
          </button>

          {
            addCourse &&
            <div className="modal-overlay">
              <div className="modal">
                <div className="modal-content">
                  <div className="top-desc">
                    <h2>Add New Course</h2>
                    <span
                    onClick={() => { setAddCourse(false) }}
                    ><IoMdClose /></span>
                  </div>
                  <div className="title-div">
                    <label>Course Title</label>
                    <input type="text" placeholder="Complete React Bootcamp" />
                  </div>
                  <div className="ins-div">
                    <label>Instructor Name</label>
                    <input type="text" placeholder="Marcus Reid" />
                  </div>
                  <div className="category-level-div">
                    <select
                      value={categorySelect}
                      onChange={(e) => setCategorySelect(e.target.value)}
                      className="category-select">
                      <option value="">Choose Category</option>
                      <option value="development">Development</option>
                      <option value="data science">Data Science</option>
                      <option value="design">Design</option>
                      <option value="business">Business</option>
                      <option value="Marketing">Marketing</option>
                    </select>
                    <select
                      value={levelSelect}
                      onChange={(e) => setLevelSelect(e.target.value)}
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
                    <input type="number" placeholder="89" />
                  </div>

                  <div className="desc-div">
                    <label>Description</label>
                    <textarea
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
                     onClick={() => { setAddCourse(false) }}>
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

export default CourseToolbar