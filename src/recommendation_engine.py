# src/recommendation_engine.py
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

def find_closest_title(title, data):
    """
    Find the closest matching title in the dataset based on fuzzy matching.
    """
    titles = data['title'].tolist()
    closest_match = process.extractOne(title, titles, scorer=fuzz.token_set_ratio)
    return closest_match[0] if closest_match[1] >= 60 else None  # Set a threshold (e.g., 60) for match quality

def create_similarity_matrix(data):
    """
    Create a similarity matrix using content-based filtering on genres.
    """
    count_vectorizer = CountVectorizer()
    profile_matrix = count_vectorizer.fit_transform(data['genres'])

    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(profile_matrix)
    return similarity_matrix

def get_recommendations(title, data, similarity_matrix):
    """
    Get movie recommendations based on a given movie title.
    """
    closest_title = find_closest_title(title, data)
    if not closest_title:
        print("No close match found in the dataset.")
        return []

    matched_indices = data[data['title'] == closest_title].index
    idx = matched_indices[0]
    
    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    seen_movies = set()
    top_movies = []
    input_title = data['title'][idx]

    for i in similarity_scores[1:]:
        movie_title = data['title'][i[0]]
        if movie_title.lower() != input_title.lower() and movie_title not in seen_movies:
            seen_movies.add(movie_title)
            top_movies.append(movie_title)
            if len(top_movies) == 10:
                break

    return top_movies
