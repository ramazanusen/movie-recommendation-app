import streamlit as st
from data_loader import load_movies
from recommender import MovieRecommender
from poster_api import get_movie_poster
import urllib.parse

# Configure the page
st.set_page_config(
    page_title="CineMatch | Your Personal Movie Guide",
    page_icon="🎬"
)

# Add custom CSS and JavaScript to the page
st.markdown("""
    <style>
        .poster-container {
            width: 150px;
            height: 225px;
            perspective: 1000px;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
            position: relative;
        }
        
        .poster-inner {
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.3s ease-out;
            display: block;
        }
        
        .poster-inner img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            border-radius: 10px;
        }
        
        .poster-container:hover .poster-inner {
            transform: 
                translateZ(30px)
                rotateX(10deg)
                rotateY(15deg)
                scale3d(1.1, 1.1, 1.1);
        }
        
        .poster-container::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                45deg,
                rgba(255,255,255,0) 0%,
                rgba(255,255,255,0.2) 100%
            );
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }
        
        .poster-container:hover::after {
            opacity: 1;
        }
        
        /* Movie title hover effect */
        .movie-title {
            position: relative;
            display: inline-block;
            transition: all 0.2s ease;
        }
        .movie-title::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 2px;
            bottom: -2px;
            left: 0;
            background-color: #1E88E5;
            transform: scaleX(0);
            transform-origin: bottom right;
            transition: transform 0.3s ease;
        }
        .movie-title:hover {
            color: #1565C0;
            transform: translateY(-1px);
        }
        .movie-title:hover::after {
            transform: scaleX(1);
            transform-origin: bottom left;
        }

        /* Number input width override */
        #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-13ln4jf.ea3mdgi5 > div > div > div > div:nth-child(8) > div {
            width: 300px !important;
        }
        
        /* Number input element width override */
        div.stNumberInput {
            width: 100px !important;
        }
        
        /* Show Recommendations button width override */
        .stButton {
            width: 100% !important;
        }
        .stButton button {
            width: 100% !important;
        }
        .stElementContainer {
            width: 100% !important;
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
        <div style="margin-bottom: 10px;">
            <a href="{url}" class="movie-title" style="
                font-size: 20px;
                font-weight: 600;
                color: #1E88E5;
                text-decoration: none;
                line-height: 1.3;
            ">{title}</a>
            <span style="
                font-size: 18px;
                color: #666;
                margin-left: 8px;
            ">({year})</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_no_poster_placeholder():
    """Display a placeholder when no movie poster is available"""
    st.markdown(
        """
        <div style="
            width: 150px;
            height: 225px;
            background-color: #f0f2f6;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: #666;
            font-size: 14px;
            padding: 10px;
            box-sizing: border-box;
        ">
            <div style="font-size: 40px; margin-bottom: 10px;">🎬</div>
            <div>No Poster Available</div>
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
                position: relative;
                width: 150px;
                height: 225px;
                transition: transform 0.3s;
            }}
            
            .poster-container:hover {{
                transform: translateY(-5px) scale(1.05);
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
                            st.write(f"Genres: {movie['genres']}")
                        
                        with col3:
                            st.write(f"⭐ {movie['rating']:.1f}/10")
                            st.write(f"👥 {format_number(movie['votes'])} votes")
                            st.write(f"📊 Similarity: {movie['similarity']:.1f}%")
                        
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
    
    # Set API token
    api_token = "386|Y22cNCVpuwXCSccFhFDvg8qfslFdLOzuIBOcCKC2"
    
    try:
        # Initialize session state
        if 'previous_search' not in st.session_state:
            st.session_state.previous_search = ""
        if 'previous_n_recommendations' not in st.session_state:
            st.session_state.previous_n_recommendations = 10
        
        # Load recommender
        recommender = initialize_recommender()
        
        if recommender is None:
            st.error("Failed to initialize the recommendation system. Please try again later.")
            return

        # Create the search interface
        movie_title = st.text_input("🔍 Enter a movie title:")
        
        # Number of recommendations input
        st.write("Number of recommendations:")
        n_recommendations = st.number_input(
            "",  # Empty label since we're using st.write above
            min_value=5,
            max_value=20,
            value=10,
            label_visibility="collapsed"
        )
            
        # Show recommendations button
        show_recommendations_button = st.button("🎯 Show Recommendations")
        
        # Trigger recommendations on button click, Enter key, or when number of recommendations changes
        if (show_recommendations_button or 
            (movie_title and movie_title != st.session_state.previous_search) or
            (movie_title and n_recommendations != st.session_state.previous_n_recommendations)):
            show_recommendations(recommender, movie_title, n_recommendations, api_token)
            st.session_state.previous_search = movie_title
            st.session_state.previous_n_recommendations = n_recommendations
                    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.write("Please try refreshing the page. If the problem persists, contact support.")

if __name__ == "__main__":
    main()
