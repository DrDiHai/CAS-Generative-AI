# Step 1: Install the required packages
# pip install pandas PyPDF2 sqlite3

import pandas as pd
import sqlite3
import PyPDF2

# Function to extract the table from PDF
def extract_table_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        
        # Extract text from all pages
        for page in reader.pages:
            text += page.extract_text()

    # Clean the text and locate the table
    # Split lines and remove extra whitespace
    lines = text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    # In this example, we assume the table begins and ends between specific keywords.
    # This part needs tweaking depending on your file format and content.
    print(cleaned_lines)
    start_idx = cleaned_lines.index("ID_candidate")  # Modify this based on table start
    end_idx = cleaned_lines.index("age_REC6") + 1    # Modify this based on table end

    # Extract relevant table lines
    table_data = cleaned_lines[start_idx:end_idx]

    # Create a DataFrame from the extracted data (adjust the structure as needed)
    headers = table_data[:30]  # Extract column names, adjust based on actual table format
    rows = [row.split() for row in table_data[1:]]  # Split each row into columns

    # Create a pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    return df

# Step 2: Load extracted table data into SQLite
def load_data_into_sqlite(df, db_name, table_name):
    # Connect to SQLite database (or create it)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table with column names from DataFrame
    columns = df.columns
    column_defs = ', '.join([f"{col} TEXT" for col in columns])  # Assuming all text
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});"
    cursor.execute(create_table_query)

    # Insert data into the table
    for _, row in df.iterrows():
        placeholders = ', '.join(['?' for _ in row])
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders});"
        cursor.execute(insert_query, tuple(row))

    # Commit and close the connection
    conn.commit()
    conn.close()

# Path to yer PDF treasure map
pdf_file_path = 'smartvote_data\\Codebook_sv23_sr_candidates.pdf'

# Extract the table from the PDF
df = extract_table_from_pdf(pdf_file_path)

# Load the table into SQLite
database_name = 'treasure.db'
table_name = 'info'
load_data_into_sqlite(df, database_name, table_name)

print(f"The table has been successfully extracted from the PDF and stored into the {database_name} database!")
