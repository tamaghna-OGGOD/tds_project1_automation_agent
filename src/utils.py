from openai import OpenAI
from dotenv import load_dotenv
import os

def call_llm(prompt: str) -> str:

    # Load environment variables from .env file two directories up
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)

    client = OpenAI( api_key=os.environ.get("AIPROXY_TOKEN"))

    # Get response from LLM using chat completions API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that gives whatever is asked."},
            {"role": "user", "content": prompt}
        ]
    )

    # Return the extracted email address from the LLM response
    return response.choices[0].message.content.strip()

def read_file_content(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

def write_to_file(file_path: str, content: str) -> None:
    with open(file_path, 'w') as file:
        file.write(content)