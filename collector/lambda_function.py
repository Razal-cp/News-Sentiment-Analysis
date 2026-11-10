
import json
import os
import boto3
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

s3 = boto3.client("s3")
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "label": label,
        "compound": compound,
        "scores": scores
    }


def lambda_handler(event, context):
    api_key = os.environ["NEWS_API_KEY"]
    bucket = os.environ["S3_BUCKET"]

    params = urllib.parse.urlencode({
        "q": "technology",
        "language": "en",
        "pageSize": 20,
        "apiKey": api_key
    })

    url = "https://newsapi.org/v2/everything?" + params

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NewsSentimentProject/1.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        news_data = json.loads(response.read().decode("utf-8"))

    if news_data.get("status") != "ok":
        raise RuntimeError("News API request failed")

    articles = news_data.get("articles", [])

    for article in articles:
        text = " ".join(
            str(article.get(field) or "")
            for field in ("title", "description", "content")
        )
        article["sentiment"] = analyze_sentiment(text)

    timestamp = datetime.now(timezone.utc)

    output = {
        "fetched_at": timestamp.isoformat(),
        "total_results": news_data.get("totalResults", 0),
        "article_count": len(articles),
        "articles": articles
    }

    key = (
        "analyzed-news/news_"
        + timestamp.strftime("%Y%m%dT%H%M%SZ")
        + ".json"
    )

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(output, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "News sentiment analysis completed",
            "article_count": len(articles),
            "s3_key": key
        })
    }

