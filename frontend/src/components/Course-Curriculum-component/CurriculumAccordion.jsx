import { useState } from "react";



import { GoLock } from "react-icons/go";
import { IoIosPlay } from "react-icons/io";
import { LuCircleCheckBig } from "react-icons/lu";
import { IoIosArrowDown , IoIosArrowUp } from "react-icons/io";


import './curriculum-accordion.css';

function CurriculumAccordion() {

  const [openSectionId, setOpenSectionId] = useState(null);




  const sections = [
    {
      id: 1,
      title: "Getting Started",
      lessons: [
        {
          id: 1,
          title: "Course Introduction",
          duration: "5 min",
          status: "preview",
        },
        {
          id: 2,
          title: "Install React",
          duration: "12 min",
          status: "locked",
        },
        {
          id: 3,
          title: "Components",
          duration: "8 min",
          status: "completed",
        },
      ],
    },
    {
      id: 2,
      title: "React Basics",
      lessons: [
        {
          id: 4,
          title: "JSX",
          duration: "10 min",
          status: "completed",
        },
        {
          id: 5,
          title: "Props",
          duration: "15 min",
          status: "locked",
        },
        {
          id: 6,
          title: "State",
          duration: "20 min",
          status: "locked",
        },
      ],
    },
  ];


  return (
    <div className="curriculum">

      {
        sections.map((section) => (
          <div className="curriculum-section" key={section.id}>

            <div
              className="section-header"
              onClick={() =>
                setOpenSectionId(
                  openSectionId === section.id ? null : section.id
                )
              }
            >
              <h4>{section.title}</h4>

              <span className="span-lessons">
                {section.lessons.length} lessons
              </span>
              
              <span className="span-arrow">
                {
                  openSectionId === section.id ? <IoIosArrowUp /> : <IoIosArrowDown />
                }
              </span>

            </div>

            {
              openSectionId === section.id && (
                <div className="section-content">

                  {
                    section.lessons.map((lesson) => (
                      <div className="lesson-row" key={lesson.id}>

                        <span className="lesson-icon">
                          {lesson.status === "preview" && <IoIosPlay />}
                          {lesson.status === "locked" && <GoLock className="locked-svg" />}
                          {lesson.status === "completed" && <LuCircleCheckBig className="completed-svg" />}
                        </span>

                        <span className={lesson.status === "completed" ? "lesson-title-completed" : "lesson-title"}>
                          {lesson.title}
                        </span>

                        <span className="lesson-duration">
                          {lesson.duration}
                        </span>

                        <span className="lesson-status">
                          {lesson.status === "preview" && "Free Preview"}
                          {lesson.status === "locked" && "Locked"}
                          {lesson.status === "completed" && "Completed"}
                        </span>

                      </div>
                    ))
                  }

                </div>
              )
            }

          </div>
        ))
      }

    </div>
  )
}

export default CurriculumAccordion