#!/usr/bin/env python3
"""
Initialize PostGIS extension for Heroku PostgreSQL database
"""
import os
import psycopg2
import sys
from urllib.parse import urlparse

def enable_postgis():
    """Enable PostGIS extension in the database"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL environment variable not found")
        return False
    
    # Parse database URL and convert postgres:// to postgresql:// if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if PostGIS is already installed
        cur.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
        postgis_exists = cur.fetchone()[0]
        
        if postgis_exists:
            print("PostGIS extension is already enabled")
        else:
            print("Enabling PostGIS extension...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            print("PostGIS extension enabled successfully")
        
        # Verify PostGIS version
        cur.execute("SELECT PostGIS_Version()")
        version = cur.fetchone()[0]
        print(f"PostGIS version: {version}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error enabling PostGIS: {e}")
        print("This is normal if PostGIS is not available on this PostgreSQL instance")
        print("The application will continue to work with basic geographic functionality")
        return False

if __name__ == "__main__":
    success = enable_postgis()
    sys.exit(0 if success else 1)