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
        
        # Add genres (highest weight)
        if pd.notna(row['genres']):
            genres = str(row['genres']).split()
            content_parts.extend([genre.lower() for genre in genres] * 3)
        
        # Add year (medium weight)
        if pd.notna(row['year']):
            year = str(int(row['year']))
            content_parts.extend([f"year_{year}"] * 2)
        
        # Add rating (lower weight)
        if pd.notna(row['averageRating']):
            rating = int(float(row['averageRating']) * 2)
            content_parts.append(f"rating_{rating}")
        
        # Join all parts with spaces
        content = ' '.join(content_parts)
        
        if not content:
            logger.warning(f"Empty content string created for movie: {row.get('title', 'Unknown')}")
            
        return content
        
    except Exception as e:
        logger.error(f"Error creating content string for movie {row.get('title', 'Unknown')}: {str(e)}")
        return ""

def get_recommendations(title, data, similarity_matrix, min_similarity=70, max_recommendations=10):
    """Get movie recommendations based on title"""
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

        # Get similarity scores
        similarity_scores = list(enumerate(similarity_matrix[movie_idx]))
        sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        recommendations = []
        seen_titles = set()  # To avoid duplicate recommendations

        for idx, score in sorted_scores:
            if len(recommendations) >= max_recommendations:
                break
                
            if idx == movie_idx:  # Skip the searched movie itself
                continue

            movie = data.iloc[idx]
            title = movie['title']
            
            # Skip if we've already recommended this title
            if title in seen_titles:
                continue
                
            seen_titles.add(title)
            
            recommendations.append({
                'title': title,
                'year': int(movie['year']) if pd.notna(movie['year']) else None,
                'genres': movie['genres'].split() if pd.notna(movie['genres']) else [],
                'rating': float(movie['averageRating']) if pd.notna(movie['averageRating']) else None,
                'similarity_score': float(score)
            })

        return recommendations
            
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        return []