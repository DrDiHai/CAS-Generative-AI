from openai import OpenAI
import re
import json


# Utility class to handle AI interactions
class AIService:
    @staticmethod
    def get_recommendations(
        client: OpenAI, consolidated_candidates: str, max_retries: int = 5
    ) -> dict:
        """
        Use the OpenAI client to generate candidate recommendations.
        Ensures the response contains correctly formatted JSON with expected keys.
        Retries the process if validation fails.
        """
        retries = 0
        while retries < max_retries:
            print(f"Attempt {retries + 1} to fetch AI recommendations.")

            # Step 1: Generate AI response
            recommend_thread = client.beta.threads.create()
            client.beta.threads.messages.create(
                thread_id=recommend_thread.id,
                role="user",
                content=consolidated_candidates,
            )
            run = client.beta.threads.runs.create_and_poll(
                thread_id=recommend_thread.id,
                assistant_id="asst_yimCJNOsP1QyLiiqBU3DhosV",
            )

            if run.status != "completed":
                raise ValueError("AI completion failed")

            # Step 2: Extract AI-generated messages
            recommend_messages = list(
                client.beta.threads.messages.list(thread_id=recommend_thread.id)
            )
            response_text = recommend_messages[0].content[0].text.value

            # Step 3: Try extracting JSON using regex
            matches = re.findall(r"```json(.*?)```", response_text, re.DOTALL)
            extracted_json = matches[0].strip() if matches else None

            # Step 4: Validate the extracted JSON
            try:
                data = (
                    json.loads(extracted_json)
                    if extracted_json
                    else json.loads(response_text)
                )
                assert "ranked_candidates" in data, "Missing 'ranked_candidates' key."
                assert "reason" in data, "Missing 'reason' key."
                print("Response validated successfully.")
                return data  # Success! Return the parsed JSON.
            except (json.JSONDecodeError, AssertionError) as e:
                print(f"Validation failed: {e}")
                print(f"Extracted JSON: {extracted_json}")

            # Retry logic
            print(f"Retrying... ({retries + 1}/{max_retries})")
            retries += 1

        # If all retries fail, raise an error
        raise ValueError(
            "Failed to get valid AI recommendations after multiple attempts."
        )
