import pandas as pd
import sqlalchemy as sa
import os
import json
import requests
import traceback
from datetime import datetime
import time
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    MetaData,
    create_engine,
    Text,
)
from sqlalchemy.dialects.postgresql import insert


def create_token_table(engine):
    """Create token table if it doesn't exist"""
    metadata = MetaData()

    # Define the token table with fields matching the API response
    tokens = Table(
        "tokens",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("name", String),
        Column("symbol", String),  # from "ticker" in the API
        Column("address", String, unique=True),
        Column("chain", String),
        Column("description", Text),  # New field from API
        Column("image_url", String),  # New field from API
        Column("price", Float),  # from "initPrice" in the API
        Column("market_cap", Float),  # from "lastMcap" in the API
        Column("volume_24h", Float),  # from "totalVolume" in the API
        Column("holders_count", Integer),  # from "totalHolders" in the API
        Column("top10_hold_percent", Float),  # New field from API
        Column("created_at", DateTime),
        Column("last_buy", DateTime),  # New field from API
        Column("fetch_time", DateTime),
        Column("is_migrated_to_dex", sa.Boolean),
    )

    # Create the table if it doesn't exist
    metadata.create_all(engine)

    return tokens


def fetch_and_save_to_db(
    api_url="https://tama.meme/api/tokenList?sortDirection=desc&sortBy=createdAt&page=1&limit=100&isMigratedToDex=false",
    db_url="postgresql://kestra:k3str4@localhost:5432/kestra",
    retry_count=3,
    retry_delay=5,
):
    """
    Fetch data from API and save to PostgreSQL database

    Args:
        api_url (str): URL of the API endpoint
        db_url (str): Database connection URL
        retry_count (int): Number of retry attempts
        retry_delay (int): Delay between retries in seconds

    Returns:
        dict: Operation result metadata
    """
    error_log = []
    success = False
    data = None
    fetch_time = datetime.now()

    # Create output for tracking
    result = {
        "status": "unknown",
        "message": "",
        "details": [],
        "timestamp": fetch_time.strftime("%Y-%m-%d %H:%M:%S"),
        "record_count": 0,
    }

    try:
        # Implement retry mechanism with exponential backoff
        for attempt in range(retry_count):
            current_delay = retry_delay * (2**attempt)
            try:
                print(
                    f"Attempt {attempt + 1} of {retry_count}: Fetching data from {api_url}"
                )

                # Set reasonable timeout and add headers
                headers = {"User-Agent": "Kestra-Workflow/1.0"}
                response = requests.get(api_url, timeout=30, headers=headers)

                # Handle HTTP errors with specific messaging
                response.raise_for_status()

                # Attempt to parse as JSON
                data = response.json()
                success = True
                break

            except Exception as e:
                error_msg = f"Error on attempt {attempt + 1}: {str(e)}"
                print(error_msg)
                error_log.append(error_msg)
                result["details"].append({"attempt": attempt + 1, "error": error_msg})

                # Don't wait after last attempt
                if attempt < retry_count - 1:
                    print(f"Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)

        # Handle case where all retries failed
        if not success:
            result["status"] = "failed"
            result["message"] = f"All {retry_count} attempts failed"
            raise Exception(
                f"All {retry_count} attempts failed. Errors: {'; '.join(error_log)}"
            )

        # Validate and process data
        if not data:
            result["status"] = "failed"
            result["message"] = "No data received from API"
            raise ValueError("No data received from API")

        # Extract data from the response - tokens are at the root level
        tokens_data = data
        if isinstance(data, dict) and "items" in data:
            tokens_data = data["items"]

        # Convert to DataFrame
        df = pd.DataFrame(tokens_data)

        if df.empty:
            result["status"] = "warning"
            result["message"] = "Empty dataset received from API"
            print("Warning: Empty dataset received from API")
            return result

        print(f"Retrieved {len(df)} records with {len(df.columns)} columns")
        print(f"Columns: {', '.join(df.columns.tolist())}")

        # Convert timestamp fields from milliseconds to datetime
        timestamp_cols = ["createdAt", "lastBuy"]
        for col in timestamp_cols:
            if col in df.columns:
                # Convert milliseconds to datetime, handling zeros
                df[col] = pd.to_datetime(df[col], unit="ms", errors="coerce")

        # Map API fields to database columns based on the actual API response
        df = df.rename(
            columns={
                "name": "name",
                "address": "address",
                "ticker": "symbol",
                "description": "description",
                "imageUrl": "image_url",
                "initPrice": "price",
                "lastMcap": "market_cap",
                "totalVolume": "volume_24h",
                "totalHolders": "holders_count",
                "top10HoldPercent": "top10_hold_percent",
                "createdAt": "created_at",
                "lastBuy": "last_buy",
                "isMigratedToDex": "is_migrated_to_dex",
            }
        )

        # Add fetch timestamp
        df["fetch_time"] = fetch_time

        # Create DB connection
        print(f"Connecting to database: {db_url}")
        engine = create_engine(db_url)

        # Create table if not exists
        tokens_table = create_token_table(engine)

        # Prepare data for PostgreSQL
        records = df.to_dict(orient="records")
        result["record_count"] = len(records)

        # Save to database using upsert (insert or update)
        with engine.begin() as conn:
            for record in records:
                # Clean up any None values
                cleaned_record = {k: v for k, v in record.items() if v is not None}

                # Use the PostgreSQL-specific upsert
                stmt = insert(tokens_table).values(**cleaned_record)

                # On conflict with unique address, update values
                update_dict = {
                    "name": stmt.excluded.name,
                    "symbol": stmt.excluded.symbol,
                    "description": stmt.excluded.description,
                    "image_url": stmt.excluded.image_url,
                    "price": stmt.excluded.price,
                    "market_cap": stmt.excluded.market_cap,
                    "volume_24h": stmt.excluded.volume_24h,
                    "holders_count": stmt.excluded.holders_count,
                    "top10_hold_percent": stmt.excluded.top10_hold_percent,
                    "last_buy": stmt.excluded.last_buy,
                    "fetch_time": stmt.excluded.fetch_time,
                    "is_migrated_to_dex": stmt.excluded.is_migrated_to_dex,
                }

                update_stmt = stmt.on_conflict_do_update(
                    index_elements=["address"], set_=update_dict
                )

                conn.execute(update_stmt)

        print(f"Successfully saved {len(records)} records to database")

        # Set success status
        result["status"] = "success"
        result["message"] = f"Successfully saved {len(records)} records to database"

        return result

    except Exception as e:
        result["status"] = "failed"
        if not result["message"]:
            result["message"] = str(e)

        print(f"Error in fetch_and_save_to_db: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")

        return result


# Function to get token data from database for API
def get_token_data(
    db_url="postgresql://kestra:k3str4@localhost:5432/kestra",
    limit=100,
    offset=0,
    sort_by="fetch_time",
    sort_direction="desc",
):
    """
    Get token data from the database

    Args:
        db_url (str): Database connection URL
        limit (int): Number of records to return
        offset (int): Offset for pagination
        sort_by (str): Column to sort by
        sort_direction (str): Sort direction (asc/desc)

    Returns:
        list: List of token records
    """
    try:
        # Create DB connection
        engine = create_engine(db_url)

        # Create SQL query
        query = f"""
        SELECT * FROM tokens
        ORDER BY {sort_by} {sort_direction}
        LIMIT {limit} OFFSET {offset}
        """

        # Execute query and return results as dictionary
        df = pd.read_sql(query, engine)
        records = df.to_dict(orient="records")

        return records

    except Exception as e:
        print(f"Error getting token data: {str(e)}")
        return []


# Test the functions if running directly
if __name__ == "__main__":
    # Test fetch and save
    result = fetch_and_save_to_db()
    print(json.dumps(result, indent=2))

    # Test getting data
    records = get_token_data(limit=5)
    print(json.dumps(records, indent=2))