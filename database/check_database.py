from database.database import get_db_connection

connection = get_db_connection()
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM news_articles")

count = cursor.fetchone()[0]

print("Total articles in PostgreSQL:", count)

cursor.close()
connection.close()