



import RatingSummary from './RatingSummary';
import './reviews-section.css';
import ReviewsList from './ReviewsList';
import WriteReview from './WriteReview';

function ReviewsSection() {
  return (
    <section className='bigger-section'>
      <h2>Reviews</h2>
      <RatingSummary />
      <WriteReview />
      <ReviewsList />
    </section>
  )
}

export default ReviewsSection