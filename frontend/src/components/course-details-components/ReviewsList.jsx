



import './reviews-list.css';


const reviews = [
  {
    id: 1,
    name: 'Ahmed',
    avatar: 'A',
    rating: 5,
    comment: 'Great course! Really helpful and easy to understand.',
    date: '2 days ago',
  },
  {
    id: 2,
    name: 'Mohamed',
    avatar: 'M',
    rating: 4,
    comment: 'Very good course. The explanation is clear and simple.',
    date: '5 days ago',
  },
  {
    id: 3,
    name: 'Sara',
    avatar: 'S',
    rating: 5,
    comment: 'I really enjoyed the course and learned a lot from it.',
    date: '1 week ago',
  },
  {
    id: 4,
    name: 'Omar',
    avatar: 'O',
    rating: 4,
    comment: 'Good content and useful examples. Highly recommended.',
    date: '2 weeks ago',
  },
];






function ReviewsList() {
  return (
    <div className="reviews-list">
      {reviews.map((review) => (
        <div className="review-card" key={review.id}>

          <div className="review-avatar">
            {review.avatar}
          </div>

          <div className="review-content">
            <h4>{review.name}</h4>

            <div className="review-stars">
              {'★'.repeat(review.rating)}
            </div>

            <p>
              {review.comment}
            </p>

            <span className="review-date">
              {review.date}
            </span>
          </div>

        </div>
      ))}

      <button className="load-more">
        Load more
      </button>
    </div>
  )
}

export default ReviewsList