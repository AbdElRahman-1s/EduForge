import './courses-page.css';
import HeroCourses from '../components/HeroCourses';
import Categories from '../components/Categories';
import Statistics from '../components/Statistics';
import CourseSection from '../components/CourseSection';
function CoursesPage() {
  return (

    <>


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