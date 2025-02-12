import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect(r'D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\ticket-sales.db')
cursor = conn.cursor()

# Execute the query to calculate total sales for "Gold" tickets
cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold';")
result = cursor.fetchone()[0]

# Write the result in /data/ticket-sales-gold.txt
with open(r'D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\ticket-sales-gold.txt', 'w') as file:
    file.write(str(result))

conn.close()