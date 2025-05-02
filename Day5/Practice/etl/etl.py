import os
import shutil
from google.cloud import storage, bigquery
import traceback

# Lấy tên bucket từ biến môi trường hoặc dùng bucket mặc định nếu không có
BUCKET_NAME = os.environ.get(
    "BUCKET_NAME", "bucket-test-unique-axle-457602-n6-20250428150827"
)


def extract_from_gcs(source_blob_name, destination_file_name):
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Downloaded {source_blob_name} to {destination_file_name}")
        return True
    except Exception as e:
        print(f"Error downloading from GCS: {e}")
        # Fall back to local if GCS fails
        try:
            local_bucket_dir = "/tmp/local_bucket"
            os.makedirs(local_bucket_dir, exist_ok=True)
            source_path = os.path.join(local_bucket_dir, source_blob_name)
            if os.path.exists(source_path):
                shutil.copy(source_path, destination_file_name)
                print(f"Locally copied {source_path} to {destination_file_name}")
                return True
            else:
                print(f"File {source_path} not found in local bucket")
                return False
        except Exception as local_e:
            print(f"Error in local fallback: {local_e}")
            return False


def upload_to_gcs(source_file_name, destination_blob_name):
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(
            f"Uploaded {source_file_name} to gs://{BUCKET_NAME}/{destination_blob_name}"
        )
        return True
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        # Fall back to local if GCS fails
        try:
            local_bucket_dir = "/tmp/local_bucket"
            os.makedirs(local_bucket_dir, exist_ok=True)
            destination_path = os.path.join(local_bucket_dir, destination_blob_name)
            shutil.copy(source_file_name, destination_path)
            print(f"Locally copied {source_file_name} to {destination_path}")
            return True
        except Exception as local_e:
            print(f"Error in local fallback: {local_e}")
            return False


def load_to_bigquery(dataset_id, table_id, source_file):
    try:
        # Initialize client
        client = bigquery.Client()

        # Make sure dataset exists
        try:
            dataset_ref = client.dataset(dataset_id)
            client.get_dataset(dataset_ref)
            print(f"Dataset {dataset_id} already exists")
        except Exception as e:
            print(f"Dataset {dataset_id} does not exist, creating it: {e}")
            # Create the dataset
            dataset = bigquery.Dataset(f"{client.project}.{dataset_id}")
            dataset.location = "US"
            client.create_dataset(dataset, exists_ok=True)
            print(f"Created dataset {client.project}.{dataset_id}")

        # Set up job config with CSV autodetect
        table_ref = client.dataset(dataset_id).table(table_id)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            autodetect=True,
            skip_leading_rows=1,
        )

        # Check if file exists and is readable
        if not os.path.exists(source_file):
            print(f"Error: Source file {source_file} does not exist")
            return False

        print(f"Loading file {source_file} to BigQuery table {dataset_id}.{table_id}")
        # Load data
        with open(source_file, "rb") as source_file_obj:
            job = client.load_table_from_file(
                source_file_obj, table_ref, job_config=job_config
            )

        # Wait for job to complete and get results
        result = job.result()

        # Get table to verify rows loaded
        table = client.get_table(table_ref)
        print(f"Loaded {table.num_rows} rows to BigQuery table {dataset_id}.{table_id}")
        return True
    except Exception as e:
        error_details = str(e)
        print(f"Error loading to BigQuery: {error_details}")
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")
        print(f"Would load {source_file} to BigQuery {dataset_id}.{table_id}")
        return False


if __name__ == "__main__":
    # Download file from GCS
    extract_from_gcs("data.csv", "data.csv")
    # Upload file to GCS (ví dụ)
    # upload_to_gcs("localfile.csv", "uploaded.csv")
    # Load vào BigQuery
    load_to_bigquery("test_dataset", "test_table", "data.csv")