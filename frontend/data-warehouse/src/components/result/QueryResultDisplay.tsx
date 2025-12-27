import React, { useMemo, useState } from 'react';
import type { DatabaseResults, DataSource, DatabaseResult } from '../../types/api';
import type { Movie } from '../../types/data';
import MovieCard from './MovieCard';
import MovieDetails from './MovieDetails';
import ReviewList from './ReviewList';

interface QueryResultDisplayProps {
  results: DatabaseResults;
  dataSource: DataSource;
}

function extractMovies(db: DatabaseResult | null): Movie[] {
  if (!db || !db.result || !db.success) return [];
  // 后端返回 movie_id，前端 Movie 类型使用 id，这里做映射
  // 同时为缺失的必填字段提供默认值，确保组件能正确渲染
  return (db.result ?? []).map((item: any) => ({
    actors: item.actors || [],
    release_date: item.release_date || '',
    ...item,
    id: item.movie_id,
  }));
}

const QueryResultDisplay: React.FC<QueryResultDisplayProps> = ({ results, dataSource }) => {
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  // 规则：强制只显示 opengauss 的数据
  const chosenDb = useMemo(() => {
    const opengaussResult = results.OpenGauss;
    if (opengaussResult && opengaussResult.success) {
      return opengaussResult;
    }
    return null;
  }, [results]);

  const moviesToShow = useMemo(() => extractMovies(chosenDb), [chosenDb]);

  // 如果当前选择的电影不在新结果集里，清空选择，避免右侧详情显示“脏数据”
  React.useEffect(() => {
    if (selectedMovie && !moviesToShow.some(m => m.id === selectedMovie.id)) {
      setSelectedMovie(null);
    }
  }, [moviesToShow, selectedMovie]);

  if (moviesToShow.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
        暂无查询结果
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', gap: '20px', height: '100%' }}>
      {/* Left Panel: Movie List */}
      <div style={{
        flex: '0 0 400px',
        overflowY: 'auto',
        paddingRight: '10px',
      }}>
        <h2 style={{ marginBottom: '1rem', color: '#374151', fontSize: '20px' }}>
          查询结果 ({moviesToShow.length} 部电影)
          {chosenDb ? (
            <span style={{ marginLeft: '8px', fontSize: '12px', color: '#6b7280' }}>
              来自：{chosenDb.database}（{chosenDb.execution_time}ms）
            </span>
          ) : null}
        </h2>
        <div>
          {moviesToShow.map(movie => (
            <MovieCard
              key={movie.id}
              movie={movie}
              isSelected={selectedMovie?.id === movie.id}
              onSelect={setSelectedMovie}
            />
          ))}
        </div>
      </div>

      {/* Right Panel: Movie Details */}
      <div style={{
        flex: '1 1 auto',
        overflowY: 'auto',
        backgroundColor: 'rgba(255, 255, 255, 0.5)',
        borderRadius: '12px',
        padding: '24px',
      }}>
        {selectedMovie ? (
          <div>
            <MovieDetails movie={selectedMovie} />
            <div style={{ marginTop: '24px' }}>
              <h3 style={{ fontSize: '24px', color: '#1f2937', marginBottom: '16px' }}>评论</h3>
              <ReviewList movieId={selectedMovie.id} dataSource={dataSource} />
            </div>
          </div>
        ) : (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: '#9ca3af',
            textAlign: 'center',
          }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
            <h3 style={{ marginTop: '16px', fontSize: '20px', fontWeight: '500' }}>请从左侧选择一部电影查看详情</h3>
            <p>点击电影卡片以加载其详细信息和评论。</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryResultDisplay;
