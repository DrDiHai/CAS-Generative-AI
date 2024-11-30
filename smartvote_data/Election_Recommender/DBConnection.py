import sqlite3

class DBConnection:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Allow row access by column name
        self.cursor = self.conn.cursor()

    def execute(self, query, params=()):
        try:
            self.cursor.close()
            self.cursor = self.conn.cursor()
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            print(len(params))
            raise  # Reraise the error so ye know what went awry
        return self.cursor.fetchall()
