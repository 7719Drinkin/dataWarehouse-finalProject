import React from 'react';
import type { Review } from '../../types/data';

interface ReviewItemProps {
  review: Review;
}

// Helper to generate a consistent avatar color from a user ID
const getAvatarColor = (userId: string) => {
  let hash = 0;
  for (let i = 0; i < userId.length; i++) {
    hash = userId.charCodeAt(i) + ((hash << 5) - hash);
  }
  const color = `hsl(${hash % 360}, 75%, 60%)`;
  return color;
};

const ReviewItem: React.FC<ReviewItemProps> = ({ review }) => {
  const avatarColor = getAvatarColor(review.user_id);

  return (
    <div style={{
      display: 'flex',
      gap: '16px',
      padding: '16px',
      borderBottom: '1px solid #f0f0f0',
    }}>
      {/* Avatar */}
      <div style={{
        width: '48px',
        height: '48px',
        borderRadius: '50%',
        backgroundColor: avatarColor,
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        fontSize: '18px',
        flexShrink: 0,
      }}>
        {review.profile_name.charAt(0).toUpperCase()}
      </div>

      {/* Review Content */}
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 'bold', color: '#1f2937' }}>{review.profile_name}</span>
          <span style={{ fontSize: '12px', color: '#6b7280' }}>{new Date(review.review_time).toLocaleDateString()}</span>
        </div>
        <div style={{ margin: '4px 0' }}>
          {[...Array(5)].map((_, i) => (
            <span key={i} style={{ color: i < review.score ? '#f59e0b' : '#d1d5db', fontSize: '18px' }}>★</span>
          ))}
        </div>
        <h4 style={{ margin: '8px 0', color: '#374151' }}>{review.review_summary}</h4>
        <p style={{ margin: 0, color: '#4b5563', lineHeight: 1.5 }}>{review.review_text}</p>
        <div style={{ marginTop: '8px', fontSize: '12px', color: '#6b7280' }}>
          {review.helpfulness[0]} out of {review.helpfulness[1]} people found this helpful.
        </div>
      </div>
    </div>
  );
};

export default ReviewItem;

