import streamlit as st
from data_loader import load_movies
from recommender import MovieRecommender

def format_number(num):
    """
    Format numbers for better readability
    """
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

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
        # Load recommender
        recommender = initialize_recommender()
        
        if recommender is None:
            st.error("Failed to initialize the recommendation system. Please try again later.")
            return
        
        # Movie search
        movie_title = st.text_input("🔍 Enter a movie title:")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            n_recommendations = st.number_input(
                "Number of recommendations:",
                min_value=5,
                max_value=20,
                value=10
            )
        
        if st.button("🎯 Show Recommendations"):
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
                                    st.write(f"**{movie['title']}** ({movie['year']})")
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
                    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.write("Please try refreshing the page. If the problem persists, contact support.")

if __name__ == "__main__":
    main()
