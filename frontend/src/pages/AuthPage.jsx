import { useState } from "react";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { IoBookOutline } from "react-icons/io5";
import { MdOutlineEmail } from "react-icons/md";
import { FiKey } from "react-icons/fi";
import { RxPerson } from "react-icons/rx";
import './auth-page.css'
import { useNavigate } from "react-router-dom";
import axios from 'axios'

function AuthPage() {

  const [isLoading, setIsLoading] = useState(false);

  const [succesMessage, setSuccesMessage] = useState('');
  const [seeMessage, setSeeMessage] = useState(false);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm_password, setConfirmPassword] = useState("");

  const [errorName, setErrorName] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const [signToggle, setSignToggle] = useState(true);

  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  function handleLogin() {
    const fakeUser = {
      id: 1,
      name: "abdo",
      role: "student",
    };

    login(fakeUser);


    navigate("/dashboard");
  }
  async function handleRegister() {
    let response
    try {

      setIsLoading(true);

      response = await axios.post('http://127.0.0.1:8000/api/auth/register/', {
        username,
        email,
        password,
        confirm_password
      });

      setSuccesMessage(response.data.message);
      setSeeMessage(true);
      setTimeout(() => {
        setSeeMessage(false);
      }, 3000);

      setIsLoading(false);

      // alert(response.data.message);
      // login(response);
      // navigate("/dashboard");
    } catch (error) {
      const errors = error.response?.data;

      if (errors.username) {
        setErrorMessage(errors.username[0]);
        setErrorName('username');
      } else if (errors.email) {
        setErrorMessage(errors.email[0]);
        setErrorName('email');
      } else if (errors.password) {
        setErrorMessage(errors.password[0]);
        setErrorName('password');
      } else if (errors.confirm_password) {
        setErrorMessage(errors.confirm_password[0]);
        setErrorName('confirmpassword');
      }
    }


  }


  return (
    <>
      <div className="container">
        <div className="title">
          <span><IoBookOutline /></span>
          <h2>EduForge</h2>
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
                <label
                  className="name-label"

                >Username</label>
                <div className="svg-name-relative">
                  <input
                    className="name-input"
                    type="text"
                    placeholder="Abdo42"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                  <p className="error">{errorName === 'username' && errorMessage}</p>
                  <RxPerson />
                </div>
              </div>

              <div className="email-container">
                <label className="email-label">Email address</label>
                <div className="svg-email-relative">
                  <input
                    className="email-input"
                    type="email"
                    name="email"
                    placeholder="your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                  <p className="error">{errorName === 'email' && errorMessage}</p>
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
                  <input
                    className="pass-input"
                    type="password"
                    placeholder="your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <p className="error">{errorName === 'password' && errorMessage}</p>
                  <FiKey />
                </div>
              </div>
              <div className="password-container">
                <label className="pass-label">Confirm password</label>
                <div className="svg-pass-relative">
                  <input
                    className="pass-input"
                    type="password"
                    placeholder="confirm your password"
                    value={confirm_password}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                  <p className="error">{errorName === 'confirmpassword' && errorMessage}</p>
                  <FiKey />
                </div>
              </div>

            </form>

          }

          <div className="btns-container">
            {signToggle ? <button
              className="sign-in-up-btn"
              onClick={handleLogin}
            >Sign in to EduForge
            </button> :
              <button
                disabled={isLoading}
                className="sign-in-up-btn"
                onClick={handleRegister}
              >
                <span className="succes">{seeMessage && succesMessage}</span>
                Create your account
              </button>}

          </div>
        </div>
      </div>
    </>
  )
}

export default AuthPage