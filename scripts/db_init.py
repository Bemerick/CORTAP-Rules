"""
Database initialization script for FTA Comprehensive Review Application
Creates the database schema and prepares for data loading
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the database if it doesn't exist"""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database='postgres'  # Connect to default database
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    db_name = os.getenv('DB_NAME', 'fta_review')

    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f'CREATE DATABASE {db_name}')
        print(f"Database '{db_name}' created successfully")
    else:
        print(f"Database '{db_name}' already exists")

    cursor.close()
    conn.close()

def initialize_schema():
    """Initialize the database schema"""
    # Connect to the FTA database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'fta_review')
    )
    cursor = conn.cursor()

    # Read and execute schema file
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    try:
        cursor.execute(schema_sql)
        conn.commit()
        print("Database schema initialized successfully")
    except Exception as e:
        conn.rollback()
        print(f"Error initializing schema: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Main initialization function"""
    print("Starting database initialization...")

    # Create database
    create_database()

    # Initialize schema
    initialize_schema()

    print("Database initialization complete!")

if __name__ == '__main__':
    main()
