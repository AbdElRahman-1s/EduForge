import { Routes, Route } from "react-router-dom";
import AuthPage from './pages/auth-page/AuthPage';
import Dashboard from "./pages/dashboard-page/Dashboard";
import ProtectedRoute from "./components/ProtectedRoutes";
import './App.css'
import ProfilePage from "./pages/ProfilePage";
import CoursesPage from "./pages/courses-page/CoursesPage";
import CourseDetails from "./pages/course-details-page/CourseDetails";
import MyCourses from "./pages/my-courses-page/MyCourses";

function App() {

  return (
<>

 <Routes>
  <Route path="/auth" element={<AuthPage />}/>
     <Route
        path="/dashboard"
        element={
            <ProtectedRoute>
                <Dashboard/>
            </ProtectedRoute>
        }
    />
     <Route
        path="/profile"
        element={
            <ProtectedRoute>
                <ProfilePage/>
            </ProtectedRoute>
        }
    />

    <Route path='/courses' element={<CoursesPage />} />
    <Route path="/course/details" element={<CourseDetails />} />

    <Route path="/my/courses" element={<MyCourses />} />
 </Routes>
 </>
  )
}

export default App
