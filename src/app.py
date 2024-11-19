import streamlit as st
from data_loader import load_movies
from recommender import MovieRecommender
import urllib.parse

def format_number(num):
    """
    Format numbers for better readability
    """
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def create_google_search_url(movie_title, year):
    """
    Create a Google search URL for a movie
    """
    query = f"{movie_title} {year} movie"
    return f"https://www.google.com/search?q={urllib.parse.quote(query)}"

def show_recommendations(recommender, movie_title, n_recommendations):
    """
    Display movie recommendations
    """
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
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Create clickable movie title with Google search link
                            search_url = create_google_search_url(movie['title'], movie['year'])
                            st.markdown(f"**[{movie['title']}]({search_url})** ({movie['year']})")
                            st.write(f"Genres: {movie['genres']}")
                        
                        with col2:
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
    """
    Initialize and cache the recommendation system
    """
    try:
        movies_df = load_movies()
        return MovieRecommender(movies_df)
    except Exception as e:
        st.error(f"Failed to initialize recommender: {str(e)}")
        return None

def main():
    st.title("🎬 Movie Recommendation System")
    st.write("Movie recommendations based on IMDb data")
    
    try:
        # Initialize session state for previous search
        if 'previous_search' not in st.session_state:
            st.session_state.previous_search = ""
        
        # Load recommender
        recommender = initialize_recommender()
        
        if recommender is None:
            st.error("Failed to initialize the recommendation system. Please try again later.")
            return
        
        # Movie search with Enter key support
        movie_title = st.text_input("🔍 Enter a movie title and press Enter:")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            n_recommendations = st.number_input(
                "Number of recommendations:",
                min_value=5,
                max_value=20,
                value=10
            )
        
        # Show recommendations button
        show_recommendations_button = st.button("🎯 Show Recommendations")
        
        # Trigger recommendations on Enter key or button click
        if show_recommendations_button or (movie_title and movie_title != st.session_state.previous_search):
            show_recommendations(recommender, movie_title, n_recommendations)
            st.session_state.previous_search = movie_title
                    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.write("Please try refreshing the page. If the problem persists, contact support.")

if __name__ == "__main__":
    main()
