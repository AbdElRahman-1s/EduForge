import { useState } from "react";
import { IoBookOutline } from "react-icons/io5";
import { MdOutlineEmail } from "react-icons/md";
import { FiKey } from "react-icons/fi";
import { FcGoogle } from "react-icons/fc";
import { RxPerson } from "react-icons/rx";
import './auth-page.css'

function AuthPage() {

  const [signToggle, setSignToggle] = useState(true);


  return (
    <>
      <div className="container">
        <div className="title">
          <span><IoBookOutline /></span>
          <h2>Learnify</h2>
        </div>
        <div className="sign-in-up">
          <button onClick={() => setSignToggle(!signToggle)} className={signToggle ? `sign-active` : 'sign-no-active'}>Sign In</button>
          <button onClick={() => setSignToggle(!signToggle)} className={!signToggle ? `sign-active` : 'sign-no-active'} >Create Account</button>
        </div>
        <div>
          {signToggle &&
            <form className="form">
              <div className="email-container">
                <label className="email-label">Email address</label>
                <div className="svg-email-relative">
                  <input className="email-input" type="email" name="email" placeholder="your email address" />
                  <MdOutlineEmail />
                </div>
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
              <div className="password-container">
                <label className="pass-label">Password</label>
                <div className="svg-pass-relative">
                  <input className="pass-input" type="password" placeholder="your password" />
                  <FiKey />
                </div>
              </div>

            </form>
          }
          {!signToggle &&
            <form className="form">
              <div className="name-container">
                <label className="name-label">Full name</label>
                <div className="svg-name-relative">
                  <input className="name-input" type="text" placeholder="Abdo Adel"/>
                  <RxPerson />
                </div>
              </div>

              <div className="email-container">
                <label className="email-label">Email address</label>
                <div className="svg-email-relative">
                  <input className="email-input" type="email" name="email" placeholder="your email address" />
                  <MdOutlineEmail />
                </div>
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
              <div className="password-container">
                <label className="pass-label">Password</label>
                <div className="svg-pass-relative">
                  <input className="pass-input" type="password" placeholder="your password" />
                  <FiKey />
                </div>
              </div>

            </form>

          }

          <div className="btns-container">
            <button className="sign-in-up-btn">{signToggle ? 'Sign in to learnify' : 'Create your account'}</button>

            <button className="with-google-btn">
              <FcGoogle /> Continue with Google
            </button>

          </div>
        </div>
      </div>
    </>
  )
}

export default AuthPage