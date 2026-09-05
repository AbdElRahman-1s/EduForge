import { useState } from 'react';



import RatingSummary from './RatingSummary';
import './reviews-section.css';
import ReviewsList from './ReviewsList';
import WriteReview from './WriteReview';

function ReviewsSection() {

  const [reviews, setReviews] = useState([]);

  return (
    <section className='bigger-section'>
      <h2>Reviews</h2>
      <RatingSummary />
      <WriteReview
        reviews={reviews}
        setReviews={setReviews}
      />
      <ReviewsList
        reviews={reviews}
        setReviews={setReviews}
      />
    </section>
  )
}

export default ReviewsSection