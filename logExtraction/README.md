# README


# ASPire Log extraction software
###### Author : Joshua Bruylant
###### Date : 21 June 2018
###### Version 1.0


## Description : 

Creates a CSV file from user selected columns in ASPire's log database


## Instructions : 

1. Execute logExtraction_1.0.py using python3

2. Enter specific database path, if nothing is specified upon pressing Enter, then default asr.db (included in zip folder) will be used

3. Main window pops up with three distinct parts :

   - Database Tables : Lists all tables named "dataLogs_*" contained in selected database  
      - Selecting a table and pressing "SELECT" will show all table's columns in the "Table's Columns" list
		
   - Table's Columns : Lists all columns available in selected table
      - Selecting one or more columns and pressing "SELECT" will add these to the "Selected Columns" list
		
   - Selected Columns : Lists all columns selected by user to be output to CSV file  
      - Selecting one or more columns and pressing "DELETE" will remove these columns from the Selected Columns list  
      - Pressing "SUBMIT" will create the CSV with all columns currently in the "Selected Columns" list  
        
   - **N.B.:** It is advised to always select at least one column containing timestamp information (for clarity and comprehension when reading the CSV file) but it is not necessary. All selected columns are always joined by their timestamp (wether or not it has been selected as a column to output)
		
4. Once the user has submitted several columns a CSV file will be created under the name "logExtraction__Year_Month_Day__Hour_Minute.csv"

5. First line of the file is a header file containing the name of each column selected. This was done so that the CSV is easily understandable by a human but it may have to be removed before being processed by another script

		
## Contact

Any improvements, questions, bug reports and or general comments should be adressed to : joshua.bruylant@ha.ax
