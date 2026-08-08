import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../../context/AuthContext';
import { minutesToSeconds, secondsToTime } from '../../../utills/time.js';
import {
  Plus, GripVertical, PlayCircle, Lock,
  Pencil, Trash2, Check
} from 'lucide-react';

import axios from 'axios';
import { Reorder } from 'framer-motion';
import './manage-curriculum.css';

function ManageCurriculum({ setSelected }) {

  const { accessToken } = useContext(AuthContext);

  const [courseDetails, setCourseDetails] = useState(null);
  const [addSection, setAddSection] = useState(false);
  const [sectionTitle, setSectionTitle] = useState("");
  const [editSection, setEditSection] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [addLesson, setAddLesson] = useState(false);
  const [lessonTitle, setLessonTitle] = useState("");
  const [lessonDuration, setLessonDuration] = useState(0);
  const [free, setFree] = useState(false);
  const [lessonTitleEdit, setLessonTitleEdit] = useState("");
  const [lessonDurationEdit, setLessonDurationEdit] = useState(0);
  const [lockedEdit, setLockedEdit] = useState(true);
  const [editLesson, setEditLesson] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [editVideoUrl, setEditVideoUrl] = useState("");

  const [selectedSectionId, setSelectedSectionId] = useState(null);


  const courseId = localStorage.getItem("selectedCourseId");


  const [sections, setSections] = useState([]);



  const handleLessonReorder = (sectionId, newLessons) => {
    setSections(prev =>
      prev.map(sec => sec.id === sectionId ? { ...sec, lessons: newLessons } : sec)
    );
  };


  useEffect(() => {
    async function fetchCourse() {
      try {
        const response = await axios.get(`/api/courses/${courseId}/`);

        setCourseDetails(response.data);
        setSections(response.data.sections);
      } catch (error) {
        console.log(error);
      }
    }

    if (courseId) {
      fetchCourse();
    }
  }, [courseId]);

  async function postAddSection() {
    try {
      const response = await axios.post(`/api/courses/${courseId}/sections/`,
        {
          title: sectionTitle
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          }
        }
      )

      console.log(response.data);


    } catch (error) {
      console.log(error.data);

    }
  }



  async function postAddLesson(sectionId) {
    try {

      const response = await axios.post(`/api/sections/${sectionId}/lessons/`,
        {
          title: lessonTitle,
          video: videoUrl,
          duration_seconds: minutesToSeconds(lessonDuration),
          free: free
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          }
        }
      );

      console.log(response.data);


    } catch (error) {
      console.log(error.response?.data);

    }
  }





  if (!courseDetails) {
    return <h2>Loading...</h2>;
  }

  return (
    <>
      <button
        className="back-btn"
        onClick={() => setSelected("courses")}
      >
        ← Back to Courses
      </button>

      <div className="manage-curriculum">

        <div className="course-header">

          <div className="course-info">

            <img
              src={courseDetails.thumbnail}
              alt={courseDetails.title}
            />

            <div className="course-text">
              <h3>{courseDetails.title}</h3>
              <span>{courseDetails.instructor.username}</span>
            </div>

          </div>

          <div className="course-actions">
            <button className="preview-btn">
              Preview Course
            </button>

            <button
              onClick={() => setAddSection(true)}
              className="add-section-btn">
              + Add Section
            </button>
          </div>

        </div>

        <div className='drag-drop-div'>
          !  Drag and drop sections or lessons to recorder them.
        </div>

        <Reorder.Group
          axis="y"
          values={sections}
          onReorder={setSections}
          className='sections-lessons-container'
          style={{ listStyle: 'none', padding: 0 }}
        >
          {sections.map((section) => (
            <Reorder.Item key={section.id} value={section} className="section-card">

              {/* هيدر السكشن */}
              <div className="section-header-card">
                <div className="section-title-wrapper">
                  <GripVertical className="drag-icon" size={18} />
                  <span className="section-title">{section.title}</span>
                  <button
                    onClick={() => {
                      setEditSection(true)
                      setEditTitle(section.title)
                    }}
                    className="icon-edit-title"><Pencil size={14} /></button>
                </div>

                <div className="section-actions-btns">
                  <button
                    onClick={() => {
                      setSelectedSectionId(section.id);
                      setAddLesson(true)
                    }}
                    className="btn-add-lesson"><Plus size={15} /> Add Lesson</button>
                  <button
                    onClick={() => {
                      setEditSection(true)
                      setEditTitle(section.title)
                    }}
                    className="btn-sec-edit"><Pencil size={14} /> Edit</button>
                  <button className="btn-sec-delete"><Trash2 size={14} /> Delete</button>
                </div>
              </div>

              {/* 🟢 تصحيح: غيرنا الـ div إلى Reorder.Group */}
              {section.lessons.length > 0 && (
                <Reorder.Group
                  axis="y"
                  values={section.lessons}
                  onReorder={(newLessons) => handleLessonReorder(section.id, newLessons)}
                  className="lessons-wrapper"
                  style={{ listStyle: 'none', padding: 0 }}
                >
                  {section.lessons.map((lesson) => (
                    <Reorder.Item key={lesson.id} value={lesson} className="lesson-item">
                      <div className="lesson-info">
                        <GripVertical className="drag-icon" size={16} />
                        {lesson.free ? (
                          <PlayCircle size={16} className="lesson-type-icon" />
                        ) : (
                          <Lock size={16} className="lesson-type-icon" />
                        )}
                        <span className="lesson-title">{lesson.title}</span>
                      </div>

                      <div className="lesson-details">
                        <span className="lesson-duration">{secondsToTime(lesson.duration_seconds)}</span>
                        <span className={`badge ${(lesson.free)? 'free' : 'locked'}`}>
                          {(lesson.free)? 'Free' : 'Locked'}
                        </span>
                        <button
                          onClick={() => {
                            setLessonTitleEdit(lesson.title);
                            const numDuration = Number(lesson.duration);
                            setLessonDurationEdit(numDuration);
                            setLockedEdit(lesson.locked);
                            setEditLesson(true);
                          }}
                          className="icon-action-btn"><Pencil size={14} /></button>
                        <button className="icon-action-btn delete"><Trash2 size={14} /></button>
                      </div>
                    </Reorder.Item>
                  ))}
                </Reorder.Group>
              )}

            </Reorder.Item>
          ))}
        </Reorder.Group>

        {/* 🟢 تصحيح: طلعنا زرار الحفظ خارج الـ Reorder.Group */}
        <div className="save-order-bar">
          <button className="save-order-btn">
            <Check size={16} /> Save Order
          </button>
          <span className="last-saved-text">Last saved: 2 minutes ago</span>
        </div>

      </div>


      {/*Modals*/}

      {addSection && (
        <div className="modal-overlay-section" onClick={() => setAddSection(false)}>
          <div
            className="modal-content-section"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Add New Section</h3>

            <input
              type="text"
              placeholder="Enter section title..."
              value={sectionTitle}
              onChange={(e) => setSectionTitle(e.target.value)}
            />

            <div className="modal-buttons-section">
              <button
                className="btn-cancel-section"
                onClick={() => setAddSection(false)}
              >
                Cancel
              </button>

              <button
                onClick={() => postAddSection()}
                className="btn-save-section">
                Add
              </button>
            </div>
          </div>
        </div>
      )}

      {editSection && (
        <div className="modal-overlay-section" onClick={() => setEditSection(false)}>
          <div
            className="modal-content-section"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Edit Section</h3>

            <input
              type="text"
              placeholder="Enter section title..."
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
            />

            <div className="modal-buttons-section">
              <button
                className="btn-cancel-section"
                onClick={() => setEditSection(false)}
              >
                Cancel
              </button>

              <button className="btn-save-section">
                Edit
              </button>
            </div>
          </div>
        </div>
      )}

      {addLesson && (
        <div className="modal-overlay-lesson">
          <div className="modal-lesson">
            <div className="modal-content-lesson">

              <div className="top-desc-lesson">
                <h2>Add New Lesson</h2>

                <span
                  onClick={() => setAddLesson(false)}
                  className="close-btn-lesson"
                >
                  ✕
                </span>
              </div>

              <form>

                <div className="form-group-lesson">
                  <label htmlFor="lesson-title">Lesson Title</label>
                  <input
                    id="lesson-title"
                    type="text"
                    placeholder="Enter lesson title"
                    value={lessonTitle}
                    onChange={(e) => setLessonTitle(e.target.value)}
                  />
                </div>
                <div className="form-group-lesson">
                  <label htmlFor="video-url">Video URL</label>
                  <input
                    id="video-url"
                    type="text"
                    placeholder="Enter lesson video url"
                    value={videoUrl}
                    onChange={(e) => setVideoUrl(e.target.value)}
                  />
                </div>

                <div className="form-group-lesson">
                  <label htmlFor="lesson-duration">Duration (minutes)</label>
                  <input
                    id="lesson-duration"
                    type="number"
                    min="1"
                    placeholder="e.g. 15"
                    value={lessonDuration}
                    onChange={(e) => setLessonDuration(e.target.value)}
                  />
                </div>

                <div className="form-group-lesson">
                  <label>Access</label>

                  <div className="radio-group-lesson">
                    <label>
                      <input
                        type="radio"
                        name="is_free"
                        checked={free === true}
                        onChange={() => setFree(true)}
                      />
                      Free
                    </label>

                    <label>
                      <input
                        type="radio"
                        name="is_free"
                        checked={free === false}
                        onChange={() => setFree(false)}
                      />
                      Locked
                    </label>
                  </div>
                </div>

                <button
                  onClick={() => postAddLesson(selectedSectionId)}
                  type="submit" className="save-btn-lesson">
                  Add Lesson
                </button>

              </form>

            </div>
          </div>
        </div>
      )}


      {editLesson && (
        <div className="modal-overlay-lesson">
          <div className="modal-lesson">
            <div className="modal-content-lesson">

              <div className="top-desc-lesson">
                <h2>Edit Lesson</h2>

                <span
                  onClick={() => setEditLesson(false)}
                  className="close-btn-lesson"
                >
                  ✕
                </span>
              </div>

              <form>

                <div className="form-group-lesson">
                  <label htmlFor="lesson-title">Lesson Title</label>
                  <input
                    id="lesson-title"
                    type="text"
                    placeholder="Enter lesson title"
                    value={lessonTitleEdit}
                    onChange={(e) => setLessonTitleEdit(e.target.value)}
                  />
                </div>
                <div className="form-group-lesson">
                  <label htmlFor="video-url">Video URL</label>
                  <input
                    id="video-url"
                    type="text"
                    placeholder="Enter lesson video url"
                    value={editVideoUrl}
                    onChange={(e) => setEditVideoUrl(e.target.value)}
                  />
                </div>

                <div className="form-group-lesson">
                  <label htmlFor="lesson-duration">Duration (minutes)</label>
                  <input
                    id="lesson-duration"
                    type="number"
                    min="1"
                    placeholder="e.g. 15"
                    value={lessonDurationEdit}
                    onChange={(e) => setLessonDurationEdit(e.target.value)}
                  />
                </div>

                <div className="form-group-lesson">
                  <label>Access</label>

                  <div className="radio-group-lesson">
                    <label>
                      <input
                        type="radio"
                        name="is_free"
                        checked={lockedEdit === false}
                        onChange={() => setLockedEdit(false)}
                      />
                      Free
                    </label>

                    <label>
                      <input
                        type="radio"
                        name="is_free"
                        checked={lockedEdit === true}
                        onChange={() => setLockedEdit(true)}
                      />
                      Locked
                    </label>
                  </div>
                </div>

                <button type="submit" className="save-btn-lesson">
                  Edit Lesson
                </button>

              </form>

            </div>
          </div>
        </div>
      )}



    </>
  );
}

export default ManageCurriculum;