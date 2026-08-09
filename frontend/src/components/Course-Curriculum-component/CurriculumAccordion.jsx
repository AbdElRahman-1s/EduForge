import { useState } from "react";
import { secondsToTime } from "../../utills/time";

import { GoLock } from "react-icons/go";
import { IoIosPlay } from "react-icons/io";
// import { LuCircleCheckBig } from "react-icons/lu";
import { IoIosArrowDown, IoIosArrowUp } from "react-icons/io";


import './curriculum-accordion.css';

function CurriculumAccordion({ sections }) {

  const [openSectionId, setOpenSectionId] = useState(null);




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
                          {lesson.free && <IoIosPlay />}
                          {!lesson.free && <GoLock className="locked-svg" />}
                          {/* {lesson.status === "completed" && <LuCircleCheckBig className="completed-svg" />} */}
                        </span>

                        <span className={lesson.status === "completed" ? "lesson-title-completed" : "lesson-title"}>
                          {lesson.title}
                        </span>

                        <span className="lesson-duration">
                          {secondsToTime(lesson.duration_seconds)}
                        </span>

                        <span className="lesson-status">
                          {lesson.free ? "Free Preview" : "Locked"}
                          {/* {lesson.status === "completed" && "Completed"} */}
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