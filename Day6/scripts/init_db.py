#!/usr/bin/env python3
"""
Database initialization script for the Token Data API.
Creates the tokens table and populates it with initial data from the API.
"""

import sys
import os
from sqlalchemy import create_engine, text
import traceback

# Import database handler functions
from db_handler import create_token_table, fetch_and_save_to_db


def init_database(db_url="postgresql://kestra:k3str4@localhost:5432/kestra"):
    """
    Initialize database for the Token Data API.
    Creates the tokens table and populates it with data if fetch_data is True.

    Args:
        db_url (str): Database connection URL

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Connecting to database: {db_url}")

        # Create database engine
        engine = create_engine(db_url)

        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print("Database connection successful!")

        # Create tokens table
        print("Creating tokens table...")
        tokens_table = create_token_table(engine)
        print("Tokens table created successfully!")

        # Fetch data from API and save to database
        print("Fetching initial data from API...")
        api_result = fetch_and_save_to_db(db_url=db_url)

        if api_result["status"] == "success":
            print(f"Successfully loaded {api_result['record_count']} token records.")
        else:
            print(f"Warning: Failed to fetch initial data: {api_result['message']}")

        print("Database initialization complete!")
        return True

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)