import requests
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MoviePosterAPI:
    def __init__(self, api_token=None):
        # Get API key from environment variable
        self.api_key = os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found in environment variables")
        self.base_url = "https://api.themoviedb.org/3"
        
    def search_movie(self, title, year=None):
        """Search for a movie and get its poster"""
        try:
            # Search for the movie
            search_url = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': title,
                'year': year if year else None
            }
            
            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                # Get the first movie's poster
                first_movie = results[0]
                poster_path = first_movie.get('poster_path')
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"
            
            return None
            
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None:
                st.error(f"Error fetching poster: {e.response.status_code} - {e.response.text}")
            else:
                st.error(f"Error fetching poster: {str(e)}")
            return None

@st.cache_data
def get_movie_poster(api_token, title, year=None):
    """Cached function to get movie poster URL"""
    # We don't need the api_token anymore since we're using TMDB
    poster_api = MoviePosterAPI()
    return poster_api.search_movie(title, year)