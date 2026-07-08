import { IoBookOutline } from "react-icons/io5";
import { MdOutlineEmail } from "react-icons/md";
import { FiKey } from "react-icons/fi";
import './auth-page.css'

function AuthPage() {
  return (
    <>
      <div className="container">
        <div className="title">
          <IoBookOutline />
          <h2>Learnify</h2>
        </div>
        <div className="sign-in-out">
          <span>Sign In</span>
          <span>Create Account</span>
        </div>
        <div>
          <form action="">
            <label>Email address</label>
            <div>
              <input type="email" name="email" placeholder="Email address" />
              <MdOutlineEmail />
            </div>
            <div className="job-type">
              <label>
                <input type="radio" name="job" value="student" />
                Student
              </label>

              <label>
                <input type="radio" name="job" value="teacher" />
                Teacher
              </label>
            </div>
            <label>Password</label>
            <div>
              <input type="password" />
              <FiKey />
            </div>
          </form>
          <div>
          <button>Sign in to learnify</button>
          <div>
            <span>or continue with</span>
          </div>
          <button>Continue with Google</button>
          </div>
        </div>
      </div>
    </>
  )
}

export default AuthPage