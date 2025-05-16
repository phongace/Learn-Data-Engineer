import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from google.cloud import bigquery

class Recommender:
    def __init__(self):
        self.client = bigquery.Client(project="learn-data-engineer-457903")
        self.df = self.load_data()

    def load_data(self):
        query = """
            SELECT id, name, artists, danceability, energy, tempo, valence
            FROM `learn-data-engineer-457903.data.data`
        """
        df = self.client.query(query).to_dataframe()
        print("Loaded data shape:", df.shape)
        return df

    def recommend(self, track_id, top_k=5):
        if track_id not in self.df['id'].values:
            raise ValueError("Track ID not found.")

        features = self.df[['danceability', 'energy', 'tempo', 'valence']]
        target_index = self.df[self.df['id'] == track_id].index[0]

        target_vector = features.iloc[[target_index]]  # 2D shape
        similarity_scores = cosine_similarity(target_vector, features)[0]

        sim_scores = list(enumerate(similarity_scores))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Bỏ chính nó đi [0] → lấy từ 1 đến top_k
        sim_indices = [i for i, _ in sim_scores[1:top_k + 1]]

        return self.df.iloc[sim_indices][['id', 'name', 'artists']].to_dict(orient='records')

recommender = Recommender()
