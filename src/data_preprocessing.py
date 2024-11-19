import pandas as pd

def load_and_process_imdb_data(akas_path, ratings_path, basics_path):
    try:
        # Load datasets
        akas = pd.read_csv(akas_path, sep='\t', usecols=['titleId', 'title', 'region', 'isOriginalTitle'])
        ratings = pd.read_csv(ratings_path, sep='\t', usecols=['tconst', 'averageRating', 'numVotes'])
        basics = pd.read_csv(basics_path, sep='\t', usecols=['tconst', 'primaryTitle', 'startYear', 'genres'])

        # Debugging: Print data shapes
        print("Basics Data Shape:", basics.shape)
        print("Ratings Data Shape:", ratings.shape)
        print("Akas Data Shape:", akas.shape)

        # Merge datasets: Basics and Ratings
        merged = pd.merge(basics, ratings, on='tconst', how='inner')

        # Filter by movie type and valid startYear
        merged = merged[(merged['startYear'].notnull()) & (merged['startYear'] != '\\N')]
        merged['startYear'] = merged['startYear'].astype(int)

        # Filter movies with at least 1000 votes
        merged = merged[(merged['numVotes'] >= 1000)]

        # Rename and simplify columns
        merged = merged.rename(columns={
            'primaryTitle': 'title',
            'averageRating': 'rating',
            'startYear': 'year'
        })

        # Merge with Akas dataset
        merged = pd.merge(merged, akas, left_on='tconst', right_on='titleId', how='left')

        # Use only original titles or titles from 'US' region
        merged = merged[(merged['isOriginalTitle'] == 1) | (merged['region'] == 'US')]

        # Drop duplicates and unnecessary columns
        merged = merged[['title', 'year', 'genres', 'rating', 'numVotes']].drop_duplicates()

        # Fill missing genres with 'Unknown'
        merged['genres'] = merged['genres'].fillna('Unknown')

        return merged

    except KeyError as e:
        print(f"KeyError: {e}")
        print("Available columns in the problematic dataset:")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        raise
