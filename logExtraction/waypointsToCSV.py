import sys
import csv
import sqlite3
from pathlib import Path

if not len(sys.argv) == 2:
	sys.exit('Arguments are as follow : <database>')
database = sys.argv[1]

dbPathFile = Path(database)
if not dbPathFile.is_file():
	sys.exit('Please provide database path as first parameter')


conn = sqlite3.connect(database)
c = conn.cursor()

c.execute('pragma table_info(current_Mission)')
columns = c.fetchall()
header=[]
for col in columns:
	header.append(col[1])

c.execute('SELECT * FROM current_Mission')
data = c.fetchall()


outputFile = 'current_Mission.csv'

with open(outputFile, "w") as f:
	
	writer = csv.writer(f, lineterminator='\n')

	writer.writerow(header)
	
	for row in data:
		writer.writerow(row)
