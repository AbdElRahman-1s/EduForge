import { RxPeople } from "react-icons/rx";
import { IoBookOutline } from "react-icons/io5";
import { PiMedalLight } from "react-icons/pi";
import { FaArrowTrendUp } from "react-icons/fa6";

import './statistics.css';

const statistics = [
  {
    icon: <RxPeople />,
    number: '280K+',
    title: 'Active learners'
  },
  {
    icon: <IoBookOutline />,
    number: '4,800+',
    title: 'Expert courses'
  },
  {
    icon: <PiMedalLight />,
    number: '340+',
    title: 'Top instructors'
  },
  {
    icon: <FaArrowTrendUp />,
    number: '96%',
    title: 'Completion rate'
  }

]

function Statistics() {
  return (
    <section>

      <div className="contain">

      <div className="statistics-div">
      {statistics.map((statistic) => {
        return(
          <div className="statistic-div"> 
            <span className="svg-span">{statistic.icon}</span>
            <div className="text-div">
              <p>{statistic.number}</p>
              <span>{statistic.title}</span>
            </div>
          </div>
        )
      })}

      </div>

      </div>



    </section>
  )
}

export default Statistics