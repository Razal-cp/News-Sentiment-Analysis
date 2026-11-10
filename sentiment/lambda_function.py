import psycopg2
import json
import os
import boto3
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

s3 = boto3.client("s3")
analyzer = SentimentIntensityAnalyzer()


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

def save_articles_to_database(articles):
    connection = get_db_connection()
    cursor = connection.cursor()

    for article in articles:
        published_at = article.get("published_at")

        if published_at:
            published_at = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            ).astimezone(timezone.utc).replace(tzinfo=None)

        cursor.execute("""
            INSERT INTO news_articles
            (title, description, source, url,
             sentiment, sentiment_score, published_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """, (
            article.get("title"),
            article.get("description"),
            article.get("source"),
            article.get("url"),
            article.get("sentiment"),
            article.get("sentiment_score"),
            published_at
        ))

    connection.commit()
    cursor.close()
    connection.close()

    print("Articles saved to PostgreSQL successfully!")
S3_BUCKET = os.environ["S3_BUCKET"]


def lambda_handler(event, context):

    raw_key = event.get("s3_key")

    if not raw_key:
        raise ValueError("Please provide s3_key in the event")

    response = s3.get_object(
        Bucket=S3_BUCKET,
        Key=raw_key
    )

    news_data = json.loads(
        response["Body"].read().decode("utf-8")
    )

    articles = news_data.get("articles", [])
    analyzed_articles = []

    for article in articles:
        title = article.get("title") or ""
        description = article.get("description") or ""

        scores = analyzer.polarity_scores(
            title + " " + description
        )

        compound = scores["compound"]

        if compound >= 0.05:
            sentiment = "Positive"
        elif compound <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        analyzed_articles.append({
            "title": title,
            "description": description,
            "source": (article.get("source") or {}).get("name"),
            "url": article.get("url"),
            "published_at": article.get("publishedAt"),
            "sentiment": sentiment,
            "sentiment_score": compound
        })

    output = {
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(analyzed_articles),
        "articles": analyzed_articles
    }

    analyzed_key = (
        "analyzed-news/analyzed_"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + ".json"
    )

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=analyzed_key,
        Body=json.dumps(output, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json"
    )
    save_articles_to_database(analyzed_articles)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Sentiment analysis completed",
            "article_count": len(analyzed_articles),
            "s3_key": analyzed_key
        })
    }
import psycopg2
import json
import os
import boto3
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

s3 = boto3.client("s3")
analyzer = SentimentIntensityAnalyzer()


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

def save_articles_to_database(articles):
    connection = get_db_connection()
    cursor = connection.cursor()

    for article in articles:
        published_at = article.get("published_at")

        if published_at:
            published_at = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            ).astimezone(timezone.utc).replace(tzinfo=None)

        cursor.execute("""
            INSERT INTO news_articles
            (title, description, source, url,
             sentiment, sentiment_score, published_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """, (
            article.get("title"),
            article.get("description"),
            article.get("source"),
            article.get("url"),
            article.get("sentiment"),
            article.get("sentiment_score"),
            published_at
        ))

    connection.commit()
    cursor.close()
    connection.close()

    print("Articles saved to PostgreSQL successfully!")
S3_BUCKET = os.environ["S3_BUCKET"]


def lambda_handler(event, context):

    raw_key = event.get("s3_key")

    if not raw_key:
        raise ValueError("Please provide s3_key in the event")

    response = s3.get_object(
        Bucket=S3_BUCKET,
        Key=raw_key
    )

    news_data = json.loads(
        response["Body"].read().decode("utf-8")
    )

    articles = news_data.get("articles", [])
    analyzed_articles = []

    for article in articles:
        title = article.get("title") or ""
        description = article.get("description") or ""

        scores = analyzer.polarity_scores(
            title + " " + description
        )

        compound = scores["compound"]

        if compound >= 0.05:
            sentiment = "Positive"
        elif compound <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        analyzed_articles.append({
            "title": title,
            "description": description,
            "source": (article.get("source") or {}).get("name"),
            "url": article.get("url"),
            "published_at": article.get("publishedAt"),
            "sentiment": sentiment,
            "sentiment_score": compound
        })

    output = {
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(analyzed_articles),
        "articles": analyzed_articles
    }

    analyzed_key = (
        "analyzed-news/analyzed_"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + ".json"
    )

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=analyzed_key,
        Body=json.dumps(output, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json"
    )
    save_articles_to_database(analyzed_articles)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Sentiment analysis completed",
            "article_count": len(analyzed_articles),
            "s3_key": analyzed_key
        })
    }

