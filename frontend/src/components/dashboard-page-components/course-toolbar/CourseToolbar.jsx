import { FiPlusCircle } from "react-icons/fi";
import { IoIosSearch } from "react-icons/io";


import './course-toolbar.css';
function CourseToolbar() {
  return (
    
    <section>
      <div className="container-dashboard">
        <div className="search-addbtn-div">
          <div className="search-div">
            <IoIosSearch />
            <input type="text" placeholder="Search courses..." />
            </div>
            <button className="add-course-btn">
              <FiPlusCircle /> Add Course
              </button>
        </div>
      </div>
    </section>
  )
}

export default CourseToolbar