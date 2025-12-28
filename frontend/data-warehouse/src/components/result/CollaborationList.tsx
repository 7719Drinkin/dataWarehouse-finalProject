import React from 'react';
import type { ActorCollaboration, DirectorActorCollaboration } from '../../types/data';

type CollaborationRow =
  | ({ type: 'actor' } & ActorCollaboration)
  | ({ type: 'director' } & DirectorActorCollaboration);

function normalizeStringArray(v: unknown): string[] {
  if (Array.isArray(v)) return v.map(String);
  if (typeof v === 'string') {
    const s = v.trim();
    if (s.startsWith('[') && s.endsWith(']')) {
      try {
        const parsed = JSON.parse(s);
        return Array.isArray(parsed) ? parsed.map(String) : [];
      } catch {
        return [];
      }
    }
    return s.split(/[|,]/).map(x => x.trim()).filter(Boolean);
  }
  return [];
}

function getCollaborationCount(row: any): number {
  // 兼容后端字段：collaboration_count / collaborations / collaborationCount
  const v = row.collaboration_count ?? row.collaborations ?? row.collaborationCount ?? row.count;
  const n = typeof v === 'string' ? Number(v) : v;
  return Number.isFinite(n) ? n : 0;
}

function getMovies(row: any): string[] {
  return normalizeStringArray(row.movies ?? row.movie_ids ?? row.movie_titles);
}

interface CollaborationListProps {
  title: string;
  rows: any[];
}

const CollaborationList: React.FC<CollaborationListProps> = ({ title, rows }) => {
  const normalized: CollaborationRow[] = rows.map((r: any) => {
    if ('actor1' in r || 'actor2' in r) {
      return {
        type: 'actor',
        actor1: String(r.actor1 ?? ''),
        actor2: String(r.actor2 ?? ''),
        collaboration_count: getCollaborationCount(r),
        movies: getMovies(r),
      };
    }
    // director-actor
    return {
      type: 'director',
      director: String(r.director ?? ''),
      actor: String(r.actor ?? ''),
      collaboration_count: getCollaborationCount(r),
      movies: getMovies(r),
    };
  });

  return (
    <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '16px' }}>
      <h2 style={{ margin: '0 0 12px 0', color: '#374151', fontSize: '18px' }}>{title}</h2>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #e5e7eb' }}>对象1</th>
              <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #e5e7eb' }}>对象2</th>
              <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #e5e7eb' }}>合作次数</th>
              <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #e5e7eb' }}>相关电影</th>
            </tr>
          </thead>
          <tbody>
            {normalized.map((row, idx) => {
              const left = row.type === 'actor' ? row.actor1 : row.director;
              const right = row.type === 'actor' ? row.actor2 : row.actor;
              const movies = row.movies;
              const key = `${row.type}-${left}-${right}-${idx}`;

              return (
                <tr key={key}>
                  <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{left || '-'}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{right || '-'}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{row.collaboration_count}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', color: '#6b7280' }}>
                    {movies.length > 0 ? movies.slice(0, 5).join('，') : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CollaborationList;

