import os
import pandas as pd
from google.cloud import bigquery

# Cấu hình GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

DATASET_ID = "data"
PROJECT_ID = "learn-data-engineer-457903"
CSV_DIR = "data/"
FILES = [
    "data_by_artist.csv",
    "data_by_genres.csv",
    "data_by_year.csv",
    "data_w_genres.csv",
    "data.csv"
]

# Khởi tạo BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Mapping schema cho từng file
schema_mapping = {
    "data_by_artist.csv": [
        {"name": "mode", "type": "INTEGER"},
        {"name": "count", "type": "INTEGER"},
        {"name": "acousticness", "type": "FLOAT"},
        {"name": "artists", "type": "STRING"},
        {"name": "danceability", "type": "FLOAT"},
        {"name": "duration_ms", "type": "FLOAT"},
        {"name": "energy", "type": "FLOAT"},
        {"name": "instrumentalness", "type": "FLOAT"},
        {"name": "liveness", "type": "FLOAT"},
        {"name": "loudness", "type": "FLOAT"},
        {"name": "speechiness", "type": "FLOAT"},
        {"name": "tempo", "type": "FLOAT"},
        {"name": "valence", "type": "FLOAT"},
        {"name": "popularity", "type": "FLOAT"},
        {"name": "key", "type": "INTEGER"}
    ],
    "data_by_genres.csv": [
        {"name": "mode", "type": "INTEGER"},
        {"name": "genres", "type": "STRING"},
        {"name": "acousticness", "type": "FLOAT"},
        {"name": "danceability", "type": "FLOAT"},
        {"name": "duration_ms", "type": "FLOAT"},
        {"name": "energy", "type": "FLOAT"},
        {"name": "instrumentalness", "type": "FLOAT"},
        {"name": "liveness", "type": "FLOAT"},
        {"name": "loudness", "type": "FLOAT"},
        {"name": "speechiness", "type": "FLOAT"},
        {"name": "tempo", "type": "FLOAT"},
        {"name": "valence", "type": "FLOAT"},
        {"name": "popularity", "type": "FLOAT"},
        {"name": "key", "type": "INTEGER"}
    ],
    "data_by_year.csv": [
        {"name": "mode", "type": "INTEGER"},
        {"name": "year", "type": "INTEGER"},
        {"name": "acousticness", "type": "FLOAT"},
        {"name": "danceability", "type": "FLOAT"},
        {"name": "duration_ms", "type": "FLOAT"},
        {"name": "energy", "type": "FLOAT"},
        {"name": "instrumentalness", "type": "FLOAT"},
        {"name": "liveness", "type": "FLOAT"},
        {"name": "loudness", "type": "FLOAT"},
        {"name": "speechiness", "type": "FLOAT"},
        {"name": "tempo", "type": "FLOAT"},
        {"name": "valence", "type": "FLOAT"},
        {"name": "popularity", "type": "FLOAT"},
        {"name": "key", "type": "INTEGER"}
    ],
    "data_w_genres.csv": [
        {"name": "genres", "type": "STRING"},
        {"name": "artists", "type": "STRING"},
        {"name": "acousticness", "type": "FLOAT"},
        {"name": "danceability", "type": "FLOAT"},
        {"name": "duration_ms", "type": "FLOAT"},
        {"name": "energy", "type": "FLOAT"},
        {"name": "instrumentalness", "type": "FLOAT"},
        {"name": "liveness", "type": "FLOAT"},
        {"name": "loudness", "type": "FLOAT"},
        {"name": "speechiness", "type": "FLOAT"},
        {"name": "tempo", "type": "FLOAT"},
        {"name": "valence", "type": "FLOAT"},
        {"name": "popularity", "type": "FLOAT"},
        {"name": "key", "type": "INTEGER"},
        {"name": "mode", "type": "INTEGER"},
        {"name": "count", "type": "INTEGER"}
    ],
    "data.csv": [
        {"name": "valence", "type": "FLOAT"},
        {"name": "year", "type": "INTEGER"},
        {"name": "acousticness", "type": "FLOAT"},
        {"name": "artists", "type": "STRING"},
        {"name": "danceability", "type": "FLOAT"},
        {"name": "duration_ms", "type": "INTEGER"},
        {"name": "energy", "type": "FLOAT"},
        {"name": "explicit", "type": "INTEGER"},
        {"name": "id", "type": "STRING"},
        {"name": "instrumentalness", "type": "FLOAT"},
        {"name": "key", "type": "INTEGER"},
        {"name": "liveness", "type": "FLOAT"},
        {"name": "loudness", "type": "FLOAT"},
        {"name": "mode", "type": "INTEGER"},
        {"name": "name", "type": "STRING"},
        {"name": "popularity", "type": "INTEGER"},
        {"name": "release_date", "type": "STRING"},
        {"name": "speechiness", "type": "FLOAT"},
        {"name": "tempo", "type": "FLOAT"}
    ]
}

# Upload function
def upload_csv_to_bigquery(file_name):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{file_name.replace('.csv', '')}"
    df = pd.read_csv(os.path.join(CSV_DIR, file_name))

    schema_fields = [bigquery.SchemaField(col["name"], col["type"]) for col in schema_mapping[file_name]]

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(
            schema=schema_fields,
            source_format=bigquery.SourceFormat.CSV,
            write_disposition="WRITE_TRUNCATE"
        ),
    )
    job.result()
    print(f"✅ Uploaded: {file_name} → {table_id}")

# Chạy chính
if __name__ == "__main__":
    for file in FILES:
        upload_csv_to_bigquery(file)
