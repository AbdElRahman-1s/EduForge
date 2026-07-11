import { Routes, Route } from "react-router-dom";
import AuthPage from './pages/AuthPage'
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoutes";
import './App.css'

function App() {

  return (
 <Routes>
  <Route path="/" element={<AuthPage />}/>
     <Route
        path="/dashboard"
        element={
            <ProtectedRoute>
                <Dashboard/>
            </ProtectedRoute>
        }
    />
 </Routes>
  )
}

export default App
