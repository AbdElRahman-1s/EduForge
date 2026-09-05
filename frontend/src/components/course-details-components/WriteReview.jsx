import { useState, useContext } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

import { AuthContext } from '../../context/AuthContext';

import './write-review.css';

function WriteReview({setReviews }) {
  const { id } = useParams();
  const { accessToken } = useContext(AuthContext);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmitReview = async () => {
    if (rating === 0) {
      setErrorMessage('Please select a rating');
      return;
    }

    if (!comment.trim()) {
      setErrorMessage('Please write a review');
      return;
    }

    try {
      const response = await axios.post(
        `/api/courses/${id}/reviews/`,
        {
          rating,
          comment,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          }
        }
      );

      console.log(response.data);
      setReviews((prev) => [response.data, ...prev]);
    } catch (error) {
      const data = error.response?.data;

      if (data?.detail) {
        setErrorMessage(data.detail);
      } else if (data?.rating) {
        setErrorMessage(data.rating[0]);
      } else {
        setErrorMessage("Something went wrong. Please try again.");
      }
    }
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
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      <button
        className='click-submit'
        onClick={handleSubmitReview}
      >
        Submit Review
      </button>
    </div>
  );
}

export default WriteReview;