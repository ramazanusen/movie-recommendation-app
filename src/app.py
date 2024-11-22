import streamlit as st
from data_loader import load_movies
from recommendation_engine import MovieRecommender
from poster_api import get_movie_poster
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="CineMatch | Your Personal Movie Guide",
    page_icon="🎬"
)

# Add custom CSS
st.markdown("""
    <style>
        .poster-container {
            width: 150px;
            height: 225px;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
            position: relative;
            transition: all 0.3s ease-out;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .poster-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 50%;
            height: 100%;
            background: linear-gradient(
                to right,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            transform: skewX(-25deg);
            transition: 0.5s;
            z-index: 1;
        }
        
        .poster-container:hover::before {
            left: 150%;
        }
        
        .poster-container:hover {
            transform: scale(1.1);
            z-index: 2;
            box-shadow: 
                0 8px 16px rgba(0,0,0,0.2),
                0 0 20px rgba(255,255,255,0.2);
        }
        
        .poster-inner img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            border-radius: 10px;
            transition: transform 0.3s ease-out;
        }
        
        .poster-container:hover .poster-inner img {
            transform: scale(1.05);
        }
        
        /* Style number input container */
        [data-testid="stNumberInput"] {
            width: 150px !important;
            margin-top: 0.5rem;
        }
        
        [data-testid="stNumberInput"] label {
            display: none;
        }
        
        [data-testid="stNumberInputField"] {
            text-align: center;
        }
        
        .movie-title {
            position: relative;
            display: inline-block;
            font-weight: 500;
            margin-top: 0.5rem;
            transition: color 0.3s ease;
        }
        
        .movie-title:hover {
            color: #ff4b4b;
        }
        
        .movie-card {
            display: inline-block;
            margin: 10px;
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .movie-card:hover {
            transform: translateY(-5px);
        }
    </style>
""", unsafe_allow_html=True)

def format_number(num):
    """Format numbers for better readability"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def create_google_search_url(movie_title, year):
    """Create a Google search URL for a movie"""
    query = f"{movie_title} {year} movie"
    return f"https://www.google.com/search?q={urllib.parse.quote(query)}"

def show_movie_title(title, year, url):
    """Display movie title with enhanced styling"""
    st.markdown(
        f"""
        <a href="{url}" target="_blank" style="text-decoration: none;">
            <h3 class="movie-title">{title} ({year})</h3>
        </a>
        """,
        unsafe_allow_html=True
    )

def show_no_poster_placeholder():
    """Display a placeholder when no movie poster is available"""
    st.markdown(
        """
        <style>
            .no-poster {
                width: 150px;
                height: 225px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #f0f2f6;
                border-radius: 10px;
                color: #666;
                text-align: center;
                font-size: 0.8em;
                padding: 10px;
            }
        </style>
        <div class="no-poster">
            No poster available
        </div>
        """,
        unsafe_allow_html=True
    )

def show_movie_poster(url, link_url):
    """Display a movie poster with consistent styling"""
    st.markdown(
        f"""
        <style>
            .poster-container {{
                width: 150px;
                height: 225px;
                border-radius: 10px;
                overflow: hidden;
                position: relative;
            }}
            
            .poster-container img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transition: box-shadow 0.3s;
            }}
            
            .poster-container:hover img {{
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }}
        </style>
        <div class="poster-container">
            <a href="{link_url}" target="_blank">
                <img src="{url}" alt="Movie Poster">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_movie_card(title, poster_url, genres, overview):
    """Display a movie card with poster and details"""
    if not poster_url:
        poster_url = "https://via.placeholder.com/150x225.png?text=No+Poster"
    
    html = f"""
    <div class="movie-card">
        <a href="https://www.google.com/search?q={urllib.parse.quote(f'{title} movie')}" target="_blank" style="text-decoration: none;">
            <div class="poster-container">
                <div class="poster-inner">
                    <img src="{poster_url}" alt="{title} poster">
                </div>
                <div class="poster-description">
                    <strong>Overview:</strong><br>
                    {overview[:200] + '...' if len(overview) > 200 else overview}<br><br>
                    <strong>Genres:</strong><br>
                    {genres}
                </div>
            </div>
            <h3 class="movie-title">{title}</h3>
        </a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def show_recommendations(recommender, movie_title, n_recommendations, api_token):
    """Display movie recommendations"""
    if not movie_title:
        st.warning("Please enter a movie title")
        return
            
    with st.spinner('🔄 Finding recommendations...'):
        try:
            recommendations = recommender.find_similar_movies(
                movie_title,
                n_recommendations
            )
            
            if recommendations:
                st.write("### 🎥 Recommended Movies:")
                for movie in recommendations:
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        # Get movie poster
                        poster_url = get_movie_poster(api_token, movie['title'], movie['year'])
                        
                        with col1:
                            if poster_url:
                                search_url = create_google_search_url(movie['title'], movie['year'])
                                show_movie_poster(poster_url, search_url)
                            else:
                                show_no_poster_placeholder()
                        
                        with col2:
                            search_url = create_google_search_url(movie['title'], movie['year'])
                            show_movie_title(movie['title'], movie['year'], search_url)
                            st.write(f"Genres: {' '.join(movie['genres'])}")
                        
                        with col3:
                            st.write(f"⭐ {movie['rating']:.1f}/10")
                            st.write(f"📊 {movie['similarity_score']:.1%} match")
                        
                        st.write("---")
            else:
                st.warning("⚠️ No movies found or couldn't make recommendations.")
        except Exception as e:
            st.error(f"Error finding recommendations: {str(e)}")

@st.cache_resource
def initialize_recommender():
    """Initialize and cache the recommendation system"""
    try:
        movies_df = load_movies()
        return MovieRecommender(movies_df)
    except Exception as e:
        st.error(f"Failed to initialize recommender: {str(e)}")
        return None

def main():
    st.title("🎬 CineMatch: Your Personal Movie Guide")
    st.write("Discover your next favorite movie with AI-powered recommendations")
    
    # Get API token from environment variables first, then try Streamlit secrets
    api_token = os.getenv('TMDB_API_KEY')
    if not api_token:
        try:
            api_token = st.secrets.tmdb_api_key
        except:
            pass
    
    if not api_token:
        st.error("⚠️ TMDB API key not found in environment variables or Streamlit secrets")
        return
    
    try:
        # Initialize session state
        if 'previous_search' not in st.session_state:
            st.session_state.previous_search = ""
            
        # Initialize recommender
        recommender = initialize_recommender()
        
        if recommender is None:
            st.error("Failed to initialize the recommendation system. Please try again later.")
            return
        
        # Create the search interface
        movie_title = st.text_input("🔍 Enter a movie title:")
        
        # Create a container for number input
        st.markdown('<div style="margin-top: 1rem;">Number of recommendations:</div>', unsafe_allow_html=True)
        n_recommendations = st.number_input(
            "Number of recommendations",
            min_value=5,
            max_value=20,
            value=10,
            step=1,
            label_visibility="visible"
        )
        
        # Show recommendations when input changes
        current_search = f"{movie_title}_{n_recommendations}"
        if current_search != st.session_state.previous_search:
            if movie_title:
                show_recommendations(recommender, movie_title, n_recommendations, api_token)
            st.session_state.previous_search = current_search
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()