

import './rating-summary.css';

function RatingSummary() {
  return (
    <div className='rating-summary'>

      {/* Average Rating */}
      <div className='rating-average'>
        <h3>4.8</h3>

        <div className="stars">
          ★★★★★
        </div>

        <p>31.6k Reviews</p>
      </div>

      {/* Rating Distribution */}
      <div className="rating-distribution">

        <div className="rating-row">
          <span>5 ★</span>
          <div className="rating-bar">
            <div className="rating-fill" style={{ width: "85%" }} />
          </div>
          <span>85%</span>
        </div>

        <div className="rating-row">
          <span>4 ★</span>
          <div className="rating-bar">
            <div className="rating-fill" style={{ width: "10%" }} />
          </div>
          <span>10%</span>
        </div>

        <div className="rating-row">
          <span>3 ★</span>
          <div className="rating-bar">
            <div className="rating-fill" style={{ width: "3%" }} />
          </div>
          <span>3%</span>
        </div>

        <div className="rating-row">
          <span>2 ★</span>
          <div className="rating-bar">
            <div className="rating-fill" style={{ width: "1%" }} />
          </div>
          <span>1%</span>
        </div>

        <div className="rating-row">
          <span>1 ★</span>
          <div className="rating-bar">
            <div className="rating-fill" style={{ width: "1%" }} />
          </div>
          <span>1%</span>
        </div>

      </div>

    </div>
  )
}

export default RatingSummary