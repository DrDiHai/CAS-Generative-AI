import re
import json
from Candidate import Candidate
from DBConnection import DBConnection
from DatabaseService import DatabaseService
from openai import OpenAI
from AIService import AIService
from VariantKey import generate_variant_key, store_or_fetch_variant_key  # Refactored functions

class Election:
    def __init__(self, ID_election: list[int], client: OpenAI, connection: DBConnection):
        self.id = max(ID_election)
        self.ids = ID_election
        self.client = client
        self.db = connection
        self._candidates: list[Candidate] = None

    def get_next_run_id(self) -> int:
        """
        Calculate the next run ID for this election.
        """
        return DatabaseService.get_last_run_id(self.db, self.id) + 1

    def candidates(self) -> list[Candidate]:
        """
        Retrieve the list of candidates for the elections specified in ID_election.
        ID_election is now a list of election IDs.
        """
        if self._candidates is None:
            # Prepare the query to match multiple election IDs
            query = f"SELECT ID FROM Kandidat WHERE ID_election IN ({','.join(['?' for _ in self.ids])})"
            
            # Execute the query using the list of election IDs
            candidate_ids = self.db.execute(query, tuple(self.ids))
            
            # Create Candidate objects for each retrieved ID
            self._candidates = [
                Candidate(self.db, self.client, candidate["ID"]) 
                for candidate in candidate_ids 
            ]
        return self._candidates

    def recommend_candidates(self, **kwargs) -> None:
        """
        Generate candidate recommendations, optionally applying alterations via kwargs.
        Save recommendations with a Variant_Key to identify changes.
        """
        # Generate or retrieve a Variant_Key based on kwargs
        variant_key = store_or_fetch_variant_key(self.db, kwargs)
        print(f"Generated Variant_Key: {variant_key}")

        # Consolidate altered candidate summaries
        consolidated_candidates = "\n".join(
            [
                f"\nKandidat Nummer {candidate.candidate_id}:\n\n{candidate.summary(**kwargs)}"
                for candidate in self.candidates()
            ]
        )

        try:
            # Get validated recommendations from the AI service
            data = AIService.get_recommendations(self.client, consolidated_candidates)

            ranked_candidates = data["ranked_candidates"]
            reasoning = data["reason"]

            # Save recommendations and reasoning with the Variant_Key
            DatabaseService.insert_recommendations_with_variant(
                self.db, self.id, self.get_next_run_id(), ranked_candidates, reasoning, variant_key, data
            )
            print("Recommendations successfully saved.")
        except ValueError as e:
            print(f"Failed to recommend candidates: {e}")
            raise e



class CantonalElection(Election):
    def __init__(self, ID_election: list[int], client: OpenAI, connection: DBConnection, canton: str):
        if not canton:
            raise ValueError("Canton must be provided for CantonalElection")
        super().__init__(ID_election, client, connection)
        self.canton = canton
        self.basic_id = max(ID_election)
        self.ids = ID_election
        self.id = self.basic_id * 100 + self.canton
        self.canton = canton
        print(self.ids)

    def candidates(self) -> list[Candidate]:
        """
        Retrieve the list of candidates for this cantonal election.
        """
        if self._candidates is None:
            # Prepare the query to match multiple election IDs
            query = f"SELECT ID FROM Kandidat WHERE ID_election IN ({','.join(['?' for _ in self.ids])}) AND canton = ?"
            
            # Execute the query using the list of election IDs
            param_list = self.ids
            param_list.append(self.canton)
            print(query)
            print(param_list)
            candidate_ids = self.db.execute(query, [str(id) for id in param_list])
            print(candidate_ids)
            
            # Create Candidate objects for each retrieved ID
            self._candidates = [
                Candidate(self.db, self.client, candidate["ID"]) 
                for candidate in candidate_ids 
            ]
        return self._candidates