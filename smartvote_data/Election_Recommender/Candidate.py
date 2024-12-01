# Create an AI-Generated summary of a candidate
from answer_types import AnswerType
from openai import OpenAI
import os
from DBConnection import DBConnection
from DatabaseService import DatabaseService
from VariantKey import generate_variant_key


class Candidate:
    def __init__(self, db: DBConnection, client: OpenAI, ID_candidate: int):
        self.db = db
        self.client = client
        self.candidate_id = ID_candidate
        print(f"Creating candidate object for ID {ID_candidate}")
        data = self.db.execute(
            """SELECT Kandidat.*, 
        Canton.short_name AS canton_name,
        Denomination.name AS denomination_name,
        Language.short_name AS language_name,
        Gender.name AS gender_name,
        MaritalStatus.name AS marital_status_name,
        Education.name AS highest_education_name,
        CASE WHEN Kandidat.incumbent = 0 THEN 'Nicht bisherig' ELSE 'Bisherig im Amt' END AS Bisherig_explained
        FROM Kandidat
        LEFT JOIN Canton ON Kandidat.canton = Canton.canton_id
        LEFT JOIN Language ON Kandidat.language = Language.language_id
        LEFT JOIN Denomination ON Kandidat.denomination = Denomination.denomination
        LEFT JOIN Gender ON Kandidat.gender = gender.gender
        LEFT JOIN MaritalStatus ON Kandidat.marital_status = MaritalStatus.marital_status
        LEFT JOIN Education ON Education.education = Kandidat.highest_education
        WHERE Kandidat.ID = ?""",
            [ID_candidate],
        )
        if not data:
            raise ValueError(f"No candidate found with ID {ID_candidate}")
        if len(data) > 1:
            raise ValueError(f"Multiple candidates found with ID {ID_candidate}")
        self.data = data[0]

    def __getattr__(self, name):
        try:
            raw = self.data[name]
            if raw == "-9":
                return None  # Return None for missing data instead of '-9'
            return raw
        except KeyError:
            raise AttributeError(f"'Candidate' object has no attribute '{name}'")

    @property
    def reversed_gender(self):
        gender_code = int(self.gender)
        if int(self.gender) == 1:
            gender_code = 0
        else:
            gender_code = 1
        print(f"Reversed gender from {self.gender=} to {gender_code=}")
        return DatabaseService.get_gender(self.db, gender_code)

    def base_data(self, **kwargs):
        # Base dictionary of candidate properties
        base_data = {
            "Kanton": self.canton_name,
            "Partei": self.party_short,
            "Liste 1": self.list_place_1,
            "Liste 2": self.list_place_2,
            "Bisherig": self.Bisherig_explained,
            "PLZ": self.zip,
            "Stadt": self.city,
            "Land": self.country,
            "Sprache": self.language_name,
            "Geschlecht": self.gender_name,
            "Alter": self.age,
            "Konfession": self.denomination_name,
            "Familienstand": self.marital_status_name,
            "Anzahl Kinder": self.N_children,
            "Höchster Bildungsabschluss": self.highest_education_name,
            "Beruf": self.occupation,
            "Arbeitgeber": self.employers,
            "Finanzierungsbetrag": self.funding_amount,
            "Finanzierungskommentar": self.funding_comment,
            "Slogan": self.slogan,
            "Hobbies": self.hobbies,
            "Lieblingsbücher": self.fav_books,
            "Lieblingsfilme": self.fav_movies,
            "Lieblingsmusik": self.fav_music,
        }

        # Check if any property in the base data be overridden by kwargs
        for key, alt_property in kwargs.items():
            if key in base_data:  # If the key exists in base data
                # Replace the key's value with the alternative property value from self
                base_data[key] = getattr(self, alt_property, None)

        return base_data

    def base_profile(self, **kwargs):
        base_data = self.base_data(**kwargs)
        return self.create_profile(base_data, **kwargs)

    def create_profile(self, base_data, **kwargs):
        candidate_profile = "\n".join(
            [f"{item}: {base_data[item]}" for item in base_data if base_data[item]]
        )
        cleavages = self.fetch_candidate_answers(
            self.candidate_id, [AnswerType.CLEAVAGE]
        )
        if cleavages:
            candidate_profile += "\n\nPolitische Ausrichtung:\n"
            candidate_profile += cleavages

        if kwargs.get("use_base_profile", False):
            return candidate_profile

        comments = self.fetch_candidate_answers(self.candidate_id, [AnswerType.COMMENT])
        if comments:
            candidate_profile += "\n\nKommentare:\n"
            candidate_profile += comments
        return candidate_profile

    def __str__(self):
        return f"Kandidat {self.candidate_id}, zur Wahl in {self.election_id}"

    def __repr__(self):
        return (
            f"<Candidate(id={self.candidate_id}, election_id={self.election_id}, "
            f"party='{self.party_short}'>"
        )

    def summary(self, **kwargs):
        # Generate a unique key to identify candidate alterations
        variant_key = generate_variant_key(kwargs)

        if kwargs.get("reverse_gender_for_id"):
            if kwargs["reverse_gender_for_id"] == self.candidate_id:
                self.Geschlecht = self.reversed_gender

        # Check if summary exists in Candidate_Summary table
        summary_data = self.db.execute(
            "SELECT Summary FROM Candidate_Summary WHERE Candidate_ID = ? AND Election_ID = ? AND Variant_Key = ?",
            (self.candidate_id, self.ID_election, variant_key),
        )

        # Return existing summary if found
        if summary_data:
            print(
                f"Summary found for candidate {self.candidate_id} in election {self.ID_election}, variant {kwargs}"
            )
            return summary_data[0]["Summary"]

        # Otherwise, create a new summary, save it, and return it
        print(
            f"Creating new summary for candidate {self.candidate_id} in election {self.ID_election}, variant: {kwargs}"
        )

        new_summary = (
            self.base_profile(**kwargs)
            if kwargs.get("use_base_profile", False)
            else self.create_ai_summary(**kwargs)
        )

        print(f"New summary created: {new_summary}, saving to database")
        self.db.execute(
            "INSERT INTO Candidate_Summary (Candidate_ID, Election_ID, Variant_Key, Summary) VALUES (?, ?, ?, ?)",
            (self.candidate_id, self.ID_election, variant_key, new_summary),
        )
        return new_summary

    def create_ai_summary(self, **kwargs):
        # Create a new AI summary
        thread = self.client.beta.threads.create()
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=self.base_profile(**kwargs)
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id="asst_ALcWlyFGOirZjVDlS911iPxg",
        )

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            return list(messages)[0].content[0].text.value
        else:
            raise ValueError("AI completion failed")

    def fetch_candidate_answers(self, candidate_id, answer_types: list[AnswerType]):
        # SQL query to fetch the answers and comments
        query = """
        SELECT
        Answer.ID,
        Answer.dimension,
        Question.Text,
        COALESCE(Selection.Text, Answer.Value) AS AnswerText,
        Answer.Value,
        Answer.Type,
        CASE
            WHEN Answer.Type = 'comment' THEN Answer.Value
            ELSE NULL
        END AS Comment
        FROM Answer
        LEFT JOIN Question ON dimension = Question.ID
        LEFT JOIN Selection ON Selection.Selection = Question.Selection AND Selection.Weight = Answer.Value AND Answer."type" <> 'comment'
        WHERE Answer.ID = ?
        AND Answer.dimension NOT LIKE '%_REC%'
        AND Answer.Value IS NOT NULL
        ORDER BY Answer.ID, Question.ID;
        """

        # Execute the query with the candidate ID as parameter
        results = self.db.execute(query, (candidate_id,))

        # Dictionary to hold answers and comments by dimension
        answers_by_dimension = {}

        # Process each row and combine answer and comment
        for row in results:
            (
                answer_id,
                dimension,
                question_text,
                answer_text,
                value,
                answer_type,
                comment,
            ) = row

            if dimension not in answers_by_dimension:
                answers_by_dimension[dimension] = {
                    "question": question_text,
                    "answer": "",
                    "comment": "",
                    "cleavage_value": "",
                }

            if answer_type == "cleavage":
                answers_by_dimension[dimension]["cleavage_value"] = value
            elif answer_type == "answer":
                answers_by_dimension[dimension]["answer"] = answer_text
            elif answer_type == "comment":
                answers_by_dimension[dimension]["comment"] = comment

        # Build human-readable output by combining answers and comments
        readable_output = []
        for dimension, entry in answers_by_dimension.items():
            question = entry["question"]
            full_answer = ""
            if AnswerType.CLEAVAGE in answer_types and entry["cleavage_value"]:
                full_answer = ", ".join(
                    [cur for cur in [full_answer, entry["cleavage_value"]] if cur]
                )
            if AnswerType.ANSWER in answer_types and entry["answer"]:
                full_answer = ", ".join(
                    [cur for cur in [full_answer, entry["answer"]] if cur]
                )
            if AnswerType.COMMENT in answer_types and entry["comment"]:
                full_answer = ", ".join(
                    [cur for cur in [full_answer, entry["comment"]] if cur]
                )

            if full_answer:
                readable_output.append(f"Question: {question}\nAnswer: {full_answer}\n")

        return "\n".join(readable_output)
