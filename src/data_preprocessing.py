# src/data_preprocessing.py
import pandas as pd

def load_data(filepath):
    """
    Load the dataset from the provided file path.
    """
    try:
        data = pd.read_csv(filepath, sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])
        print("Data loaded successfully.")
        return data
    except FileNotFoundError:
        print(f"File not found. Please check the file path: {filepath}")
        return None

def preprocess_data(data, movies_filepath):
    """
    Preprocess the data by handling missing values and unnecessary columns,
    and join with movie titles, genres, and IMDb URLs.
    """
    # Drop unnecessary columns
    data.drop(columns=['timestamp'], inplace=True)

    # Load movies data with correct column names for u.item
    movies = pd.read_csv(movies_filepath, sep='|', names=['item_id', 'title', 'release_date', 'video_release_date', 
                                                          'IMDb_URL', 'unknown', 'Action', 'Adventure', 'Animation', 
                                                          'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 
                                                          'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 
                                                          'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'], 
                         usecols=['item_id', 'title', 'release_date', 'IMDb_URL', 'Action', 'Adventure', 
                                  'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 
                                  'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 
                                  'Sci-Fi', 'Thriller', 'War', 'Western'], encoding='latin-1')

    # Extract year from release_date
    movies['year'] = movies['release_date'].str.extract(r'(\d{4})').astype(float)
    
    # Combine genres into a single 'genres' column
    genre_columns = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 
                     'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 
                     'War', 'Western']
    movies['genres'] = movies[genre_columns].apply(lambda row: ' '.join([genre for genre, present in zip(genre_columns, row) if present == 1]), axis=1)

    # Drop individual genre columns after combining
    movies.drop(columns=genre_columns, inplace=True)

    # Merge datasets on item_id
    data = pd.merge(data, movies, on='item_id')

    # Check the processed data
    print("Processed data with genres, IMDb URL, and year columns:")
    print(data.head())

    return data
