import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
import logging
import pandas as pd
from functools import lru_cache
import joblib
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieRecommender:
    CACHE_DIR = Path("cache")
    SIMILARITY_MATRIX_FILE = CACHE_DIR / "similarity_matrix.joblib"
    PROCESSED_DATA_FILE = CACHE_DIR / "processed_data.joblib"
    
    def __init__(self, data):
        """Initialize with movie data"""
        self.data = data
        self.processed_data = None
        self.similarity_matrix = None
        self._initialize_cache_dir()
        self._process_data()
    
    def _initialize_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        self.CACHE_DIR.mkdir(exist_ok=True)
    
    def _load_cache(self):
        """Load cached similarity matrix and processed data"""
        try:
            if self.SIMILARITY_MATRIX_FILE.exists() and self.PROCESSED_DATA_FILE.exists():
                logger.info("Loading cached similarity matrix and processed data...")
                self.similarity_matrix = joblib.load(self.SIMILARITY_MATRIX_FILE)
                self.processed_data = joblib.load(self.PROCESSED_DATA_FILE)
                return True
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        return False
    
    def _save_cache(self):
        """Save similarity matrix and processed data to cache"""
        try:
            logger.info("Saving similarity matrix and processed data to cache...")
            joblib.dump(self.similarity_matrix, self.SIMILARITY_MATRIX_FILE)
            joblib.dump(self.processed_data, self.PROCESSED_DATA_FILE)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _process_data(self):
        """Process the data and create similarity matrix with caching"""
        if self._load_cache():
            return
            
        try:
            logger.info("Processing data and creating similarity matrix...")
            self.processed_data, self.similarity_matrix = create_similarity_matrix(self.data)
            self._save_cache()
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise
    
    @lru_cache(maxsize=1000)
    def find_similar_movies(self, title, max_recommendations=10):
        """Find similar movies based on title with caching"""
        try:
            return get_recommendations(
                title, 
                self.processed_data,
                self.similarity_matrix,
                max_recommendations=max_recommendations
            )
        except Exception as e:
            logger.error(f"Error finding similar movies: {str(e)}")
            return []

def create_similarity_matrix(data):
    """Create a similarity matrix based on movie content"""
    try:
        # Ensure we have the required columns
        required_columns = ['genres', 'year', 'averageRating', 'title']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Create content string for each movie
        logger.info("Creating content strings...")
        data['content'] = data.apply(_create_content_string, axis=1)
        
        # Remove any rows where content is empty
        data = data[data['content'].str.len() > 0].copy()
        
        if len(data) == 0:
            raise ValueError("No valid movies found after processing")
        
        logger.info(f"Processing {len(data)} movies...")
        
        # Create the vectorizer with specific stop words and token pattern
        count_vectorizer = CountVectorizer(
            tokenizer=lambda x: x.split(),
            token_pattern=None,  # Disable default token pattern
            stop_words=None,  # Don't use default stop words
            min_df=1,  # Include all terms
            max_features=5000  # Limit features for better performance
        )
        
        # Create the count matrix
        count_matrix = count_vectorizer.fit_transform(data['content'])
        
        if count_matrix.shape[1] == 0:
            raise ValueError("No valid features extracted from movie content")
        
        logger.info(f"Created matrix with shape: {count_matrix.shape}")
        
        # Calculate similarity
        similarity_matrix = cosine_similarity(count_matrix, count_matrix)
        
        return data, similarity_matrix
        
    except Exception as e:
        logger.error(f"Error creating similarity matrix: {str(e)}")
        raise

def _create_content_string(row):
    """Create a content string for a movie with weighted features"""
    try:
        content_parts = []
        
        # Add genres with reduced weight to prevent over-domination
        if pd.notna(row['genres']):
            genres = str(row['genres']).split()
            # Add each genre only once to reduce genre dominance
            content_parts.extend([genre.lower() for genre in genres])
        
        # Add themes and keywords based on genres
        if pd.notna(row['genres']):
            genres = str(row['genres']).split()
            # Add related themes for genre variety
            theme_mapping = {
                'Horror': ['suspense', 'tension', 'supernatural'],
                'Sci-Fi': ['space', 'future', 'technology'],
                'Thriller': ['suspense', 'mystery', 'tension'],
                'Drama': ['emotional', 'character-driven', 'relationship'],
                'Action': ['adventure', 'excitement', 'dynamic'],
                'Mystery': ['investigation', 'suspense', 'discovery'],
                'Adventure': ['journey', 'exploration', 'discovery'],
                'Fantasy': ['magical', 'imagination', 'supernatural']
            }
            for genre in genres:
                if genre in theme_mapping:
                    content_parts.extend(theme_mapping[genre])
        
        # Add year with high weight for temporal relevance
        if pd.notna(row['year']):
            year = int(row['year'])
            decade = (year // 10) * 10
            content_parts.extend([
                f"year_{year}",
                f"decade_{decade}",
                f"era_{decade}"
            ] * 2)
        
        # Add rating with increased weight
        if pd.notna(row['averageRating']):
            rating = float(row['averageRating'])
            # Create rating bands
            if rating >= 7.5:
                content_parts.extend(['excellent_rating'] * 3)
            elif rating >= 6.5:
                content_parts.extend(['good_rating'] * 2)
            else:
                content_parts.append('average_rating')
        
        # Add popularity consideration
        if pd.notna(row.get('numVotes')):
            vote_count = int(row['numVotes'])
            if vote_count > 100000:
                content_parts.extend(['highly_popular'] * 2)
            elif vote_count > 50000:
                content_parts.append('popular')
            elif vote_count > 10000:
                content_parts.append('moderate_popularity')
        
        # Join all parts with spaces
        content = ' '.join(content_parts)
        
        if not content:
            logger.warning(f"Empty content string created for movie: {row.get('title', 'Unknown')}")
            
        return content
        
    except Exception as e:
        logger.error(f"Error creating content string for movie {row.get('title', 'Unknown')}: {str(e)}")
        return ""

def get_recommendations(title, data, similarity_matrix, min_similarity=70, max_recommendations=10):
    """Get movie recommendations based on title with enhanced diversity"""
    try:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Invalid title: must be a non-empty string")
            
        title_to_index = {row['title']: idx for idx, row in data.iterrows()}

        # Find closest match using fuzzy matching
        closest_match = process.extractOne(title, list(title_to_index.keys()))
        if not closest_match or closest_match[1] < min_similarity:
            logger.info(f"No close matches found for title: {title}")
            return []

        matched_title = closest_match[0]
        movie_idx = title_to_index[matched_title]
        source_movie = data.iloc[movie_idx]

        # Get similarity scores
        similarity_scores = list(enumerate(similarity_matrix[movie_idx]))
        
        # Get source movie information
        source_genres = set(source_movie['genres'].split() if pd.notna(source_movie['genres']) else [])
        source_year = int(source_movie['year']) if pd.notna(source_movie['year']) else 2024
        
        recommendations = []
        seen_genres = set()  # Track recommended genres
        genre_counts = {}    # Track genre frequencies
        seen_titles = set()  # Track recommended titles
        
        # First pass: Calculate scores for all candidates
        candidates = []
        for idx, base_score in similarity_scores:
            if idx == movie_idx:
                continue

            movie = data.iloc[idx]
            title = movie['title']
            
            if title in seen_titles:
                continue
                
            current_genres = set(movie['genres'].split() if pd.notna(movie['genres']) else [])
            
            # Skip if too similar in genres when we already have enough recommendations
            if len(recommendations) >= max_recommendations // 2:
                if current_genres == source_genres:
                    continue
            
            # Calculate various bonus scores
            
            # Genre diversity bonus (0-0.3)
            new_genres = current_genres - seen_genres
            diversity_bonus = len(new_genres) * 0.15
            
            # Genre variety penalty (to avoid same-genre domination)
            genre_penalty = 0
            for genre in current_genres:
                if genre in genre_counts:
                    genre_penalty += genre_counts.get(genre, 0) * 0.05
            
            # Rating bonus (0-0.2)
            rating = float(movie['averageRating']) if pd.notna(movie['averageRating']) else 0
            rating_bonus = (rating - 5) * 0.04 if rating > 5 else 0
            
            # Popularity bonus (0-0.15)
            votes = int(movie['numVotes']) if pd.notna(movie.get('numVotes')) else 0
            popularity_bonus = min(0.15, votes / 1000000)
            
            # Era diversity bonus (0-0.2)
            year = int(movie['year']) if pd.notna(movie['year']) else 2024
            year_diff = abs(year - source_year)
            era_bonus = min(0.2, year_diff / 200)  # Max bonus for 40-year difference
            
            # Combine all scores
            final_score = (
                float(base_score) * 0.5 +    # Base similarity (50% weight)
                diversity_bonus * 0.2 +       # Genre diversity (20% weight)
                rating_bonus * 0.15 +         # Rating bonus (15% weight)
                popularity_bonus * 0.1 +      # Popularity (10% weight)
                era_bonus * 0.05 -           # Era diversity (5% weight)
                genre_penalty                # Genre penalty to prevent repetition
            )
            
            candidates.append({
                'title': title,
                'year': year,
                'genres': list(current_genres),
                'rating': rating,
                'similarity_score': final_score,
                'idx': idx
            })
            
            # Update genre counts
            for genre in current_genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # Sort candidates by final score and select top recommendations
        candidates.sort(key=lambda x: x['similarity_score'], reverse=True)
        recommendations = candidates[:max_recommendations]
        
        return recommendations
            
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        return []