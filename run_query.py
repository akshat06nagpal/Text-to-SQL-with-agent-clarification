import sqlite3

sql = "SELECT COUNT(*) FROM Track JOIN Genre ON Track.GenreId = Genre.GenreId WHERE Genre.Name = 'Rock';"

conn = sqlite3.connect("chinook.sqlite")
print(conn.execute(sql).fetchall())
conn.close()