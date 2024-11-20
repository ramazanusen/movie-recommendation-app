import pandas as pd

def load_movies():
    """
    IMDb verilerini yükle ve işle
    """
    print("📊 IMDb verileri yükleniyor...")
    
    try:
        # 1. Ratings verisini yükle
        print("1/3 Ratings yükleniyor...")
        ratings = pd.read_csv(
            'data/title.ratings.tsv',
            sep='\t'
        )
        print(f"Ratings sütunları: {ratings.columns.tolist()}")
        
        # 2. Basics verisini yükle
        print("2/3 Film bilgileri yükleniyor...")
        movies = pd.read_csv(
            'data/title.basics.tsv',
            sep='\t'
        )
        print(f"Movies sütunları: {movies.columns.tolist()}")
        
        # Sadece filmleri al
        movies = movies[
            (movies['titleType'] == 'movie') & 
            (movies['genres'] != '\\N') &
            (movies['startYear'] != '\\N')
        ]
        
        # Verileri birleştir
        print("🔄 Veriler birleştiriliyor...")
        df = movies.merge(ratings, on='tconst', how='inner')
        print(f"Birleştirilmiş veri sütunları: {df.columns.tolist()}")
        
        # Veri temizliği
        df['startYear'] = pd.to_numeric(df['startYear'], errors='coerce')
        
        # Final veri setini oluştur
        final_df = df[
            (df['startYear'] >= 1970) &           # Modern filmler
            (df['numVotes'] >= 10000) &           # Popüler filmler
            (df['averageRating'] >= 5.0)          # İyi puanlı filmler
        ].copy()
        
        # Sütunları düzenle
        final_df = final_df.rename(columns={
            'primaryTitle': 'title',
            'startYear': 'year',
            'averageRating': 'rating',
            'numVotes': 'votes'
        })
        
        # Son düzenlemeler
        final_df = final_df[[
            'title',
            'year',
            'genres',
            'rating',
            'votes'
        ]]
        
        # NA değerleri temizle ve index'i sıfırla
        final_df = final_df.dropna().reset_index(drop=True)
        
        print(f"✅ Toplam {len(final_df)} film başarıyla yüklendi")
        print(f"Final sütunlar: {final_df.columns.tolist()}")
        
        return final_df
        
    except Exception as e:
        print(f"❌ Veri yükleme hatası: {str(e)}")
        print("Mevcut sütunlar:")
        if 'df' in locals():
            print(df.columns.tolist())
        if 'final_df' in locals():
            print("Final sütunlar:", final_df.columns.tolist())
        raise