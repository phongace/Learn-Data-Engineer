from flask import Flask, request, jsonify, send_file
import os
import traceback
from etl import extract_from_gcs, upload_to_gcs, load_to_bigquery, BUCKET_NAME

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        dest_blob = request.form.get("dest_blob", file.filename)
        file.save(file.filename)

        print(f"Attempting to upload to bucket: {BUCKET_NAME}")
        upload_success = upload_to_gcs(file.filename, dest_blob)
        os.remove(file.filename)

        if upload_success:
            return jsonify(
                {
                    "message": "File uploaded to GCS",
                    "bucket": BUCKET_NAME,
                    "blob": dest_blob,
                }
            )
        else:
            return jsonify({"error": "Failed to upload to GCS"}), 500
    except Exception as e:
        print(f"Upload error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/download", methods=["GET"])
def download():
    try:
        blob = request.args.get("blob")
        if not blob:
            return jsonify({"error": "No blob specified"}), 400

        local_file = request.args.get("local_file", blob)

        download_success = extract_from_gcs(blob, local_file)
        if download_success:
            return send_file(local_file, as_attachment=True)
        else:
            return jsonify({"error": "Failed to download from GCS"}), 500
    except Exception as e:
        print(f"Download error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/run-etl", methods=["POST"])
def run_etl():
    try:
        blob = request.json.get("blob")
        if not blob:
            return jsonify({"error": "No blob specified"}), 400

        local_file = request.json.get("local_file", "data.csv")
        dataset = request.json.get("dataset")
        table = request.json.get("table")

        if not dataset or not table:
            return jsonify({"error": "Dataset and table are required"}), 400

        extract_success = extract_from_gcs(blob, local_file)
        if not extract_success:
            return jsonify({"error": "Failed to extract from GCS"}), 500

        load_to_bigquery(dataset, table, local_file)
        return jsonify({"message": "ETL completed", "dataset": dataset, "table": table})
    except Exception as e:
        print(f"ETL error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)