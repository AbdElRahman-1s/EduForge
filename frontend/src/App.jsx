import { Routes, Route } from "react-router-dom";
import AuthPage from './pages/AuthPage'
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoutes";
import './App.css'
import ProfilePage from "./pages/ProfilePage";
import CoursesPage from "./pages/CoursesPage";

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
 </Routes>
 </>
  )
}

export default App
