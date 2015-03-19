import sqlite3

conn = sqlite3.connect('reddit_music.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE songs (artist varchar(32), song varchar(64), year number(4), subreddit varchar(16), url varchar(128), d date DEFAULT CURRENT_TIMESTAMP, submission_id varchar(6))''')

conn.commit()
conn.close()

