import { FaArrowTrendUp } from "react-icons/fa6";
import { RxPeople } from "react-icons/rx";
import { TiFolderOpen } from "react-icons/ti";
import { PiMedalLight } from "react-icons/pi";
import './dashboard-stats.css';

const statsInfo = [
  {
    title: 'Total Revenue',
    icon: <FaArrowTrendUp />,
    value: '$48,320',
    change: '+12.4%'
  },
  {
    title: 'Active Students',
    icon: <RxPeople />,
    value: '12,840',
    change: '+8.7%'
  },
  {
    title: 'Total Courses',
    icon: < TiFolderOpen />,
    value: '6',
    change: '+2 this month'
  },
  {
    title: 'Completion Rate',
    icon: <PiMedalLight />,
    value: '96%',
    change: '+1.2%'
  }
]

function DashboardStats() {
  return (
    <section>
      <div className="container-dashboard">
        <div className='grid-container-stats'>
          {
            statsInfo.map((statInfo, i) => {
              return (
                <div key={i} className="stat-info">
                  <span
                    className={
                      (statInfo.title === 'Total Revenue' && 'first-stat') ||
                      (statInfo.title === 'Active Students' && 'second-stat') ||
                      (statInfo.title === 'Total Courses' && 'third-stat') ||
                      (statInfo.title === 'Completion Rate' && 'fourth-stat')
                    }
                  >{statInfo.icon}</span>
                  <div className="more-stats">
                    <h3 className="stats-value">
                      {statInfo.value}
                      </h3>
                    <p className="stats-title">
                      {statInfo.title}
                      </p>
                    <span className="stats-change">
                      {statInfo.change}
                      </span>
                  </div>
                </div>
              )
            })
          }
        </div>
      </div>
    </section>
  )
}

export default DashboardStats