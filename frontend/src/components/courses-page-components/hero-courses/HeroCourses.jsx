import { IoBookOutline } from 'react-icons/io5';
import { CiSearch } from "react-icons/ci";
import './hero-courses.css';

function HeroCourses() {
  return (
    <section>

      <div className="contain">

        <div className='background'>
          <div className='left-words'>
            <h1>
              Expand your skills.
              Advance your career.
            </h1>
            <p>Expert-led courses on development, design, business, and more.</p>
            <div className='search-box'>
              <CiSearch />
              <input type="text" placeholder='Search courses...'/>
              <button>Search</button>
            </div>

          </div>
          <div className='right-img'>
            <IoBookOutline />
          </div>

        </div>




      </div>




    </section>
  )
}

export default HeroCourses