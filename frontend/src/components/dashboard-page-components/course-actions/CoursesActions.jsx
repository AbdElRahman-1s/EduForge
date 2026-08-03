import { useContext, useEffect, useState } from "react";
import { LuPenLine } from "react-icons/lu";
import { FaRegTrashCan } from "react-icons/fa6";



import { IoMdClose } from "react-icons/io";
import { AiOutlinePicture } from "react-icons/ai";
import { LiaFileVideo } from "react-icons/lia";

import './courses-actions.css';
import axios from "axios";
import { AuthContext } from "../../../context/AuthContext";



// const recentCoursesActions = [
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'New',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Hot',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.'
//   },
//   {
//     img: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=340&fit=crop&auto=format',
//     title: 'Complete React & Next.js Development',
//     instructor: 'Marcus Reid',
//     category: 'Bestseller',
//     students: '48,200',
//     price: 89,
//     courseCategory: 'development',
//     courseLevel: 'beginner',
//     courseDesc: 'Master React 18, Next.js 14, TypeScript, and modern full-stack patterns with real-world projects.frfr'
//   },



// ]


function CoursesActions() {


  const { accessToken } = useContext(AuthContext);


  const [isEdit, setISEdit] = useState(false);
  const [selectedCourseEdit, setSelectedCourseEdit] = useState(null);

  const [categorySelectEdit, setCategorySelectEdit] = useState("");
  const [levelSelectEdit, setLevelSelectEdit] = useState("");
  const [mineCourseResults, setmineCourseResults] = useState({
    results: [],
  });
  const [fetchCategories, setFetchCategories] = useState([]);
  const [fetchTopics, setFetchTopics] = useState([]);
  const [thumbnail, setThumbnail] = useState(null);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [badgeSelect, setBadgeSelect] = useState("");

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [published, setPublished] = useState(false);
  const [disabledToggle, setDisabledToggle] = useState(false);
  const [price, setPrice] = useState(0);
  const [errorMessage, setErrorMessage] = useState('hide-warning');



  useEffect(() => {

    async function fetchInsmineCourseResults() {

      try {
        const response = await axios.get('/api/courses/mine/',
          {
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          }
        );

        setmineCourseResults(response.data);
        console.log(response.data);
      } catch (error) {
        console.log(error);
        
      }


    }

    fetchInsmineCourseResults();

  }, [accessToken]);


  async function patchEditCourse() {

    try {

      setDisabledToggle(true);



      const formData = new FormData();


      formData.append("title", title);
      selectedTopics.forEach((topicId) => {
        formData.append("topics", Number(topicId));
      });
      formData.append("description", description);
      formData.append("level", levelSelectEdit);
      formData.append("category", categorySelectEdit);
      formData.append("price", price);
      formData.append("badge", badgeSelect);

      if (thumbnail) {
        formData.append("thumbnail", thumbnail);
      }
      formData.append("published", published);




      const response = await axios.patch(`/api/courses/${selectedCourseEdit.id}/`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          }
        }
      )

      console.log(response.data);

      setmineCourseResults((prev) => ({
        ...prev,
        results: prev.results.map((course) =>
          course.id === response.data.id ? response.data : course
        ),
      }));

    } catch (error) {
      console.log(error.response.status);
      console.log(error.response.data);
      if (error.response?.data) {
        setErrorMessage("show-warning");
      }

    } finally {
      setDisabledToggle(false);
    }


  }


  async function deleteCourse(id) {

    try {

      setDisabledToggle(true);

      const response = await axios.delete(`/api/courses/${id}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          }
        }
      );

      console.log(response.status);

      setmineCourseResults((prev) => ({
        ...prev,
        results: prev.results.filter((course) => course.id !== id),
      }));

    } catch (error) {
      console.log(error);

    } finally {
      setDisabledToggle(false);
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






  async function handleEdit(course) {

    try {

      const response = await axios.get(`/api/courses/${course.id}/`);
      setSelectedCourseEdit(response.data);
      console.log(response.data);


      const data = response.data;

      setSelectedCourseEdit(data);

      setPublished(data.published);
      setDescription(data.description);
      setTitle(data.title);
      setPrice(data.price);
      setLevelSelectEdit(data.level);
      setBadgeSelect(data.badge);

      setSelectedTopics(
        fetchTopics
          .filter((fetchTopic) =>
            data.topics.includes(fetchTopic.name)
          )
          .map((fetchTopic) => fetchTopic.id)
      );

      setCategorySelectEdit(
        fetchCategories.find(
          (category) => category.name === data.category
        )?.id
      );

      setISEdit(true);


    } catch (error) {
      console.log(error);
    }



  }








  function handleTopicClick(id) {
    if (selectedTopics.includes(id)) {
      setSelectedTopics(
        selectedTopics.filter((topicId) => topicId !== id)
      );
    } else {
      setSelectedTopics([...selectedTopics, id]);
    }
  }



  const categoryClasses = {
    bestseller: "best-category",
    hot: "hot-category",
    new: "new-category",
    none: "none-category"
  };

  function selectClassCategory(categoryName) {
    return categoryClasses[categoryName] || "none-category";
  }




  return (
    <section>
      <div className="container-courses-actions">
        <div className="grid-actions">

          <div className='table-header'>
            <div className="left-header">
              COURSE
            </div>
            <div className="mid-header">
              <span className="category-course">CATEGORY</span>
              <span className="students-course">STUDENTS</span>
              <span className="price-course">PRICE</span>
            </div>
            <div className="right-header">
              ACTIONS
            </div>
          </div>

          {
            mineCourseResults.results.map((mineCourseResult) => {
              return (
                <div key={mineCourseResult.id} className="course-details">
                  <div className="left-details-dash">
                    <img src={mineCourseResult.thumbnail} alt="" />
                    <div className='title-inst-course'>
                      <p className="title-course">{mineCourseResult.title}</p>
                      <span className="inst-course">{mineCourseResult.instructor?.username}</span>
                    </div>
                  </div>
                  <div className='mid-details-dash'>
                    <span className={selectClassCategory(mineCourseResult.badge)}>{mineCourseResult.badge}</span>
                    <span className="hide-students">48,200</span>
                    <span className="price-course-api">${mineCourseResult.price}</span>
                  </div>
                  <div className="right-details-dash">
                    <span
                      onClick={() => { handleEdit(mineCourseResult) }}
                      className="edit-course">
                      <LuPenLine />
                    </span>

                    <span
                      disabled={disabledToggle}
                      onClick={() => deleteCourse(mineCourseResult.id)}
                      className="delete-course"><FaRegTrashCan /></span>
                  </div>
                </div>
              )
            })
          }

          {
            isEdit &&
            <div className="modal-overlay">
              <div className="modal">
                <div className="modal-content">
                  <div className="top-desc">
                    <h2>Edit Course</h2>
                    <span
                      onClick={() => { setISEdit(false) }}
                    ><IoMdClose /></span>
                  </div>
                  <div className="title-div">
                    <label>Course Title</label>
                    <input
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
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
                      value={categorySelectEdit}
                      onChange={(e) => setCategorySelectEdit(e.target.value)}
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
                      value={levelSelectEdit}
                      onChange={(e) => setLevelSelectEdit(e.target.value)}
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
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      type="number" placeholder="89" />
                  </div>

                  <div className="desc-div">
                    <label>Description</label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      className="area-desc"
                      placeholder="Brief course description"></textarea>
                  </div>
                  <div className="big-div-uploads">
                    <label
                      htmlFor="thumbnail"
                      className="thumb-div">
                      <AiOutlinePicture />
                      {
                        thumbnail
                          ? thumbnail.name
                          : selectedCourseEdit?.thumbnail?.split("/").pop()
                      }
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

                  <p
                    className={errorMessage}
                  >⚠️ All fields are required. Please do not leave any field empty.</p>

                  <div className="btns-div">
                    <button
                      className="cancel-btn"
                      onClick={() => { setISEdit(false) }}>
                      Cancel
                    </button>
                    <button
                      disabled={disabledToggle}
                      onClick={patchEditCourse}
                      className="add-new-btn">
                      Edit Course
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

export default CoursesActions