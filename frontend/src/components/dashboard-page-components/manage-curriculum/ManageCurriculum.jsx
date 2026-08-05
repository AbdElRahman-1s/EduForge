import { useState, useEffect } from 'react';
import {
  Plus, GripVertical, PlayCircle, Lock,
  Pencil, Trash2, Check
} from 'lucide-react';

import axios from 'axios';
import './manage-curriculum.css';

function ManageCurriculum({ setSelected }) {

  const [courseDetails, setCourseDetails] = useState(null);

  const courseId = localStorage.getItem("selectedCourseId");

  const [sections, setSections] = useState([
    {
      id: 1,
      title: "1. Getting Started",
      lessons: [
        { id: 101, title: "1.1 Welcome & Course Overview", duration: "05:32", status: "Free", locked: false },
        { id: 102, title: "1.2 How This Course Works", duration: "04:15", status: "Free", locked: false },
        { id: 103, title: "1.3 Tools You Need", duration: "06:40", status: "Locked", locked: true },
        { id: 104, title: "1.4 Installations", duration: "07:20", status: "Locked", locked: true },
      ]
    },
    {
      id: 2,
      title: "2. Basic Concepts",
      lessons: [
        { id: 201, title: "2.1 What is React?", duration: "06:10", status: "Free", locked: false },
        { id: 202, title: "2.2 Your First Component", duration: "08:45", status: "Locked", locked: true },
        { id: 203, title: "2.3 JSX Explained", duration: "09:30", status: "Locked", locked: true },
      ]
    },
    {
      id: 3,
      title: "3. Components",
      lessons: []
    }
  ]);



  useEffect(() => {
    async function fetchCourse() {
      try {
        const response = await axios.get(`/api/courses/${courseId}/`);

        setCourseDetails(response.data);
      } catch (error) {
        console.log(error);
      }
    }

    if (courseId) {
      fetchCourse();
    }
  }, [courseId]);

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

            <button className="add-section-btn">
              + Add Section
            </button>
          </div>

        </div>

        <div className='drag-drop-div'>
          !  Drag and drop sections or lessons to recorder them.
        </div>

        <div className='sections-lessons-container'>
          {sections.map((section) => (
            <div key={section.id} className="section-card">

              {/* هيدر السكشن */}
              <div className="section-header-card">
                <div className="section-title-wrapper">
                  <GripVertical className="drag-icon" size={18} />
                  <span className="section-title">{section.title}</span>
                  <button className="icon-edit-title"><Pencil size={14} /></button>
                </div>

                <div className="section-actions-btns">
                  <button className="btn-add-lesson">
                    <Plus size={15} /> Add Lesson
                  </button>
                  <button className="btn-sec-edit">
                    <Pencil size={14} /> Edit
                  </button>
                  <button className="btn-sec-delete">
                    <Trash2 size={14} /> Delete
                  </button>
                </div>
              </div>

              {/* قائمة الدروس داخل السكشن */}
              {section.lessons.length > 0 && (
                <div className="lessons-wrapper">
                  {section.lessons.map((lesson) => (
                    <div key={lesson.id} className="lesson-item">
                      <div className="lesson-info">
                        <GripVertical className="drag-icon" size={16} />
                        {lesson.locked ? (
                          <Lock size={16} className="lesson-type-icon" />
                        ) : (
                          <PlayCircle size={16} className="lesson-type-icon" />
                        )}
                        <span className="lesson-title">{lesson.title}</span>
                      </div>

                      <div className="lesson-details">
                        <span className="lesson-duration">{lesson.duration}</span>
                        <span className={`badge ${lesson.status.toLowerCase()}`}>
                          {lesson.status}
                        </span>
                        <button className="icon-action-btn"><Pencil size={14} /></button>
                        <button className="icon-action-btn delete"><Trash2 size={14} /></button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

            </div>
          ))}
          {/* زر حفظ الترتيب في الأسفل */}
          <div className="save-order-bar">
            <button className="save-order-btn">
              <Check size={16} /> Save Order
            </button>
            <span className="last-saved-text">Last saved: 2 minutes ago</span>
          </div>

        </div>

      </div>
    </>
  );
}

export default ManageCurriculum;