from DBConnection import DBConnection
import sqlite3
import json

# Utility class to handle database operations
class DatabaseService:

    @staticmethod
    def save_alterations(connection: DBConnection, variant_key: str, alterations: dict) -> None:
        """
        Save alterations to the CandidateAlterations table.
        """
        alterations_json = json.dumps(alterations)  # Convert alterations to JSON
        query = """
            INSERT OR REPLACE INTO CandidateAlterations (Variant_Key, Alterations)
            VALUES (?, ?)
        """
        connection.execute(query, (variant_key, alterations_json))

    @staticmethod
    def get_alterations(connection: DBConnection, variant_key: str) -> dict:
        """
        Retrieve alterations from the CandidateAlterations table.
        """
        query = "SELECT Alterations FROM CandidateAlterations WHERE Variant_Key = ?"
        result = connection.execute(query, (variant_key,))
        if result:
            return json.loads(result[0]["Alterations"])  # Decode JSON into a dictionary
        return {}

    @staticmethod
    def get_last_run_id(connection: DBConnection, election_id: int) -> int:
        """
        Retrieve the last run ID for a given election.
        """
        query = "SELECT MAX(ID_run) AS last_run FROM ElectionRun"
        last_run = connection.execute(query, ())
        query = "SELECT MAX(ID_run) AS last_run FROM ElectionRecommendation"
        last_run_recom = connection.execute(query, ())
        max1 = last_run[0]["last_run"]
        max2 = last_run_recom[0]["last_run"]
        return max(max1, max2) if max1 is not None and max2 is not None else max1 if max1 is not None else max2 if max2 is not None else 0

    @staticmethod
    def insert_recommendations_with_variant(connection: DBConnection, election_id: int, run_id: int, 
                                        ranked_candidates: list, reasoning: str, variant_key: str, ai_response: str):
        """
        Insert ranked candidates and reasoning into the database, including a Variant_Key.
        """

        insert_metadata = """
            INSERT INTO ElectionRun (Full_ID_election, ID_run, Reasoning, Variant_Key, AI_Response, Date) VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        try:
            connection.execute(insert_metadata, (election_id, run_id, reasoning, variant_key, str(ai_response)))
        except sqlite3.IntegrityError as e:
            print(insert_metadata, election_id, run_id, reasoning, variant_key, str(ai_response))
            raise e

        insert_recommendations = """
            INSERT INTO ElectionRecommendation (ID_election, ID_run, ID_candidate, Rank) VALUES
        """
        values = [
            f" ({election_id}, {run_id}, {rec['id']}, {rec['rank']})"
            for rec in ranked_candidates
        ]
        try:
            connection.execute(insert_recommendations + ", ".join(values), ())
        except sqlite3.IntegrityError as e:
            print(insert_recommendations + ", ".join(values))
            raise e

    @staticmethod
    def get_gender(connection: DBConnection, gender_code: int):
        return connection.execute("SELECT name FROM Gender WHERE gender = ?", [gender_code])[0]["name"]
