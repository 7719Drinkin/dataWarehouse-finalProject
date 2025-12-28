import React, { useMemo, useState } from 'react';
import type { DatabaseResults, DataSource, DatabaseResult } from '../../types/api';
import type { Movie } from '../../types/data';
import MovieCard from './MovieCard';
import MovieDetails from './MovieDetails';
import ReviewList from './ReviewList';
import CollaborationList from './CollaborationList';

interface QueryResultDisplayProps {
  results: DatabaseResults;
  dataSource: DataSource;
  queryType?: string;
}

function toStringArray(v: unknown): string[] {
  if (Array.isArray(v)) {
    return v.filter((x): x is string => typeof x === 'string');
  }

  if (typeof v === 'string') {
    const s = v.trim();

    // 兼容后端把数组序列化成字符串，如 "[]" / "[\"A\",\"B\"]"
    if (s.startsWith('[') && s.endsWith(']')) {
      try {
        const parsed = JSON.parse(s);
        return Array.isArray(parsed) ? parsed.filter((x): x is string => typeof x === 'string') : [];
      } catch {
        return [];
      }
    }

    // 兼容 "a,b,c" 或 "a|b|c"
    return s
      .split(/[|,]/)
      .map(x => x.trim())
      .filter(Boolean);
  }

  return [];
}

function extractMovies(db: DatabaseResult | null): Movie[] {
  if (!db || !db.success) return [];
  const rows = (db as any).data ?? (db as any).result ?? [];

  return (rows ?? []).map((item: any) => ({
    actors: item.actors || [],
    release_date: item.release_date || '',
    ...item,
    id: item.id ?? item.movie_id,
    genres: toStringArray(item.genres),
    director: toStringArray(item.director),
  }));
}

function extractRows(db: DatabaseResult | null): any[] {
  if (!db || !db.success) return [];
  return (db as any).data ?? (db as any).result ?? [];
}

const QueryResultDisplay: React.FC<QueryResultDisplayProps> = ({ results, dataSource, queryType }) => {
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  // 选择一个用于“主要展示”的数据库结果：
  // - movies_by_person 强制展示 neo4j（你之前的需求）
  // - 其他查询默认展示 opengauss（保持现状，便于调试）
  const chosenDb = useMemo(() => {
    if (queryType === 'movies_by_person') {
      const neo4jResult = (results as any).neo4j || (results as any).Neo4j;
      if (neo4jResult && neo4jResult.success) return neo4jResult;
    }

    const opengaussResult = (results as any).opengauss || (results as any).OpenGauss;
    if (opengaussResult && opengaussResult.success) {
      return opengaussResult;
    }
    return null;
  }, [results, queryType]);

  // --------- 非电影列表查询：合作关系 ---------
  if (queryType === 'actor_collaborations' || queryType === 'director_actor_collaborations') {
    const rows = extractRows(chosenDb);

    return (
      <CollaborationList
        title={queryType === 'actor_collaborations' ? '演员-演员合作关系' : '导演-演员合作关系'}
        rows={rows}
      />
    );
  }

  // --------- 电影列表查询 ---------
  const moviesToShow = useMemo(() => extractMovies(chosenDb), [chosenDb]);

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
              来自：{(chosenDb as any).database ?? '-'}（{(chosenDb as any).execution_time}ms）
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
