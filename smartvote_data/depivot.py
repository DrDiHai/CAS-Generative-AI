import sqlite3
import pandas as pd

# Step 1: Connect to SQLite and fetch data from the cursed table
conn = sqlite3.connect('staenderat.db')
query = "SELECT * FROM Kandidat"
df = pd.read_sql_query(query, conn)
conn.close()

# Step 2: Identify the columns we be wantin' to depivot (answer_, comment_, cleavage_) and keep ID as the true compass
id_column = 'ID'  # Ye should replace this with whatever yer actual ID column be named
selected_columns = [id_column] + [col for col in df.columns if col.startswith('answer_') or col.startswith('comment_') or col.startswith('cleavage_')]

# Step 3: Depivot only those columns, keepin' the ID intact
depivoted_df = pd.melt(df[selected_columns], id_vars=[id_column], var_name='dimension', value_name='value')

# Step 4: Create a new column that be indicating whether it's an answer, comment, or cleavage
def classify_dimension(dimension):
    if dimension.startswith('answer_'):
        return 'answer'
    elif dimension.startswith('comment_'):
        return 'comment'
    elif dimension.startswith('cleavage_'):
        return 'cleavage'

depivoted_df['type'] = depivoted_df['dimension'].apply(classify_dimension)

# Step 5: Strip the 'answer_', 'comment_', or 'cleavage_' from the dimension column
depivoted_df['dimension'] = depivoted_df['dimension'].str.replace('answer_', '') \
                                                    .str.replace('comment_', '') \
                                                    .str.replace('cleavage_', '')

# Step 6: Store the resulting table back into SQLite
conn = sqlite3.connect('staenderat.db')
depivoted_df.to_sql('Answer', conn, if_exists='replace', index=False)
conn.close()
