import { useState } from 'react';


import './write-review.css';

function WriteReview() {

  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');

  const handleSubmit = () => {
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    if (!comment.trim()) {
      alert('Please write a review');
      return;
    }

    console.log(rating, comment);
  };

  return (
    <div className="write-review">
      <h3>Write a review</h3>

      <div className="review-rating">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
          >
            {star <= rating ? '★' : '☆'}
          </button>
        ))}
      </div>

      <textarea
        placeholder="What did you think about this course?"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />

      <button
        className='click-submit'
        onClick={handleSubmit}
      >
        Submit Review
      </button>
    </div>
  );
}

export default WriteReview;