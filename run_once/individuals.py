# only if missing classes
import sqlite3
connection = sqlite3.connect('test.db')
cursor = connection.cursor()

# cursor.execute("INSERT OR REPLACE INTO SelectedClasses (ClassNum) VALUES (?)", ['CSE 3200'])
# cursor.execute("INSERT OR REPLACE INTO SelectedClasses (ClassNum) VALUES (?)", ['CSE 3250'])
cursor.execute("INSERT OR REPLACE INTO SelectedClasses (ClassNum) VALUES (?)", ['CSE 4705'])
cursor.execute("INSERT OR REPLACE INTO SelectedClasses (ClassNum) VALUES (?)", ['CSE 3504'])
connection.commit()
connection.close()