import pandas as pd
import logging
from pathlib import Path
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache settings
CACHE_DIR = Path("cache")
PROCESSED_DATA_CACHE = CACHE_DIR / "processed_movies.joblib"

def load_movies():
    """
    Load and process IMDb movie data with caching
    """
    try:
        # Try to load from cache first
        if PROCESSED_DATA_CACHE.exists():
            logger.info("Loading processed movies from cache...")
            return joblib.load(PROCESSED_DATA_CACHE)
            
        logger.info("Loading IMDb data...")
        
        # Load ratings data with specific dtypes
        logger.info("1/3 Loading ratings...")
        ratings = pd.read_csv(
            'data/title.ratings.tsv',
            sep='\t',
            usecols=['tconst', 'averageRating', 'numVotes'],
            dtype={
                'tconst': str,
                'averageRating': float,
                'numVotes': int
            }
        )
        
        # Load movie basics with specific dtypes
        logger.info("2/3 Loading movie information...")
        movies = pd.read_csv(
            'data/title.basics.tsv',
            sep='\t',
            usecols=['tconst', 'titleType', 'primaryTitle', 'startYear', 'genres'],
            dtype={
                'tconst': str,
                'titleType': str,
                'primaryTitle': str,
                'startYear': str,
                'genres': str
            }
        )
        
        # Clean and filter movies
        logger.info("3/3 Processing and filtering data...")
        
        # Filter movies and clean data
        movies = movies[
            (movies['titleType'] == 'movie') & 
            (movies['genres'] != '\\N') &
            (movies['startYear'] != '\\N')
        ]
        
        # Convert year to numeric, dropping invalid values
        movies['startYear'] = pd.to_numeric(movies['startYear'], errors='coerce')
        movies = movies.dropna(subset=['startYear'])
        
        # Clean genres: replace \N with empty string and split by comma
        movies['genres'] = movies['genres'].str.replace('\\N', '')
        movies['genres'] = movies['genres'].str.replace(',', ' ')
        
        # Merge datasets
        logger.info("Merging datasets...")
        df = movies.merge(ratings, on='tconst', how='inner')
        
        # Create final dataset with clean column names
        final_df = df[
            (df['startYear'] >= 1970) &           # Modern movies
            (df['numVotes'] >= 10000) &           # Popular movies
            (df['averageRating'] >= 5.0)          # Well-rated movies
        ].copy()
        
        # Rename columns for clarity
        final_df = final_df.rename(columns={
            'primaryTitle': 'title',
            'startYear': 'year'
        })
        
        # Select and order final columns
        final_df = final_df[[
            'title',
            'year',
            'genres',
            'averageRating',
            'numVotes'
        ]]
        
        # Remove any remaining null values
        final_df = final_df.dropna()
        
        # Reset index
        final_df = final_df.reset_index(drop=True)
        
        logger.info(f"Data shape: {final_df.shape}")
        logger.info(f"Columns: {final_df.columns.tolist()}")
        logger.info(f"Sample genres: {final_df['genres'].head().tolist()}")
        
        # Cache the processed data
        logger.info("Caching processed data...")
        CACHE_DIR.mkdir(exist_ok=True)
        joblib.dump(final_df, PROCESSED_DATA_CACHE)
        
        logger.info(f"Successfully loaded {len(final_df)} movies")
        return final_df
        
    except Exception as e:
        logger.error(f"Error loading movie data: {str(e)}")
        raise