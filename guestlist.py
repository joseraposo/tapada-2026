import sqlite3

conn = sqlite3.connect("guests.db")

cursor = conn.cursor()

# cursor.execute("""
# DELETE FROM guests
# """
# )
#
# conn.commit()

cursor.execute("SELECT name FROM guests")
guest_list = cursor.fetchall()

for guest in guest_list:
    print(guest[0])

conn.close()