import asyncio
import os
import re
import json
import sqlite3
import subprocess
import tempfile
from datetime import datetime
from glob import glob
from pathlib import Path
from shutil import which
import numpy as np  
import shutil                       

import requests
from utils import call_llm,get_embedding,extract_card_number_with_llm

class TaskExecutor:
    async def install_and_run_datagen_task(self, user_email: str):
        # Task A1: Install 'uv' if required and run datagen.py from remote URL with user_email argument.
        url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        if which("uv") is None:
            try:
                await asyncio.to_thread(subprocess.run, ["pip", "install", "uv"], check=True)
            except subprocess.CalledProcessError as e:
                raise Exception("Failed to install uv") from e

        try:
            response = await asyncio.to_thread(requests.get, url)
            if response.status_code != 200:
                raise Exception("Failed to download datagen.py")
            script_content = response.text
        except Exception as e:
            raise Exception("Error downloading datagen.py") from e

        temp_dir = r"D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent"
        os.makedirs(temp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir=temp_dir) as tmp:
            tmp.write(script_content)
            tmp_path = tmp.name
            print(tmp_path)
        

        try:
            await asyncio.to_thread(
                subprocess.run, ["python", tmp_path, user_email, "--root", "./data"], check=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception("Failed to run datagen.py script") from e
        finally:
            os.remove(tmp_path)

    async def format_markdown_task(self, task_description: str):
    # Task A2: Format /data/format.md using prettier@3.4.2 (assumed installed) in-place.
        npx_executable = shutil.which("npx") or shutil.which("npx.cmd")
        if npx_executable is None:
            raise Exception("npx executable not found. Please install Node.js and ensure npx is in your PATH")
            
        cmd = [npx_executable, "prettier@3.4.2", "--write", "../data/format.md"]
        try:
            await asyncio.to_thread(
                subprocess.run,
                cmd,
                check=True,
                capture_output=True,  # Capture stdout and stderr for debugging
                text=True
            )
        except FileNotFoundError as e:
            raise Exception("npx executable not found. Please install Node.js and ensure npx is in your PATH") from e
        except subprocess.CalledProcessError as e:
            # Include output details in the exception message for troubleshooting
            error_msg = f"Markdown formatting failed (exit code {e.returncode}). Output:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            raise Exception(error_msg) from e
    async def count_weekdays_task(self,task_description: str):
        input_file = "../data/dates.txt"
        output_file = "../data/dates-wednesdays.txt"

        try:
            # Read and create a list of all non-empty date strings from the input file.
            with open(input_file, "r") as f:
                dates_list = [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise Exception("Failed to read input file: " + str(e))
        
        # Construct a prompt asking the LLM to calculate the number of Wednesdays directly.
        prompt = f'''
        You are an AI assistant and an expert in handling date and time calculations.
        Given the following list of date strings (each in various formats such as "2025-01-01", "01/02/2025", "January 3, 2025", etc.),
        calculate the number of dates that fall on a Wednesday.
        Return only the integer result without any additional text.

        List of dates:
        {dates_list}
        '''
        
        try:
            # Retrieve the integer count from the LLM.
            response = await asyncio.to_thread(call_llm, prompt)
            result = response.strip()
            
            try:
                count = int(result)
            except ValueError:
                raise ValueError("LLM did not return a valid integer. Response: " + result)
            
            # Write the result to the output file.
            with open(output_file, "w") as f:
                f.write(str(count))
        except Exception as e:
            raise RuntimeError("Execution failed: " + str(e))


    async def sort_contacts_task(self, task_description: str):
        # Task A4: Sort contacts in /data/contacts.json by last_name then first_name.
        input_file = "../data/contacts.json"
        output_file = "../data/contacts-sorted.json"
        try:
            async with await asyncio.to_thread(open, input_file, "r") as f:
                contacts = json.load(f)
        except Exception as e:
            raise Exception("Failed to load contacts") from e

        sorted_contacts = sorted(
            contacts,
            key=lambda c: (c.get("last_name", "").lower(), c.get("first_name", "").lower()),
        )

        try:
            async with await asyncio.to_thread(open, output_file, "w") as f:
                json.dump(sorted_contacts, f, indent=2)
        except Exception as e:
            raise Exception("Failed to write sorted contacts") from e

    async def logs_recent_task(self, task_description: str):
        # Task A5: Write the first line of the 10 most recent .log files in /data/logs/ to /data/logs-recent.txt.
        folder = "../data/logs/"
        output_file = "../data/logs-recent.txt"
        log_files = glob(os.path.join(folder, "*.log"))
        if not log_files:
            raise Exception("No log files found")

        log_files_sorted = sorted(log_files, key=os.path.getmtime, reverse=True)[:10]
        lines = []
        for log_file in log_files_sorted:
            try:
                async with await asyncio.to_thread(open, log_file, "r") as f:
                    first_line = f.readline().strip()
                    lines.append(first_line)
            except Exception:
                continue

        try:
            async with await asyncio.to_thread(open, output_file, "w") as f:
                f.write("\n".join(lines))
        except Exception as e:
            raise Exception("Failed to write logs recent output") from e

    async def index_docs_task(self, task_description: str):
        _ = task_description
        # Task A6: Index Markdown files in /data/docs/ mapping filename (without path) to first H1 title.
        docs_folder = Path("../data/docs/")
        output_file = docs_folder / "index.json"
        index = {}
        md_files = list(docs_folder.rglob("*.md"))
        for md_file in md_files:
            try:
                async with await asyncio.to_thread(open, md_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.lstrip().startswith("#"):
                            title = line.lstrip("#").strip()
                            relative_path = str(md_file.relative_to(docs_folder))
                            index[relative_path] = title
                            break
            except Exception:
                continue

        try:
            async with await asyncio.to_thread(open, output_file, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            raise Exception("Failed to write index.json") from e

    async def extract_email_task(self, task_description: str):
        # Task A7: Extract sender email from /data/email.txt using LLM
        input_file = "/data/email.txt"
        output_file = "/data/email-sender.txt"
        
        try:
            async with await asyncio.to_thread(open, input_file, "r", encoding="utf-8") as f:
                email_content = f.read()
        except Exception as e:
            raise Exception("Failed to read email file") from e

        prompt = """
        Extract only the sender's email address from this email message. 
        Return just the email address without any other text.

        Email content:
        """ + email_content

        try:
            # Get response from LLM
            sender_email = await asyncio.to_thread(call_llm, prompt)
            sender_email = sender_email.strip()
            
            # Validate email format
            if not re.match(r"[\w\.-]+@[\w\.-]+\.\w+", sender_email):
                raise Exception("Invalid email format returned by LLM")

            # Write to output file
            async with await asyncio.to_thread(open, output_file, "w", encoding="utf-8") as f:
                f.write(sender_email)
        except Exception as e:
            raise Exception(f"Failed to process or write email: {str(e)}") from e

    async def credit_card_task(self, task_description: str):
        # Task A8: Extract credit card number from /data/credit-card.png using LLM
        input_file = "/data/credit-card.png"
        output_file = "/data/credit-card.txt"

        try:
            # Process with LLM in a separate thread
            card_number = await asyncio.to_thread(extract_card_number_with_llm,input_file)
            
            # Write result to output file
            async with await asyncio.to_thread(open, output_file, "w") as f:
                f.write(card_number)
        except Exception as e:
            raise Exception(f"Credit card task failed: {str(e)}") from e

    async def comments_similarity_task(self, task_description: str):
        # Task A9: Find the most similar pair of comments using OpenAI embeddings
        # Function to compute cosine similarity
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        input_file = "/data/comments.txt"
        output_file = "/data/comments-similar.txt"

        try:
            async with await asyncio.to_thread(open, input_file, "r", encoding="utf-8") as f:
                comments = [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise Exception("Failed to read comments file") from e

        if len(comments) < 2:
            raise Exception("Not enough comments to compare")

        # Get embeddings for all comments
        embeddings = await asyncio.to_thread(lambda: [get_embedding(comment) for comment in comments])

        # Find most similar pair
        max_sim = -1
        most_similar_pair = (None, None)
        for i in range(len(comments)):
            for j in range(i + 1, len(comments)):
                sim = cosine_similarity(embeddings[i], embeddings[j])
                if sim > max_sim:
                    max_sim = sim
                    most_similar_pair = (comments[i], comments[j])

        try:
            async with await asyncio.to_thread(open, output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(most_similar_pair))
        except Exception as e:
            raise Exception("Failed to write similar comments output") from e

    async def ticket_sales_task(self, task_description: str):
        db_file = "/data/ticket-sales.db"
        output_file = "/data/ticket-sales-gold.txt"

        prompt = f'''
    You are an AI assistant responsible for generating SQL queries to retrieve data from a SQLite database.  You will be given a description of the data needed and should respond with ONLY the SQL query. Do not provide any explanations or other text.

    Database Schema:
    The database has a table named "tickets" with the following columns:
    - type (TEXT): The type of ticket (e.g., "Gold", "Silver", "Bronze").
    - units (INTEGER): The number of tickets sold.
    - price (REAL): The price of each ticket.

    Example 1:
    Task: Calculate total sales of "Gold" tickets.
    SQL Query: SELECT SUM(units * price) FROM tickets WHERE type = 'Gold';

    Example 2:
    Task: Get the average price of all tickets.
    SQL Query: SELECT AVG(price) FROM tickets;

    Example 3:
    Task: Find the number of "Silver" tickets sold.
    SQL Query: SELECT SUM(units) FROM tickets WHERE type = 'Silver';

    Task: {task_description}
    SQL Query: 
    '''

        try:
            # Retrieve the SQL query from the LLM.
            response = await asyncio.to_thread(call_llm, prompt)  # Assuming call_llm is defined elsewhere
            sql_query = response.strip() # Remove any leading/trailing whitespace

            conn = await asyncio.to_thread(sqlite3.connect, db_file)
            cursor = conn.cursor()

            cursor.execute(sql_query)
            result = cursor.fetchone()
            
            # Handle cases where the query might return no results (e.g., SUM of no rows is NULL)
            final_output = result[0] if result and result[0] is not None else 0
            conn.close()

        except sqlite3.Error as e:
            error_message = f"Database Error: {e}"

            final_output = error_message # or some other default value/error indicator
        except Exception as e:
            error_message = f"An error occurred: {e}"
            final_output = error_message  # or some other default value/error indicator
        
        try:
            async with await asyncio.to_thread(open, output_file, "w") as f:
                f.write(str(final_output))
        except Exception as e:
            raise Exception(f"Failed to write ticket sales output: {e}") from e


    async def execute_task(self, task_description: str):
        """
        Uses call_llm from utils.py to classify the task description and determine which tasks to execute.
        It sends a prompt to the LLM asking for a JSON response with a key "tasks" (a list of task identifiers)
        and optionally additional parameters (for example, "user_email").
        Based on the returned JSON, it executes the corresponding functions.
        Returns a JSON dict with the original input and a list of success messages.
        """
        # Build a prompt that instructs the LLM to classify the task.
        prompt = f"""Here’s a refined and strict version of your prompt to ensure accurate function selection based on user tasks:  
            You are an AI engine that understands user-provided tasks and helps automate processes by returning the most relevant function(s) to execute them. Your goal is to strictly map the task to one or more function names from the predefined list.  

            ### **Example Tasks and Expected Function Mapping:**  
            - **format_markdown_task** Format the contents of `/data/format.md` using `prettier@3.4.2`, updating the file in-place → **`format_markdown_task`**  
            - **count_weekdays_task** Count the number of Wednesdays in `/data/dates.txt` and write the result to `/data/dates-wednesdays.txt` → **`count_weekdays_task`**  
            - **sort_contacts_task** Sort contacts in `/data/contacts.json` by `last_name`, then `first_name`, and write the result to `/data/contacts-sorted.json` → **`sort_contacts_task`**  
            - **logs_recent_task** Extract the first line of the 10 most recent `.log` files in `/data/logs/` and save it to `/data/logs-recent.txt` → **`logs_recent_task`**  
            - **index_docs_task** Find all Markdown (`.md`) files in `/data/docs/`, extract the first occurrence of each H1 header, and create `/data/docs/index.json` mapping filenames to titles → **`index_docs_task`**  
            - **extract_email_task** Extract the sender’s email from `/data/email.txt` and write it to `/data/email-sender.txt` → **`extract_email_task`**  
            - **credit_card_task** Extract a credit card number from `/data/credit-card.png`, remove spaces, and save it to `/data/credit-card.txt` → **`credit_card_task`**  
            - **comments_similarity_task** Find the most similar pair of comments in `/data/comments.txt` using embeddings and save them to `/data/comments-similar.txt` → **`comments_similarity_task`**  
            - **ticket_sales_task** The SQLite database file `/data/ticket-sales.db` has a tickets table with columns `type`, `units`, and `price`. Each row is a customer bid for a concert ticket. What is the total sales of all the items in the “Gold” ticket type? Write the number in `/data/ticket-sales-gold.txt` → **`ticket_sales_task`**  

            ### **Function Names:**   
            - `format_markdown_task`  
            - `count_weekdays_task`  
            - `sort_contacts_task`  
            - `logs_recent_task`  
            - `index_docs_task`  
            - `extract_email_task`  
            - `credit_card_task`  
            - `comments_similarity_task`  
            - `ticket_sales_task`   

            ### **Strict Matching Rules:**  
            1. **Accurate Mapping:** The function(s) returned must precisely match the nature of the task. No extra or unrelated functions should be included.  
            2. **No Overlap:** If a task clearly aligns with a single function, return only that function. If multiple functions are required, return only the necessary ones.  
            3. **Clear Outputs:** The response should **only** contain a **list of function names** without explanations, additional text, or formatting errors.  
            4. **Task Coverage:** Ensure that all tasks align with the provided function set.

            {task_description} 
            """
        try:
            # Call the LLM with our prompt.
            classification_str = await asyncio.to_thread(call_llm, prompt)
            # classification_json = json.loads(classification_str)
        except Exception as e:
            raise Exception("Failed to classify task via LLM. Response: " + str(e)) from e

        tasks_to_run = [classification_str]
        results = []

        for task in tasks_to_run:
            task_lower = task.lower()
            if task_lower == "`format_markdown_task`":
                await self.format_markdown_task(task_description)
                results.append("Task A2 executed successfully")
            elif task_lower == "`count_weekdays_task`":
                await self.count_weekdays_task(task_description)
                results.append("Task A3 executed successfully")
            if task_lower == "`sort_contacts_task`":
                await self.count_weekdays_task(task_description)
                results.append("Task A4 executed successfully")
            elif task_lower == "`logs_recent_task":
                await self.logs_recent_task(task_description)
                results.append("Task A5 executed successfully")
            elif task_lower == "index_docs_task`":
                await self.index_docs_task(task_description)
                results.append("Task A6 executed successfully")
            elif task_lower == "`extract_email_task`":
                await self.extract_email_task(task_description)
                results.append("Task A7 executed successfully")
            elif task_lower == "`credit_card_task`":
                await self.credit_card_task(task_description)
                results.append("Task A8 executed successfully")
            elif task_lower == "`comments_similarity_task`":
                await self.comments_similarity_task(task_description)
                results.append("Task A9 executed successfully")
            elif task_lower == "`ticket_sales_task`":
                await self.ticket_sales_task(task_description)
                results.append("Task A10 executed successfully")
            else:
                raise Exception("Unrecognized task: " + task)

        return {"input_prompt": task_description, "results": results}