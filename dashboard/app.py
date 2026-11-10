
import streamlit as st
import pandas as pd
import plotly.express as px
from database.database import get_db_connection

st.set_page_config(
    page_title="News Sentiment Dashboard",
    page_icon="📰",
    layout="wide"
)

st.title("📰 News Sentiment Analysis Dashboard")
st.write("Real-time news sentiment monitoring")

@st.cache_data(ttl=60)
def load_data():
    connection = get_db_connection()

    query = """
        SELECT title, description, source, url,
               sentiment, sentiment_score, published_at
        FROM news_articles
        ORDER BY published_at DESC
    """

    df = pd.read_sql_query(query, connection)
    connection.close()
    return df

try:
    df = load_data()

    if df.empty:
        st.warning("No news articles found in the database.")
    else:
        total = len(df)
        positive = len(df[df["sentiment"] == "Positive"])
        negative = len(df[df["sentiment"] == "Negative"])
        neutral = len(df[df["sentiment"] == "Neutral"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Articles", total)
        col2.metric("Positive", positive)
        col3.metric("Negative", negative)
        col4.metric("Neutral", neutral)

        st.divider()

        st.subheader("Sentiment Distribution")

        sentiment_counts = (
            df["sentiment"].value_counts().reset_index()
        )
        sentiment_counts.columns = ["Sentiment", "Count"]

        fig = px.pie(
            sentiment_counts,
            names="Sentiment",
            values="Count",
            title="News Sentiment Overview",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("News Articles")

        selected_sentiment = st.selectbox(
            "Filter by Sentiment",
            ["All", "Positive", "Negative", "Neutral"]
        )

        filtered_df = df.copy()

        if selected_sentiment != "All":
            filtered_df = filtered_df[
                filtered_df["sentiment"] == selected_sentiment
            ]

        for _, article in filtered_df.iterrows():

           st.markdown(f"### [{article['title']}]({article['url']})")

           st.write(article["description"])
           st.write("Source:", article["source"])
           st.write("Sentiment:", article["sentiment"])
           st.write("Sentiment Score:", article["sentiment_score"])

           st.divider()

except Exception as e:
    st.error(f"Dashboard error: {e}")

