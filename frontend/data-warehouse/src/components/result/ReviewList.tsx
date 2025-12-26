import React, { useState, useEffect, useCallback } from 'react';
import type { Review } from '../../types/data';
import type { DataSource } from '../../types/api';
import { mockFetchReviews } from '../../api/mock'; // 从 mock.ts 导入
import ReviewItem from './ReviewItem';
import LoadingIndicator from '../common/LoadingIndicator';
import ErrorMessage from '../common/ErrorMessage';

interface ReviewListProps {
  movieId: string;
  dataSource: DataSource;
}

const ReviewList: React.FC<ReviewListProps> = ({ movieId, dataSource }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({ page: 1, pageSize: 5, hasMore: true });

  const loadReviews = useCallback(async (page: number) => {
    setLoading(true);
    setError(null);

    try {
      // 将真实 API 调用替换为模拟数据调用
      const response = await mockFetchReviews(
        { filters: { movie_id: movieId } },
        { page, pageSize: pagination.pageSize },
        dataSource
      );

      if (response.success) {
        setReviews(prev => (page === 1 ? response.data : [...prev, ...response.data]));
        setPagination(prev => ({
          ...prev,
          page,
          hasMore: response.data.length === prev.pageSize,
        }));
      } else {
        setError(response.message || 'Failed to load reviews.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setLoading(false);
    }
  }, [movieId, pagination.pageSize, dataSource]);

  useEffect(() => {
    setReviews([]);
    setPagination(prev => ({ ...prev, page: 1, hasMore: true }));
    loadReviews(1);
  }, [movieId, loadReviews]);

  const handleLoadMore = () => {
    if (pagination.hasMore && !loading) {
      loadReviews(pagination.page + 1);
    }
  };

  if (loading && pagination.page === 1) {
    return <LoadingIndicator message="Loading reviews..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={() => loadReviews(1)} />;
  }

  if (reviews.length === 0) {
    return <div style={{ textAlign: 'center', color: '#6b7280', padding: '24px' }}>No reviews found for this movie.</div>;
  }

  return (
    <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
      {reviews.map(review => (
        <ReviewItem key={review.asin} review={review} />
      ))}

      {pagination.hasMore && (
        <div style={{ textAlign: 'center', padding: '16px' }}>
          <button 
            onClick={handleLoadMore} 
            disabled={loading}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: '1px solid #3b82f6',
              backgroundColor: loading ? '#dbeafe' : 'white',
              color: '#3b82f6',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              transition: 'background-color 0.2s',
            }}
          >
            {loading ? 'Loading...' : 'Load More Reviews'}
          </button>
        </div>
      )}
    </div>
  );
};

export default ReviewList;
