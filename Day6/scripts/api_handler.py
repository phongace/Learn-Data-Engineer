import requests
import pandas as pd
import os
from datetime import datetime


def create_output_dir(dir_path):
    """Create output directory if it doesn't exist"""
    os.makedirs(dir_path, exist_ok=True)


def generate_filename(prefix, directory):
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(directory, f"{prefix}_{timestamp}.csv")


def fetch_and_save_data(
    api_url="https://jsonplaceholder.typicode.com/posts",
    output_dir="/data/output",
    file_prefix="api_data",
):
    """
    Fetch data from API and save to CSV

    Args:
        api_url (str): URL of the API endpoint
        output_dir (str): Directory to save the CSV file
        file_prefix (str): Prefix for the output filename

    Returns:
        str: Path to the saved CSV file
    """
    # Fetch data from API
    print(f"Fetching data from {api_url}")
    response = requests.get(api_url)
    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data)
    print(f"Retrieved {len(df)} records")

    # Create output directory and generate filename
    create_output_dir(output_dir)
    output_file = generate_filename(file_prefix, output_dir)

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

    return output_file


if __name__ == "__main__":
    # Test the function
    output_path = fetch_and_save_data()
    print(f"Test completed. File saved at: {output_path}")