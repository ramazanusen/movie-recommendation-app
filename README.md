# Movie Recommendation App

A simple movie recommendation app built with Streamlit, using the TMDb API to fetch movie posters. This application suggests similar movies based on user input and provides links to Google searches for each recommended movie.

## Features
- Movie recommendations based on user input
- Movie posters fetched from TMDb API
- Links to Google search for each recommended movie
- Modern dark-themed UI

## Getting Started


## Prerequisites

- Python 3.x
- A TMDb API Key (sign up at https://www.themoviedb.org/ to get one)

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ramazanusen/movie-recommendation-app.git
   cd movie-recommendation-app

2. **Create a virtual environment:**
   
   python3 -m venv myenv
   source myenv/bin/activate  # On macOS/Linux
   myenv\Scripts\activate     # On Windows

4. **Install the required packages:**
   
   pip install -r requirements.txt   

5. **Set up environment variables:**
   
   Create a .env file in the project root and add your TMDb API key:
   TMDB_API_KEY=YOUR_API_KEY_HERE

6. **Run the application:**
   streamlit run src/app.py

   This will launch the Streamlit application, and you should see a local URL in the terminal. Open it in your browser to interact with the app.

Usage
1. Enter a movie title in the input field.
2. Click the "Recommend" button to get a list of similar movie recommendations.
3. Each recommendation includes:
      -Movie poster (if available from TMDb)
      -Link to Google search results for more information
4. The entire card, including the poster and title, is clickable and redirects to the movie's Google search.


Configuration
To update the .env file:

Replace YOUR_API_KEY_HERE with your actual TMDb API key.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgements
Streamlit - for the web application framework
TMDb API - for movie data and posters
