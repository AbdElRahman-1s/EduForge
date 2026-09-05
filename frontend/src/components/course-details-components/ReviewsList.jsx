import { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import axios from 'axios';


import './reviews-list.css';




function ReviewsList({ reviews, setReviews }) {
  const { id } = useParams();
  const { accessToken, user } = useContext(AuthContext);
  const [nextUrl, setNextUrl] = useState(null);
  const [editingReviewId, setEditingReviewId] = useState(null);
  const [editRating, setEditRating] = useState(0);
  const [editComment, setEditComment] = useState('');

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const response = await axios.get(
          `/api/courses/${id}/reviews/`
        );

        console.log(response.data);
        setReviews(response.data.results);
        setNextUrl(response.data.next);
      } catch (error) {
        console.error("Error fetching reviews:", error);
      }
    };

    fetchReviews();
  }, [id,setReviews]);


  async function EditReview(reviewId) {
    try {
      const response = await axios.patch(
        `/api/reviews/${reviewId}/`,
        {
          rating: editRating,
          comment: editComment,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      console.log(response.data);
      setReviews((prev) =>
        prev.map((review) =>
          review.id === reviewId ? response.data : review
        )
      );

    } catch (error) {
      console.log(error.response?.data);
    }
  }


  async function DeleteReview(reviewId) {
    try {
      const response = await axios.delete(`/api/reviews/${reviewId}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`
          }
        }
      );

      setReviews((prev) =>
        prev.filter((review) => review.id !== reviewId)
      );

      console.log(response.data);

    } catch (error) {
      console.log(error.response?.data);
    }
  }


  async function loadMoreReviews() {
    if (!nextUrl) return;

    try {
      const response = await axios.get(nextUrl);

      setReviews((prev) => [
        ...prev,
        ...response.data.results,
      ]);

      setNextUrl(response.data.next);

    } catch (error) {
      console.log(error.response?.data);
    }
  }



  return (
    <div className="reviews-list">
      {reviews.map((review) => (
        <div className="review-card" key={review.id}>

          <div className="review-avatar">
            {review.student.username.charAt(0).toUpperCase()}
          </div>

          <div className="review-content">
            <h4>{review.student.username}</h4>

            <div className="review-stars">
              {'★'.repeat(review.rating)}
              {'☆'.repeat(5 - review.rating)}
            </div>

            <p>
              {review.comment}
            </p>

            <span className="review-date">
              {review.created_at}
            </span>
          </div>
          {review.student.id === user.id && (
            <div className="review-actions">
              <button
                onClick={() => {
                  setEditingReviewId(review.id);
                  setEditRating(review.rating);
                  setEditComment(review.comment);
                }}
              >Edit</button>
              <button
                onClick={() => DeleteReview(review.id)}
              >Delete</button>
            </div>
          )}

          {editingReviewId === review.id && (
            <div className="edit-review-form">

              <div className="review-rating">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setEditRating(star)}
                  >
                    {star <= editRating ? '★' : '☆'}
                  </button>
                ))}
              </div>

              <textarea
                value={editComment}
                onChange={(e) => setEditComment(e.target.value)}
              />

              <div className="edit-actions">
                <button
                  onClick={() => EditReview(review.id)}
                >
                  Save
                </button>

                <button onClick={() => setEditingReviewId(null)}>
                  Cancel
                </button>
              </div>

            </div>
          )}

        </div>
      ))}

      {nextUrl && (
        <button
          className="load-more"
          onClick={loadMoreReviews}
        >
          Load more
        </button>
      )}
    </div>
  )
}

export default ReviewsList