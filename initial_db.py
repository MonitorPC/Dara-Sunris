import os
from dotenv import load_dotenv
import psycopg2

# Load parameters from .env
load_dotenv()

# Database parameters
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_LOGIN = os.getenv("DB_LOGIN", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "carrot")
DB_NAME = os.getenv("DB_NAME", "db")

# Path to the SQL file
SQL_FILE_PATH = "initial.sql"


def execute_sql_from_file(file_path):
    """
    Reads an SQL file and executes the queries.
    """

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_LOGIN,
        password=DB_PASSWORD
    )
    
    with conn.cursor() as cur:
        with open(file_path, "r") as f:
            sql_commands = f.read()
            try:
                cur.execute(sql_commands)
            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Error executing query: {error}")
                conn.rollback()
                return
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    execute_sql_from_file(SQL_FILE_PATH)
    print(f"Queries from file '{SQL_FILE_PATH}' executed.")