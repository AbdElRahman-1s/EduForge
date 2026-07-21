import './courses-page.css';
import HeroCourses from '../components/HeroCourses';
import Categories from '../components/Categories';
import Statistics from '../components/Statistics';
import CourseSection from '../components/CourseSection';
import Navbar from '../components/Navbar';
function CoursesPage() {
  return (

    <>
      <Navbar />

      <div className='courses-body'>

        <HeroCourses />
        <Categories />
        <Statistics />
        <CourseSection />
      </div>
    </>
  )
}

export default CoursesPage