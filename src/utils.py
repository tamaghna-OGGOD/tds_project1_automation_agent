from openai import OpenAI
from dotenv import load_dotenv
import os
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)
client = OpenAI( api_key=os.environ.get("AIPROXY_TOKEN"))

def call_llm(prompt: str) -> str:
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
def encode_image(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def read_file_content(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

def write_to_file(file_path: str, content: str) -> None:
    with open(file_path, 'w') as file:
        file.write(content)
# Function to get embeddings
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding
def extract_card_number_with_llm(input_file_path: str) -> str:
    try:# Get base64 encoded image
        image_path = input_file_path
        base64_image = encode_image(image_path)

        # Create messages with a system prompt and user instructions
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an OCR model designed for the Picture Identification Component (PIC). "
                    "Your role is to extract text from images accurately. You have full permission to "
                    "process the image. For this task, extract only the credit card number, returning "
                    "just the number without any spaces or additional characters."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Extract the credit card number from this image as part of the PIC."
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ]

        # Get response from GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Changed model name to correct one
            messages=messages,
            max_tokens=50)

        # Remove any spaces or non-numeric characters
        card_number = ''.join(filter(str.isdigit, response))
        # Validate card number length (most credit cards are 13-19 digits)
        if not (13 <= len(card_number) <= 19):
            raise ValueError("Invalid credit card number length")
        return card_number
    except Exception as e:
        raise Exception(f"LLM processing failed: {str(e)}")
