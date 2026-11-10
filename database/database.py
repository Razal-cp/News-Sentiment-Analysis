
import os
import boto3
import psycopg2


def get_db_connection():
    host = os.environ["DB_HOST"]
    port = int(os.environ.get("DB_PORT", "5432"))
    username = os.environ["DB_USER"]
    database = os.environ["DB_NAME"]
    region = os.environ.get("AWS_REGION", "ap-south-1")

    rds = boto3.client("rds", region_name=region)

    token = rds.generate_db_auth_token(
        DBHostname=host,
        Port=port,
        DBUsername=username
    )

    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=username,
        password=token,
        sslmode="require",
        connect_timeout=10
    )


def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_articles (
            id SERIAL PRIMARY KEY,
            title TEXT,
            description TEXT,
            source TEXT,
            url TEXT UNIQUE,
            sentiment TEXT,
            sentiment_score FLOAT,
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()

    print("News articles table created successfully!")


if __name__ == "__main__":
    create_table()

