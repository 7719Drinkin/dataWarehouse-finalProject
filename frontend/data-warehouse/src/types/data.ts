/**
 * Represents a movie entity.
 */
export interface Movie {
  id: string;
  title: string;
  release_date: string;
  director: string;
  actors: string[];
  genres: string[];
  rating: number;
  review_count: number;
  plot?: string;
  runtime?: number;
  box_office?: number;
}

/**
 * Represents a review for a movie.
 */
export interface Review {
    asin: string;
    movie_id: string;
    user_id: string;
    profile_name: string;
    helpfulness: [number, number];
    score: number;
    review_time: string;
    review_summary: string;
    review_text: string;
  }  

/**
 * Represents the collaboration between two actors.
 */
export interface ActorCollaboration {
  actor1: string;
  actor2: string;
  collaboration_count: number;
  movies: string[];
}

/**
 * Represents the collaboration between a director and an actor.
 */
export interface DirectorActorCollaboration {
  director: string;
  actor: string;
  collaboration_count: number;
  movies: string[];
}

/**
 * Represents the data structure for charts.
 */
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

/**
 * Represents the configuration for charts.
 */
export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'doughnut';
  data: ChartData;
  options?: unknown; // It's better to use ChartOptions from chart.js if it's used
}
