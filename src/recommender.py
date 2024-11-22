from fuzzywuzzy import process
import pandas as pd

class MovieRecommender:
    def __init__(self, movies_df):
        """
        Film öneri sistemi
        """
        print("🎬 Öneri sistemi hazırlanıyor...")
        self.movies = movies_df.copy()
        self.prepare_data()
        print("✅ Sistem hazır!")
    
    def prepare_data(self):
        """
        Veriyi hazırla
        """
        # Genre listelerini hazırla
        self.movies['genre_list'] = self.movies['genres'].str.split('|')
        
        # Yıl ve oy sayısına göre normalize edilmiş puanlar
        max_votes = self.movies['votes'].max()
        self.movies['vote_weight'] = self.movies['votes'] / max_votes
        
        current_year = pd.Timestamp.now().year
        self.movies['year_weight'] = 1 - ((current_year - self.movies['year']) / 100)
        self.movies.loc[self.movies['year_weight'] < 0, 'year_weight'] = 0
    
    def calculate_similarity(self, movie1_genres, movie2_genres):
        """
        İki film arasındaki tür benzerliğini hesapla
        """
        genres1 = set(movie1_genres)
        genres2 = set(movie2_genres)
        
        intersection = len(genres1.intersection(genres2))
        union = len(genres1.union(genres2))
        
        return intersection / union if union > 0 else 0
    
    def find_similar_movies(self, title, n_recommendations=10):
        """
        Benzer filmleri bul
        """
        try:
            # Film adı eşleştirmesi
            title_match = process.extractOne(title, self.movies['title'].tolist())
            if not title_match or title_match[1] < 85:
                print(f"⚠️ '{title}' filmi bulunamadı")
                return []
            
            matched_title = title_match[0]
            print(f"🎯 Eşleşen film: {matched_title}")
            
            # Hedef filmi bul
            target_movie = self.movies[self.movies['title'] == matched_title].iloc[0]
            target_genres = target_movie['genre_list']
            target_year = target_movie['year']
            
            # Benzer filmleri bul
            similar_movies = []
            
            for _, movie in self.movies.iterrows():
                if movie['title'] != matched_title:
                    # Tür benzerliği
                    genre_similarity = self.calculate_similarity(
                        target_genres,
                        movie['genre_list']
                    )
                    
                    # Yıl farkı
                    year_diff = abs(movie['year'] - target_year)
                    year_similarity = max(0, 1 - (year_diff / 50))
                    
                    # Final skor
                    final_score = (
                        genre_similarity * 0.4 +
                        year_similarity * 0.3 +
                        movie['vote_weight'] * 0.1 +
                        movie['year_weight'] * 0.2
                    )
                    
                    if final_score > 0:
                        similar_movies.append({
                            'title': movie['title'],
                            'year': int(movie['year']),
                            'rating': float(movie['rating']),
                            'genres': movie['genres'],
                            'votes': int(movie['votes']),
                            'similarity': round(final_score * 100, 1)
                        })
            
            # En iyi önerileri döndür
            recommendations = sorted(
                similar_movies,
                key=lambda x: x['similarity'],
                reverse=True
            )[:n_recommendations]
            
            print(f"✅ {len(recommendations)} film önerisi bulundu")
            return recommendations
            
        except Exception as e:
            print(f"❌ Öneri hatası: {str(e)}")
            return []