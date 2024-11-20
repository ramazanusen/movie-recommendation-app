from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
import numpy as np
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_similarity_matrix(data):
    """
    Create a similarity matrix based on movie content
    
    Args:
        data (pd.DataFrame): Movie data containing genres, rating, and year
        
    Returns:
        tuple: (processed_data, similarity_matrix)
    """
    try:
        # Create a content-based representation of movies
        data['content'] = (
            data['genres'].fillna('') + ' ' +
            (data['rating'] * 10).astype(int).astype(str) + ' ' +
            data['year'].astype(int).astype(str)
        )
        
        # Validate content creation
        if data['content'].isnull().any():
            logger.error("Found null values in content after preprocessing")
            raise ValueError("Invalid data: null values in content")
            
        count_vectorizer = CountVectorizer(
            tokenizer=lambda x: x.split(),
            token_pattern=r"(?u)\b\w+\b",
            min_df=2  # Ignore terms that appear in less than 2 documents
        )
        
        count_matrix = count_vectorizer.fit_transform(data['content'])
        similarity_matrix = cosine_similarity(count_matrix, count_matrix)
        
        return data, similarity_matrix
        
    except Exception as e:
        logger.error(f"Error creating similarity matrix: {str(e)}")
        raise

def get_recommendations(title, data, min_similarity=70, max_recommendations=10):
    """
    Get movie recommendations based on title
    
    Args:
        title (str): Movie title to find recommendations for
        data (pd.DataFrame): Movie data
        min_similarity (int): Minimum similarity score (0-100) for fuzzy matching
        max_recommendations (int): Maximum number of recommendations to return
        
    Returns:
        list: List of recommended movies with their details
    """
    try:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Invalid title: must be a non-empty string")
            
        filtered_data, similarity_matrix = create_similarity_matrix(data)
        title_to_index = {row['title']: idx for idx, row in filtered_data.iterrows()}

        # Find closest match using fuzzy matching
        closest_match = process.extractOne(title, list(title_to_index.keys()))
        if not closest_match or closest_match[1] < min_similarity:
            logger.info(f"No close matches found for title: {title}")
            return []

        matched_title = closest_match[0]
        movie_idx = title_to_index[matched_title]

        # Get similarity scores
        similarity_scores = list(enumerate(similarity_matrix[movie_idx]))
        sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        recommendations = []
        seen = set()

        for idx, score in sorted_scores:
            if len(recommendations) >= max_recommendations:
                break
                
            if idx == movie_idx:  # Skip the searched movie itself
                continue

            movie = filtered_data.iloc[idx]
            if movie['title'] not in seen:
                recommendations.append({
                    'title': movie['title'],
                    'rating': float(movie['rating']),
                    'year': int(movie['year']),
                    'genres': movie['genres'],
                    'similarity': float(score * 100)  # Convert to percentage
                })
                seen.add(movie['title'])

        return recommendations

    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise
