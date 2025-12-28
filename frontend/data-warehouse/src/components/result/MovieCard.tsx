import React from 'react';
import type { Movie } from '../../types/data';

interface MovieCardProps {
  movie: Movie;
  isSelected: boolean;
  onSelect: (movie: Movie) => void;
}

// A simple hash function to generate a color from a string
const stringToColor = (str: string) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
  return '#' + '00000'.substring(0, 6 - c.length) + c;
};

const MovieCard: React.FC<MovieCardProps> = ({ movie, isSelected, onSelect }) => {
  const cardStyle: React.CSSProperties = {
    display: 'flex',
    gap: '16px',
    padding: '16px',
    marginBottom: '16px',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
    border: isSelected ? '2px solid #3b82f6' : '1px solid #e5e7eb',
    backgroundColor: isSelected ? '#eff6ff' : 'white',
    boxShadow: isSelected ? '0 4px 12px rgba(0, 0, 0, 0.1)' : '0 1px 3px rgba(0, 0, 0, 0.05)',
  };

  const posterColor = stringToColor(movie.title);

  return (
    <div style={cardStyle} onClick={() => onSelect(movie)} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-3px)'} onMouseLeave={e => e.currentTarget.style.transform = 'none'}>
      {/* Poster Placeholder */}
      <div style={{
        flexShrink: 0,
        width: '80px',
        height: '120px',
        borderRadius: '8px',
        backgroundColor: posterColor,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontWeight: 'bold',
        textAlign: 'center',
        fontSize: '14px',
      }}>
        {movie.title.substring(0, 20)}
      </div>

      {/* Movie Info */}
      <div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', color: '#1f2937' }}>{movie.title}</h3>
        <p style={{ margin: '0 0 4px 0', color: '#6b7280', fontSize: '14px' }}>{movie.director}</p>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
          {movie.genres.slice(0, 3).map(genre => (
            <span key={genre} style={{
              padding: '2px 8px',
              borderRadius: '12px',
              backgroundColor: '#e5e7eb',
              color: '#4b5563',
              fontSize: '12px',
            }}>
              {genre}
            </span>
          ))}
        </div>
        <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center' }}>
          <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#f59e0b' }}>★ {Number(movie.rating ?? NaN).toFixed(1)}</span>
          <span style={{ marginLeft: '12px', fontSize: '12px', color: '#6b7280' }}>({movie.review_count} reviews)</span>
        </div>
      </div>
    </div>
  );
};

export default MovieCard;

