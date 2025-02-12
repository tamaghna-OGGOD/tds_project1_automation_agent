import re
from openai import OpenAI
from dotenv import load_dotenv
import os

# 1. Read the email content
with open('../../data/email.txt', 'r') as f:
    email_content = f.read()

# 2. Initialize OpenAI client
# Load environment variables from .env file two directories back
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=env_path)

# Initialize OpenAI client with API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# 3. Create prompt for the LLM
prompt = """
Extract only the sender's email address from this email message. 
Return just the email address without any other text.

Email content:
""" + email_content

# 4. Get response from LLM
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that extracts email addresses."},
        {"role": "user", "content": prompt}
    ]
)

# 5. Get the email address from response
sender_email = response.choices[0].message.content.strip()

# 6. Write to output file
with open('../../data/email-sender.txt', 'w') as f:
    f.write(sender_email)