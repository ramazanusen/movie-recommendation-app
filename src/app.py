# src/app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from data_preprocessing import load_data, preprocess_data
from recommendation_engine import create_similarity_matrix, get_recommendations

# Load .env file
load_dotenv()

# Get TMDb API key from .env
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def get_movie_poster_tmdb(title, year):
    """
    Retrieve the movie poster URL from TMDb API based on title and year.
    """
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&year={year}"
    response = requests.get(search_url)
    data = response.json()
    
    # Get the poster of the first matching movie in search results
    if data['results']:
        movie = data['results'][0]
        poster_path = movie.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

def get_movie_google_search_url(title, year):
    """
    Generate a Google search URL using the movie title and year.
    """
    search_query = f"{title} {int(year)}"
    formatted_query = search_query.replace(" ", "+")
    return f"https://www.google.com/search?q={formatted_query}"

def get_movie_google_images_search_url(title, year):
    """
    Generate a Google Images search URL using the movie title and year.
    """
    search_query = f"{title} {int(year)} movie poster"
    formatted_query = search_query.replace(" ", "+")
    return f"https://www.google.com/search?tbm=isch&q={formatted_query}"

# Load and preprocess data
data = load_data('data/u.data')
if data is not None:
    data = data.sample(1000, random_state=1)  # Working with a small subset of data
    data = preprocess_data(data, 'data/u.item')
    similarity_matrix = create_similarity_matrix(data)

# Dark mode CSS settings
st.markdown(
    """
    <style>
        /* General background and title color */
        .stApp {
            background-color: #1c1c1c;
            color: #f5f5f5;
        }
        
        /* Title */
        .title {
            color: #f5f5f5;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 30px;
        }
        
        /* Clickable card style */
        .card {
            background-color: #333333;
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
            color: #f5f5f5;
            text-decoration: none;
            display: block;
        }
        
        /* Movie title */
        .movie-title {
            font-size: 24px;
            color: #1e90ff;
            font-weight: bold;
            text-decoration: none;
        }
        
        /* Text input and button style */
        label {
            color: #f5f5f5;
        }
        
        input {
            background-color: #333333;
            color: #f5f5f5 !important;
            border: 1px solid #444444;
        }
        
        .stButton > button {
            background-color: #444444;
            color: #f5f5f5;
            font-size: 16px;
            border-radius: 8px;
            padding: 8px 16px;
            border: none;
        }
        
        .stButton > button:hover {
            background-color: #555555;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app layout
st.markdown('<div class="title">Movie Recommendation System</div>', unsafe_allow_html=True)

# Form structure for user input and recommendation system
with st.form(key='movie_form'):
    movie_title = st.text_input("Enter a movie title to get recommendations:")
    submit_button = st.form_submit_button(label="Recommend")

# Run the recommendation system after form submission
if submit_button and data is not None:
    recommendations = get_recommendations(movie_title, data, similarity_matrix)
    if recommendations:
        st.write("Top 10 recommendations:")
        for movie in recommendations:
            # Retrieve the movie's year from the data and create a Google search URL, then fetch the poster image from TMDb
            movie_data = data[data['title'] == movie].iloc[0]
            google_url = get_movie_google_search_url(movie, movie_data['year'])
            poster_url = get_movie_poster_tmdb(movie, movie_data['year'])

            # Clickable card structure: the entire card links to the Google URL
            st.markdown(f"""
                <a href="{google_url}" target="_blank" class="card">
                    <div>
                        <span class="movie-title">{movie}</span>
                    </div>
            """, unsafe_allow_html=True)

            # Display the poster if available
            if poster_url:
                st.markdown(
                    f'<a href="{google_url}" target="_blank"><img src="{poster_url}" width="150"></a>',
                    unsafe_allow_html=True
                )
            else:
                google_images_url = get_movie_google_images_search_url(movie, movie_data['year'])
                st.write(f"[Poster not available - Search on Google Images]({google_images_url})")
            
            st.markdown("</a>", unsafe_allow_html=True)
    else:
        st.write("No recommendations found.")
