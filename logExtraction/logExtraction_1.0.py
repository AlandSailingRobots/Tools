import sys
import sqlite3
from pathlib import Path
from tkinter import *
import csv
import datetime
import re

now = datetime.datetime.now()

"""
ASPire Log extraction software
Author : Joshua Bruylant
Date : 21 June 2018
Version 1.0


Description : 
Creates a CSV file from user selected columns in ASPire's log database
"""

#Global variables
selectedTable = []
selectedColumns = []
outputList = []

listWidth = 30
buttonWidth = 7
hPadding = 0

"""
Asks use to input his database and checks if it exists.
If user inputs nothing, default database is selected
If db doesn't exist, asks user to try again
Once correct database is selected, connects to it
"""
dbFoundFlag = 0
while dbFoundFlag == 0:
	dbPath = input("\nYosh welcomes you! Please enter your database path (Leave blank to use default asr.db): ")
	dbPathFile = Path(dbPath)
	if not dbPath:
		dbPath = './asr.db'
		break
	if dbPathFile.is_file():
		dbFoundFlag = 1
	else:
		print("Yosh hasn't found the database or it doesn't exist, please try again")
	
conn = sqlite3.connect(dbPath)
c = conn.cursor()

#Get all database's tables
c.execute('SELECT name FROM main.sqlite_master WHERE type=\'table\'')
allTables = c.fetchall()

#Keep only the 'dataLogs' tables
dbTables=[]
for n in range(len(allTables)):
	#Each item in allTables is a tuple with this format : (table, ). Since it has two values (for some reason) we must keep only what is at index 0 of this tuple
	item = allTables[n][0]
	if re.match('^dataLogs_.*', str(item)):
		dbTables.append(item)



"""
TableList is a list of all database's tables

List on one side contains all tables from current database
User selects one and clicks "SELECT" button
This then shows all table's columns inside "ColumnList" (see below)
"""
class TableList:

	def __init__(self, master):
		
		global dbTables

		self.tableFrame = Frame(master, padx=hPadding)
		self.tableFrame.grid(row=0, column=0, sticky='w')
		
		self.tableTitle = Label(self.tableFrame, text="Database Tables", width=listWidth, padx=hPadding)
		self.tableTitle.grid(row=0, column=0)
		
		#Listbox displaying all tables, user can select one
		self.tableList = Listbox(self.tableFrame, selectmode=SINGLE, width=listWidth)
		self.tableList.grid(row = 1, column = 0, sticky='w')
		for item in dbTables:
			self.tableList.insert(END, item)
			
		#Table select button
		self.tableSelectButton = Button(self.tableFrame, text="SELECT", command=self.tableSelected, width=buttonWidth, padx=hPadding)
		self.tableSelectButton.grid(row=1, column=1, sticky='w')
		
	#When user clicks the SELECT button, gets all table's columns and inserts them into ColumnList's Listbox
	def tableSelected(self):
		
		global selectedTable
		
		if self.tableList.curselection():
			selectedTable = self.tableList.get(self.tableList.curselection())
		else:
			print("No table selected for Yosh!")
			return
			
		
		#Logging
		print("Table {0} selected - Yosh thanks you".format(selectedTable))
		
		#Get all tables' columns
		c.execute('PRAGMA table_info({0})'.format(selectedTable))
		tableColumns = c.fetchall()
		
		#Delete all column list to refresh display
		columnList.columnList.delete(0,END)
		#Insert columns into the columnList listbox
		for item in tableColumns:
			columnName = item[1]
			columnList.columnList.insert(END, columnName)

		
"""		
ColumnList is a list of all selected table's columns

List on one side containing all columns for current selected table
User can select several and they are added to the list of tables to add to csv file
"""
class ColumnList:

	def __init__(self, master):

		self.columnFrame = Frame(master, padx=hPadding)
		self.columnFrame.grid(row=0, column=1, sticky='w')
		
		self.columnTitle = Label(self.columnFrame, text="Table\'s Columns", width=listWidth, padx=hPadding)
		self.columnTitle.grid(row=0, column=0, padx=hPadding)
		
		#Listbox containing all columns for current table, updated in TableList
		self.columnList = Listbox(self.columnFrame, selectmode=EXTENDED, width=listWidth)
		self.columnList.grid(row = 1, column = 0, sticky='w')
		
		#Button for user to add columns to list of columns to port to CSV
		self.columnSelectButton = Button(self.columnFrame, text="SELECT", command=self.selectColumns, width=buttonWidth, padx=hPadding)
		self.columnSelectButton.grid(row=1, column=1, sticky='w')
	
	#When user clicks the SELECT button, gets all select columns and adds them to the outputList
	def selectColumns(self):
		
		global outputList
		global selectedTable
		
		#Get all columns selected by user
		selectedColumns = [self.columnList.get(item) for item in self.columnList.curselection()]
		
		#If user hasn't selected anything, warn him and don't do anything
		if not selectedColumns:
			print("No columns selected for Yosh!")
			return
		
		#If some of these items are not in the outputList already then add them to it
		for n in range(len(selectedColumns)):
			#Concatenate the table and the column in order to keep track of which column belongs to which table
			concatTableColumn = (selectedTable + '.' + selectedColumns[n])
			#Check to see if list has already been chosen
			if not concatTableColumn in outputList:
				print("Yosh is adding {0} to selected Columns".format(concatTableColumn))
				outputList.append(concatTableColumn)
			else:
				print("Yosh sees that column {0} is already present in selected list!".format(concatTableColumn))
				
		#Delete all chosen list to refresh display
		chosenList.chosenList.delete(0,END)
		#If some items in outputList are not displayed in the chosenList then add them to it
		for item in outputList:
			if not item in chosenList.chosenList.get(0, END):
				chosenList.chosenList.insert(END, item)
		
		
"""
ChosenList is the list containing all columns the user has chosen from using previous TableList and ColumnList

Three features : Visualising selected columns, deleting them from list and submitting
Submitting will take all columns and output a CSV file with all their data
"""
class ChosenList:
	
	def __init__(self,master):
		
		self.chosenFrame = Frame(master)
		self.chosenFrame.grid(row=1, column=0, columnspan=3, sticky='w')
		
		self.chosenButtonsFrame = Frame(self.chosenFrame)
		self.chosenButtonsFrame.grid(row=1, column=1)
		
		self.chosenTitle = Label(self.chosenFrame, text="Selected Columns")
		self.chosenTitle.grid(row=0, column=0)
		
		self.chosenList = Listbox(self.chosenFrame, selectmode=EXTENDED, width=2*listWidth + buttonWidth+1)
		self.chosenList.grid(row=1, column=0, sticky='w')
		
		self.submitButton = Button(self.chosenButtonsFrame, text = "SUBMIT", command=self.submitColumns, width=buttonWidth, padx=hPadding)
		self.submitButton.grid(row=0, column=0, sticky='w')
		
		self.deleteButton = Button(self.chosenButtonsFrame, text = "DELETE", command=self.deleteColumns, width=buttonWidth, padx=hPadding)
		self.deleteButton.grid(row=1, column=0, sticky='w')
	
	#All selected columns are output to a csv file
	def submitColumns(self):
		
		global outputList
		
		if not outputList:
			print("No columns to submit to Yosh!")
			return
		
		expression = createExecuteExpression(outputList)
		
		c.execute(expression)
		data = c.fetchall()
		
		writeToFile(data)
	
	
	#Deletes all columns selected by user from the outputList
	def deleteColumns(self):
		
		global outputList
		
		#Get all columns selected by user for deletion
		selectedChosens = [self.chosenList.get(item) for item in self.chosenList.curselection()]
		
		if not selectedChosens:
			print("Yosh notices that their are no columns to delete!")
			return
		
		#Go through the chosen list and remove all selected columns from outputList
		for n in range(len(selectedChosens)):
			if selectedChosens[n] in outputList:
				print("Yosh starts removing {0} from the Chosen List!".format(selectedChosens[n]))
				outputList.remove(selectedChosens[n])
				
			else:
				print("Yosh can't find {0} in the Chosen List!".format(selectedChosens[n]))
			
			#Delete all chosen list to refresh display
			chosenList.chosenList.delete(0,END)
			#Display the new outputList
			for item in outputList:
				if not item in chosenList.chosenList.get(0, END):
					self.chosenList.insert(END, item)
	
	
"""
createExecuteExpression receives outputList and returns a proper SQL expression to be executed by sqlite3's cursor

Joins all 'table.column' contained in outputList into a string to be inserted after the SELECT keyword
Extracts all table names to be insterted after FROM and sends them to the joinExpression function in order to create what is needed after the FROM
Puts the expression into format and returns it
"""
def createExecuteExpression(outputList):
	
	#String used after the SELECT instruction, need to be separated by commas
	columnsToSelect = ','.join(outputList)
	
	#Extract all table names from the outputList, used after the 'FROM' in our expression
	outputTables = []
	for n in range(len(outputList)):
		#Split outputList at the '.' and keep only first part, which is the table
		outputTables.append(outputList[n].split('.')[0])
	#Join all tables separated by commas to fit the expression's format
	outputTablesString = ','.join(outputTables)
	
	#String containing the name of first table, used as primary table
	firstTable = outputTables[0]
	
	#Create the expression to be executed
	expression = 'SELECT ' + columnsToSelect + ' FROM ' + firstTable + joinExpression(firstTable, outputTables)
	print("Yosh has generated this SQL expression for you :")
	print(expression)
	
	return expression


"""
joinExpression receives the first table and list of all output tables

Out of the outputTables list, extracts each unique table and removes the first one
For each unique table, creates an INNER JOIN expression and adds it to res before being returned
"""
def joinExpression(firstTable, outputTables):
	
	#res is the returned INNER JOIN part of the expression
	res = ''
	#uniqueTables contains all unique table names to avoid duplicates
	uniqueTables = []
	
	#For each unique word in outputTables, add that to uniqueTables and remove the first that who's timestamp serves as the primary key. This is done to avoid joining the primary table to itself
	for item in set(outputTables):
		uniqueTables.append(item)
	uniqueTables.remove(firstTable)
	
	#If there is more than just the primary table then start creating the INNER JOIN expression, otherwise return an empty result
	if len(uniqueTables)>=1:
		for n in range(len(uniqueTables)):
			res += ' INNER JOIN ' + uniqueTables[n] + ' ON ' + firstTable + '.t_timestamp = ' + uniqueTables[n] + '.t_timestamp'
			
		#FORMAT OF CREATED EXPRESSION : 
		#	INNER JOIN Table1 ON Table0.t_timestamp = Table1.t_timestamp
		#		INNER JOIN Table2 ON Table0.t_timestamp = Table2.t_timestamp
		#			etc
	else:
		res = ''
		
	res += ' ORDER BY ' + firstTable + '.t_timestamp ASC'

	return res

"""
writeToFile receives the data extracted from database and exports it to a csv file

Creates a new file with today's date up to the minute as its name
First writes a header to that file to indicate each column's name
Goes through all the data, removing the rows with null data (-2000)
Writes the rest to the file in a csv format
"""
def writeToFile(data):
	
	global outputList
	
	output = []
	#Create a string containing today's date up to the current minute
	todayDate = str(now.year) + '_' + str(now.month) + '_' + str(now.day) + '__' + str(now.hour) + '_' + str(now.minute)
	#Add to this string a name and extension
	dataFile = 'logExtraction__' + todayDate + '.csv'
	
	#Take length of first data tuple as an indicator of how many columns exist
	numberOfColumns = len(data[0])
	
	#Create the header, going through outputList (Format : table.column) and keeping only the second part, the column
	header = []
	for column in range(len(outputList)):
		header.append(outputList[column].split('.')[1])
	
	lines_seen = set() # holds lines already seen
	with open(dataFile, "w") as f:
		
		writer = csv.writer(f, lineterminator='\n')
		writer.writerow(header)
		
		#Go through each row, remove those that have null data and write the others to the csv file
		for rowNo in range(len(data)):
			line = 	data[rowNo] #Contains the line of data to process to csv
			
			if -2000 in line:
				pass #Null data found in database, do not write it to csv file
			else:
				if line not in lines_seen: #Not a duplicate
					lines_seen.add(line)
					writer.writerow(line)
				
		print("Yosh has finished exporting to " + dataFile)

	
root = Tk()
root.title("ASPire Log Extraction - Joshua Bruylant")
root.resizable(False, False)

tableList = TableList(root)
columnList = ColumnList(root)
chosenList = ChosenList(root)


root.mainloop()
