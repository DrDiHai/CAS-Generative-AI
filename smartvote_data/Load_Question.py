# Beware, ye who seek to run this code! You'll need pandas and sqlite3. 
# Install pandas if ye haven't already:
# pip install pandas

import pandas as pd
import sqlite3

# Step 1: Load the Excel File into Pandas DataFrame
# 'excel_file.xlsx' be the map to the treasures within yer Excel file.
excel_file = 'C:\\Users\\DrDiHai\\Documents\\CAS Generative AI\\smartvote_data\\Codebook_sv_sr_candidates.xlsx'  # Name of the Excel file (replace with yer file's name)
sheet_name = 'SpiderDims'  # Name of the sheet within yer file, if any.

# Read the Excel file, columns will be plundered automatically, like the names of a thousand sunken ships!
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Step 2: Connect to SQLite Database (or create it if it doesn't exist)
# 'treasure.db' be the name of yer SQLite database, replace if need be!
conn = sqlite3.connect('staenderat.db')
cursor = conn.cursor()

# Step 3: Create a table based on the columns of the Excel file
# The table shall rise like the great Kraken, based on the DataFrame’s columns
table_name = 'Question'  # The name of yer table
columns = df.columns  # Fetch the column names from the Excel file, by the gods!
column_definitions = ', '.join([f"{col} TEXT" for col in columns])  # Assume text format for simplicity

# Ye olde SQL command to create a table
create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"
print(column_definitions)
cursor.execute(create_table_query)

# Step 4: Insert data into the SQLite table
# Here we insert row by row, casting the cursed Excel rows into the abyss of SQLite.
for _, row in df.iterrows():
    values = tuple(row)  # Turn the row into a tuple
    placeholders = ', '.join(['?' for _ in row])  # Create placeholders for the SQL insert command
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
    cursor.execute(insert_query, values)

# Step 5: Commit and close the connection before the Kraken wakes!
conn.commit()
conn.close()

print("The treasures from the Excel file have been safely stored in the SQLite database!")
