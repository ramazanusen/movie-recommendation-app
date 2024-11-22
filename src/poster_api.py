import requests
import streamlit as st
import os
from dotenv import load_dotenv
import logging
from functools import lru_cache
import json
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoviePosterAPI:
    def __init__(self, api_token=None):
        """Initialize the TMDB API client"""
        self.api_key = api_token or os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB API key not found")
            
        self.base_url = "https://api.themoviedb.org/3"
        
    def search_movie(self, title, year=None):
        """Search for a movie and get its poster"""
        try:
            # First search for the movie to get its ID
            search_url = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': title,
                'year': year if year else None,
                'include_adult': False,
                'language': 'en-US',
                'page': 1
            }
            
            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}
            
            # Search for the movie
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                logger.warning(f"No results found for movie: {title}")
                return None
                
            # Get the first movie's poster path
            poster_path = results[0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for movie '{title}': {str(e)}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing response for movie '{title}': {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching for movie '{title}': {str(e)}")
            return None

@st.cache_data(ttl=3600)  # Cache results for 1 hour
def get_movie_poster(api_token, title, year=None):
    """Cached function to get movie poster URL"""
    try:
        poster_api = MoviePosterAPI(api_token)
        return poster_api.search_movie(title, year)
    except Exception as e:
        logger.error(f"Error getting movie poster: {str(e)}")
        return None
