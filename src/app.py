import streamlit as st
from data_loader import load_movies
from recommender import MovieRecommender
from poster_api import get_movie_poster
import urllib.parse

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
                                st.image(poster_url, width=150)
                            else:
                                # Just show a placeholder without error
                                st.markdown("🎬")
                        
                        with col2:
                            search_url = create_google_search_url(movie['title'], movie['year'])
                            st.markdown(f"**[{movie['title']}]({search_url})** ({movie['year']})")
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
    st.title("🎬 Movie Recommendation System")
    st.write("Movie recommendations based on IMDb data")
    
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
        
        # Custom CSS for compact number input
        st.markdown("""
            <style>
            #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-13ln4jf.ea3mdgi5 > div > div > div > div:nth-child(7) > div {
                width: 100px !important;
                min-width: 100px !important;
            }
            div.stNumberInput > div > div > input {
                width: 100px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
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
