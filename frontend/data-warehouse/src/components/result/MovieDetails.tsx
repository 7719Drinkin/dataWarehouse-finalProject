import React from 'react';
import type { Movie } from '../../types/data';

interface MovieDetailsProps {
  movie: Movie;
}

const MovieDetails: React.FC<MovieDetailsProps> = ({ movie }) => {
  /* =======================
   * 数据归一化（关键）
   * ======================= */

  const actors: string[] = Array.isArray(movie.actors)
    ? movie.actors
    : typeof movie.actors === 'string'
      ? movie.actors.split(',').map(a => a.trim()).filter(Boolean)
      : [];

  const genres: string[] = Array.isArray(movie.genres)
    ? movie.genres
    : typeof movie.genres === 'string'
      ? movie.genres.split(',').map(g => g.trim()).filter(Boolean)
      : [];

  const rating = Number(movie.rating);
  const reviewCount = Number(movie.review_count);
  const boxOffice = Number(movie.box_office);
  const runtime = Number(movie.runtime);

  /* =======================
   * 样式
   * ======================= */

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

  /* =======================
   * 渲染
   * ======================= */

  return (
    <div
      style={{
        padding: '24px',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
      }}
    >
      <h2
        style={{
          margin: '0 0 24px 0',
          fontSize: '28px',
          color: '#1f2937',
          borderBottom: '2px solid #3b82f6',
          paddingBottom: '12px',
        }}
      >
        {movie.title || '未知影片'}
      </h2>

      <div style={detailItemStyle}>
        <span style={labelStyle}>导演</span>
        <span>{movie.director || '未知'}</span>
      </div>

      <div style={detailItemStyle}>
        <span style={labelStyle}>演员</span>
        <span style={{ textAlign: 'right' }}>
          {actors.length ? actors.join(', ') : '未知'}
        </span>
      </div>

      <div style={detailItemStyle}>
        <span style={labelStyle}>类型</span>
        <span style={{ textAlign: 'right' }}>
          {genres.length ? genres.join(', ') : '未知'}
        </span>
      </div>

      <div style={detailItemStyle}>
        <span style={labelStyle}>上映日期</span>
        <span>{movie.release_date || '未知'}</span>
      </div>

      <div style={detailItemStyle}>
        <span style={labelStyle}>评分</span>
        <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>
          ★ {Number.isFinite(rating) ? rating.toFixed(1) : 'N/A'}
        </span>
      </div>

      <div style={detailItemStyle}>
        <span style={labelStyle}>评论数</span>
        <span>
          {Number.isFinite(reviewCount) ? reviewCount.toLocaleString() : '0'}
        </span>
      </div>

      {Number.isFinite(runtime) && runtime > 0 && (
        <div style={detailItemStyle}>
          <span style={labelStyle}>片长</span>
          <span>{runtime} 分钟</span>
        </div>
      )}

      {Number.isFinite(boxOffice) && boxOffice > 0 && (
        <div style={detailItemStyle}>
          <span style={labelStyle}>票房</span>
          <span>${boxOffice.toLocaleString()}</span>
        </div>
      )}

      {movie.plot && (
        <div style={{ marginTop: '24px' }}>
          <h4 style={{ color: '#4b5563', marginBottom: '8px' }}>剧情简介</h4>
          <p style={{ color: '#6b7280', lineHeight: 1.6 }}>{movie.plot}</p>
        </div>
      )}
    </div>
  );
};

export default MovieDetails;
