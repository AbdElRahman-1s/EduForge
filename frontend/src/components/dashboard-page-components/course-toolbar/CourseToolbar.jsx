import { useContext, useState, useEffect } from "react";
import { FiPlusCircle } from "react-icons/fi";
import { IoIosSearch, IoMdClose } from "react-icons/io";
import { AiOutlinePicture } from "react-icons/ai";
import { LiaFileVideo } from "react-icons/lia";

import './course-toolbar.css';
import axios from "axios";
import { AuthContext } from "../../../context/AuthContext";
function CourseToolbar() {




  const [addCourse, setAddCourse] = useState(false);
  const [addedCourseDetails, setAddedCourseDetails] = useState({});
  const [disabeldEffect, setDisabeldEffect] = useState(false);
  const [fetchCategories, setFetchCategories] = useState([]);
  const [fetchTopics, setFetchTopics] = useState([]);
  const [errorMessage, setErrorMessage] = useState("note-p-hide");





  const [title, setTitle] = useState("");
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [description, setDescription] = useState("");
  const [categorySelect, setCategorySelect] = useState("");
  const [levelSelect, setLevelSelect] = useState("");
  const [price, setPrice] = useState("");
  const [published, setPublished] = useState(false);
  const [badgeSelect, setBadgeSelect] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);




  const { accessToken } = useContext(AuthContext);

  async function postAddCourse() {
    try {

      setDisabeldEffect(true);

      const formData = new FormData();


      formData.append("title", title);
      selectedTopics.forEach((topicId) => {
        formData.append("topics", Number(topicId));
      });
      formData.append("description", description);
      formData.append("level", levelSelect);
      formData.append("category", categorySelect);
      formData.append("price", price);
      formData.append("badge", badgeSelect);
      formData.append("thumbnail", thumbnail);
      formData.append("published", published);



      const response = await axios.post('/api/courses/',
        formData,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`
          },
          withCredentials: true,

        }
      );


      setAddedCourseDetails(response.data);
      console.log(response.data);


    } catch (error) {
      console.log(error.response?.data);
      if (error.response?.data) {
        setErrorMessage("note-p");
      }
    } finally {
      setDisabeldEffect(false);
    }

  }


  useEffect(() => {
    async function fetchCategories() {
      const response = await axios.get(' api/categories/',
        {
          headers: {
            Authorization: `Bearer ${accessToken}`
          }
        }
      );

      setFetchCategories(response.data.results);
      console.log(response.data);
    }
    async function fetchTopics() {
      const response = await axios.get(' api/topics/',
        {
          headers: {
            Authorization: `Bearer ${accessToken}`
          }
        }
      );

      setFetchTopics(response.data.results);
      console.log(response.data);

    }
    fetchCategories();
    fetchTopics();
  }, [accessToken]);



  function handleTopicClick(id) {
    if (selectedTopics.includes(id)) {
      setSelectedTopics(
        selectedTopics.filter((topicId) => topicId !== id)
      );
    } else {
      setSelectedTopics([...selectedTopics, id]);
    }
  }








  return (

    <section>
      <div className="container-dashboard">
        <div className="search-addbtn-div">
          <div className="search-div">
            <IoIosSearch />
            <input type="text" placeholder="Search courses..." />
          </div>
          <button
            onClick={() => { setAddCourse(true) }}
            className="add-course-btn">
            <FiPlusCircle /> Add Course
          </button>

          {
            addCourse &&
            <div className="modal-overlay">
              <div className="modal">
                <div className="modal-content">
                  <div className="top-desc">
                    <h2>Add New Course</h2>
                    <span
                      onClick={() => { setAddCourse(false) }}
                    ><IoMdClose /></span>
                  </div>
                  <div className="title-div">
                    <label>Course Title</label>
                    <input
                      onChange={(e) => { setTitle(e.target.value) }}
                      type="text" placeholder="Complete React Bootcamp" />
                  </div>
                  <div className="topics-div">
                    <div className="topics-container">
                      {fetchTopics.map((topic) => (
                        <button
                          key={topic.id}
                          type="button"
                          className={`topic-btn ${selectedTopics.includes(topic.id) ? "active" : ""
                            }`}
                          onClick={() => handleTopicClick(topic.id)}
                        >
                          {topic.name}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="category-level-div">
                    <select
                      value={categorySelect}
                      onChange={(e) => setCategorySelect(e.target.value)}
                      className="category-select"
                    >
                      <option value="">Choose Category</option>
                      {fetchCategories.map((category) => (
                        <option key={category.id}
                          value={category.id}
                        >
                          {category.name}
                        </option>
                      ))}
                    </select>
                    <select
                      value={levelSelect}
                      onChange={(e) => setLevelSelect(e.target.value)}
                      className="level-select">
                      <option value="">Choose Level</option>
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                      <option value="all levels">All levels</option>
                    </select>
                  </div>
                  <div>
                    <select
                      value={badgeSelect}
                      onChange={(e) => setBadgeSelect(e.target.value)}
                      className="badge-select">
                      <option value="">Choose Badge</option>
                      <option value="none">None</option>
                      <option value="new">New</option>
                      <option value="hot">Hot</option>
                      <option value="bestseller">Bestseller</option>
                    </select>
                  </div>

                  <div className="price-div">
                    <label>Price(USD)</label>
                    <input
                      onChange={(e) => { setPrice(e.target.value) }}
                      type="number" placeholder="89" />
                  </div>

                  <div className="desc-div">
                    <label>Description</label>
                    <textarea
                      onChange={(e) => { setDescription(e.target.value) }}
                      className="area-desc"
                      placeholder="Brief course description"></textarea>
                  </div>
                  <div className="big-div-uploads">
                    <label htmlFor="thumbnail" className="thumb-div">
                      <AiOutlinePicture />
                      {thumbnail ? thumbnail.name : "Upload Thumbnail"}
                    </label>
                    <input
                      id="thumbnail"
                      type="file"
                      accept="image/*"
                      hidden
                      onChange={(e) => {
                        const file = e.target.files[0];
                        setThumbnail(file);
                      }}
                    />
                    <div className="video-div">
                      <LiaFileVideo /> Upload Video/URL
                    </div>
                  </div>

                  <div className="publish-div">
                    <label>
                      <input
                        type="radio"
                        name="published"
                        checked={published === false}
                        onChange={() => setPublished(false)}
                      />
                      Draft
                    </label>
                    <label>
                      <input
                        type="radio"
                        name="published"
                        checked={published === true}
                        onChange={() => setPublished(true)}
                      />
                      Published
                    </label>
                  </div>
                  <p className={errorMessage}>
                    ⚠️Note:
                      Please fill everything correctly before adding a new course.
                    </p>
                  <div className="btns-div">
                    <button
                      className="cancel-btn"
                      onClick={() => { setAddCourse(false) }}>
                      Cancel
                    </button>
                    <button
                      disabled={disabeldEffect}
                      onClick={postAddCourse}
                      className="add-new-btn">
                      Add Course
                    </button>
                  </div>
                </div>
              </div>
            </div>
          }
        </div>
      </div>
    </section>
  )
}

export default CourseToolbar