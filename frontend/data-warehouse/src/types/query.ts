/**
 * Enum for different types of queries.
 */
export enum QueryType {
  MOVIES_BY_TIME = 'movies_by_time',
  MOVIES_BY_PERSON = 'movies_by_person',
  MOVIES_BY_PROPERTY = 'movies_by_property',
  HIGH_RATED_MOVIES = 'high_rated_movies',
  ACTOR_COLLABORATIONS = 'actor_collaborations',
  DIRECTOR_ACTOR_COLLABORATIONS = 'director_actor_collaborations',
  COMBINED_QUERY = 'combined_query'
}

/**
 * Represents the parameters for a query.
 */
export interface QueryParams {
  database?: string;
  year?: number;
  month?: number;
  quarter?: number;
  week?: number;
  movie_title?: string;
  director?: string;
  starring_actor?: string;
  participating_actor?: string;
  genre?: string;
  min_score?: number;
  min_reviews?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
  min_collaborations?: number;
}

