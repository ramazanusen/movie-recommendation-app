# Movie Recommendation System

A sophisticated movie recommendation system built with Python and Streamlit, leveraging content-based filtering to suggest similar movies based on genres, ratings, and release years. The application provides an intuitive user interface for discovering movies similar to your favorites.

## Features

- Content-based movie recommendations using:
  - Genre matching
  - Rating similarity
  - Release year proximity
- Fuzzy string matching for flexible movie title search
- User-friendly Streamlit interface
- Detailed movie information display including:
  - Movie title and release year
  - Genre information
  - IMDb rating
  - Number of votes
  - Similarity score with the searched movie

## Project Structure

```
movie-recommendation-app/
├── data/                    # Data directory for movie datasets
├── models/                  # Directory for trained models
├── src/
│   ├── app.py              # Streamlit application
│   ├── config.py           # Configuration settings
│   ├── data_loader.py      # Data loading utilities
│   ├── data_preprocessing.py # Data preprocessing functions
│   ├── recommendation_engine.py # Core recommendation logic
│   └── recommender.py      # Recommendation system class
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ramazanusen/movie-recommendation-app.git
   cd movie-recommendation-app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On macOS/Linux
   myenv\Scripts\activate     # On Windows
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application:**
   ```bash
   streamlit run src/app.py
   ```

2. **Using the interface:**
   - Enter a movie title in the search box
   - Select the number of recommendations you want (5-20)
   - Click "Show Recommendations" to get similar movies
   - View detailed information about each recommended movie

## How It Works

The recommendation system uses content-based filtering with the following components:

1. **Data Preprocessing:**
   - Combines movie metadata including genres, ratings, and release years
   - Handles missing values and data normalization

2. **Recommendation Engine:**
   - Creates a content-based representation of movies
   - Uses cosine similarity to find similar movies
   - Implements fuzzy string matching for flexible title search

3. **User Interface:**
   - Streamlit-based web interface
   - Interactive elements for user input
   - Clear presentation of recommendations

## Dependencies

- pandas >= 1.3.0
- scikit-learn >= 0.24.0
- streamlit >= 1.0.0
- fuzzywuzzy >= 0.18.0
- python-Levenshtein >= 0.12.0
- numpy >= 1.19.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
