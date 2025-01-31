import psycopg

from app.config_data.config import load_config

config = load_config('.env')


def get_db_connection():
    db_conn = psycopg.connect(
        host=config.db.db_host,
        dbname=config.db.database,
        user=config.db.db_user,
        password=config.db.db_password,
        # port=os.environ.get(config.db.)
    )
    return db_conn
