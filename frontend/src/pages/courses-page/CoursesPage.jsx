import './courses-page.css';
import HeroCourses from '../../components/courses-page-components/hero-courses/HeroCourses';
import Categories from '../../components/courses-page-components/categories-courses/Categories';
import Statistics from '../../components/courses-page-components/statistics-courses/Statistics';
import CourseSection from '../../components/courses-page-components/course-section-courses/CourseSection';
import Navbar from '../../components/Navbar';
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