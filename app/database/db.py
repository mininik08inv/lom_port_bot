import psycopg
import os

from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_conn = psycopg.connect(
        host=os.environ.get('POSTGRES_HOST'),
        dbname=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        port=os.environ.get('POSTGRES_PORT')
    )
    return db_conn