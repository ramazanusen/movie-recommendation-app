# CineMatch: Advanced Movie Recommendation System

An AI-powered movie recommendation system that provides personalized movie suggestions based on genre matching, franchise detection, and sophisticated similarity scoring.

## Features

- Content-based movie recommendations
- Advanced genre categorization and matching
- Franchise and series detection
- Weighted similarity scoring
- Movie poster integration via TMDB API
- Modern, responsive UI with Streamlit
- Comprehensive error handling and logging

## Project Structure

```
recommendation_system_project/
├── data/                      # IMDb dataset files
│   ├── title.basics.tsv      # Movie basic information
│   └── title.ratings.tsv     # Movie ratings data
├── src/                      # Source code
│   ├── app.py               # Streamlit web interface
│   ├── recommendation_engine.py  # Core recommendation logic
│   ├── data_loader.py       # Data loading and processing
│   └── poster_api.py        # Movie poster API integration
├── .env                      # Environment variables
└── requirements.txt          # Project dependencies
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd recommendation_system_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the TMDB API key:
   - Get an API key from [TMDB](https://www.themoviedb.org/documentation/api)
   - Add your key to the `.env` file:
     ```
     TMDB_API_KEY=your_api_key_here
     ```

5. Download IMDb datasets:
   - The required files will be downloaded automatically on first run
   - Alternatively, download manually from [IMDb Datasets](https://datasets.imdbws.com/):
     - title.basics.tsv.gz
     - title.ratings.tsv.gz
   - Extract the files to the `data/` directory

6. Run the application:
   ```bash
   streamlit run src/app.py
   ```

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your TMDB API key:
   - Go to [TMDB Settings](https://www.themoviedb.org/settings/api) to get your API key
   - Copy `.streamlit/secrets.toml.template` to `.streamlit/secrets.toml`
   - Replace `your-api-key-here` with your actual TMDB API key in `secrets.toml`

4. Run the application:
   ```bash
   streamlit run src/app.py
   ```

## Security Notes

- Never commit your actual API keys or secrets to version control
- The `.env` and `.streamlit/secrets.toml` files are ignored by git for security
- Always use the template files as a reference for required secrets

## Usage

1. Enter a movie title in the search box
2. Select the number of recommendations (5-20)
3. View personalized movie recommendations with:
   - Movie posters
   - Similarity scores
   - Genre tags
   - Ratings and release years

## Recommendation Features

### Genre Categories
- Superhero Movies
- Crime/Mafia Films
- Animation
- Sci-Fi
- Action/Adventure

### Special Handling
- Franchise Detection (Marvel, DC, Batman, etc.)
- Series Matching (Godfather, Lord of the Rings, etc.)
- Genre-specific Weighting
- Temporal Relevance

## Data Processing

- Filters:
  * Movies from 1970 onwards
  * Minimum 10,000 votes
  * Minimum rating of 5.0
- Features used:
  * Genre matching
  * Release year proximity
  * Rating scores
  * Vote counts
  * Franchise/series matching

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
