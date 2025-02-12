from openai import OpenAI
import base64
import os
from dotenv import load_dotenv

def encode_image(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_card_number():
    # Load environment variables from .env file two directories back
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path=env_path)

    # Initialize OpenAI client with API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)
    
    # Get base64 encoded image
    image_path = r"D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\credit_card.png"
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
        max_tokens=50
    )

    # Extract card number and remove any spaces
    card_number = response.choices[0].message.content.strip()
    print(card_number)
    card_number = "".join(card_number.split())  # Remove all whitespace

    # Write to output file
    with open(r"D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\credit-card.txt", "w") as f:
        f.write(card_number)

if __name__ == "__main__":
    extract_card_number()