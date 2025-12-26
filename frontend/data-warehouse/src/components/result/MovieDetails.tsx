import React from 'react';
import type { Movie } from '../../types/data';

interface MovieDetailsProps {
  movie: Movie;
}

const MovieDetails: React.FC<MovieDetailsProps> = ({ movie }) => {
  const detailItemStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px 0',
    borderBottom: '1px solid #f0f0f0',
  };

  const labelStyle: React.CSSProperties = {
    fontWeight: 'bold',
    color: '#4b5563',
  };

  return (
    <div style={{ padding: '24px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
      <h2 style={{ margin: '0 0 24px 0', fontSize: '28px', color: '#1f2937', borderBottom: '2px solid #3b82f6', paddingBottom: '12px' }}>
        {movie.title}
      </h2>
      
      <div style={detailItemStyle}>
        <span style={labelStyle}>导演</span>
        <span>{movie.director}</span>
      </div>
      <div style={detailItemStyle}>
        <span style={labelStyle}>演员</span>
        <span style={{ textAlign: 'right' }}>{movie.actors.join(', ')}</span>
      </div>
      <div style={detailItemStyle}>
        <span style={labelStyle}>类型</span>
        <span style={{ textAlign: 'right' }}>{movie.genres.join(', ')}</span>
      </div>
      <div style={detailItemStyle}>
        <span style={labelStyle}>上映日期</span>
        <span>{movie.release_date}</span>
      </div>
      <div style={detailItemStyle}>
        <span style={labelStyle}>评分</span>
        <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>★ {movie.rating.toFixed(1)}</span>
      </div>
      <div style={detailItemStyle}>
        <span style={labelStyle}>评论数</span>
        <span>{movie.review_count.toLocaleString()}</span>
      </div>
      {movie.runtime && (
        <div style={detailItemStyle}>
          <span style={labelStyle}>片长</span>
          <span>{movie.runtime} 分钟</span>
        </div>
      )}
      {movie.box_office && (
        <div style={detailItemStyle}>
          <span style={labelStyle}>票房</span>
          <span>${movie.box_office.toLocaleString()}</span>
        </div>
      )}
      {movie.plot && (
        <div style={{ marginTop: '24px' }}>
          <h4 style={{ color: '#4b5563' }}>剧情简介</h4>
          <p style={{ color: '#6b7280', lineHeight: 1.6 }}>{movie.plot}</p>
        </div>
      )}
    </div>
  );
};

export default MovieDetails;

