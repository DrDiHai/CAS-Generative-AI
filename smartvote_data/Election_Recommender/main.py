from DBConnection import DBConnection
from Election import Election, CantonalElection
from openai import OpenAI
import os

if __name__ == "__main__":
    db_path = "staenderat.db"
    db = DBConnection(db_path)
    client = OpenAI() 
    for canton in range(1,2):
        election = CantonalElection([1084,1085], client, db, canton=canton)
        for _ in range(20):
            try:
                candidates = election.candidates()
                for candidate in candidates:
                    election.recommend_candidates(use_base_profile=True, reverse_gender_for_id=candidate.candidate_id)
                #election.recommend_candidates(use_base_profile=True)
                #election.recommend_candidates(use_base_profile=True, Geschlecht="reversed_gender")
            except Exception as e:
                print(f"Failed to recommend candidates for canton {canton}: {e}")
        