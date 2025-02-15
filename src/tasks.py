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

import requests
from utils import call_llm

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
        cmd = ["prettier", "--write", "/data/format.md"]
        try:
            await asyncio.to_thread(subprocess.run, cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception("Markdown formatting failed") from e

    async def count_weekdays_task(self, task_description: str):
        prompt = '''
        You are an AI assistant responsible for generating executable Python code that performs specific tasks using the provided file paths. 
        Your generated code must be structured, optimized, and ready to run in a Python compiler without modification.

        IMPORTANT:
        - The code should use exactly these file paths:
            * Input file: "D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates.txt"
            * Output file: "D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates-wednesdays.txt"
        - Do not modify these paths; use them exactly as given.
        - The generated code must handle file reading and writing correctly.
        - The code should efficiently process the dates and count only the number of Wednesdays.
        - Only a single integer (the result) should be written to the output file.
        - Include proper exception handling for missing or malformed data.
        - No extra text should be output—only the Python code.
        - The generated code must define a function named "count_wednesdays" that takes two parameters: input_file and output_file.

        Example Task:
        The file "D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates.txt" contains one date per line in the format YYYY-MM-DD. 
        Your task is to count the number of Wednesdays in this file and write just the integer count to "D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates-wednesdays.txt".

        Example Code Output: 
        import datetime

        def count_wednesdays(input_file, output_file):
            try:
                with open(input_file, 'r') as f:
                    dates = f.readlines()
                
                wednesday_count = sum(1 for date in dates if datetime.datetime.strptime(date.strip(), "%Y-%m-%d").weekday() == 2)
                
                with open(output_file, 'w') as f:
                    f.write(str(wednesday_count))
            except Exception as e:
                with open(output_file, 'w') as f:
                    f.write("Error: " + str(e))

        count_wednesdays("D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates.txt",
                        "D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates-wednesdays.txt")
        '''
        try:
            # Retrieve the Python code from the LLM.
            response = await asyncio.to_thread(call_llm, prompt)
            code = response.strip()

            # Compile and execute the generated Python code.
            local_scope = {}
            compiled_code = compile(code, '<llm-generated>', 'exec')
            exec(compiled_code, local_scope)  # This "runs" the produced code.

            # Define the input and output file paths.
            input_file = r'D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates.txt'
            output_file = r'D:/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/dates-wednesdays.txt'

            # Check if the input file exists.
            if not os.path.isfile(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")

            # Execute the dynamically produced function in a separate thread.
            await asyncio.to_thread(local_scope["count_wednesdays"], input_file, output_file)
        except Exception as e:
            raise RuntimeError("Execution failed: " + str(e))


    async def sort_contacts_task(self, task_description: str):
        # Task A4: Sort contacts in /data/contacts.json by last_name then first_name.
        input_file = "/data/contacts.json"
        output_file = "/data/contacts-sorted.json"
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
        folder = "/data/logs/"
        output_file = "/data/logs-recent.txt"
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
        docs_folder = Path("/data/docs/")
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
        # Task A7: Extract sender email from /data/email.txt using simulated LLM (regex extraction).
        input_file = "/data/email.txt"
        output_file = "/data/email-sender.txt"
        try:
            async with await asyncio.to_thread(open, input_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise Exception("Failed to read email file") from e

        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", content)
        if not match:
            raise Exception("No email found in content")
        email = match.group(0)

        try:
            async with await asyncio.to_thread(open, output_file, "w", encoding="utf-8") as f:
                f.write(email)
        except Exception as e:
            raise Exception("Failed to write email sender output") from e

    async def credit_card_task(self, task_description: str):
        # Task A8: Extract credit card number from /data/credit-card.png using simulated LLM.
        input_file = "/data/credit-card.png"
        output_file = "/data/credit-card.txt"
        dummy_card_number = "4111111111111111"  # Simulated output (without spaces)
        try:
            async with await asyncio.to_thread(open, output_file, "w") as f:
                f.write(dummy_card_number)
        except Exception as e:
            raise Exception("Failed to write credit card output") from e

    async def comments_similarity_task(self, task_description: str):
        # Task A9: Find the most similar pair of comments from /data/comments.txt using embeddings (simulated).
        input_file = "/data/comments.txt"
        output_file = "/data/comments-similar.txt"
        try:
            async with await asyncio.to_thread(open, input_file, "r", encoding="utf-8") as f:
                comments = [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise Exception("Failed to read comments file") from e

        if len(comments) < 2:
            raise Exception("Not enough comments to compare")

        similar_pair = comments[:2]  # Simulated similarity

        try:
            async with await asyncio.to_thread(open, output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(similar_pair))
        except Exception as e:
            raise Exception("Failed to write similar comments output") from e

    async def ticket_sales_task(self, task_description: str):
        # Task A10: Calculate total sales of "Gold" tickets from /data/ticket-sales.db.
        db_file = "/data/ticket-sales.db"
        output_file = "/data/ticket-sales-gold.txt"
        try:
            conn = await asyncio.to_thread(sqlite3.connect, db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
            result = cursor.fetchone()
            total_sales = result[0] if result and result[0] is not None else 0
            conn.close()
        except Exception as e:
            raise Exception("Failed to compute ticket sales") from e

        try:
            async with await asyncio.to_thread(open, output_file, "w") as f:
                f.write(str(total_sales))
        except Exception as e:
            raise Exception("Failed to write ticket sales output") from e

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

            ---

            **Prompt:**  
            You are an AI engine that understands user-provided tasks and helps automate processes by returning the most relevant function(s) to execute them. Your goal is to strictly map the task to one or more function names from the predefined list.  

            ### **Example Tasks and Expected Function Mapping:**  
            - **A2.** Format the contents of `/data/format.md` using `prettier@3.4.2`, updating the file in-place → **`format_markdown_task`**  
            - **A3.** Count the number of Wednesdays in `/data/dates.txt` and write the result to `/data/dates-wednesdays.txt` → **`count_weekdays_task`**  
            - **A4.** Sort contacts in `/data/contacts.json` by `last_name`, then `first_name`, and write the result to `/data/contacts-sorted.json` → **`sort_contacts_task`**  
            - **A5.** Extract the first line of the 10 most recent `.log` files in `/data/logs/` and save it to `/data/logs-recent.txt` → **`logs_recent_task`**  
            - **A6.** Find all Markdown (`.md`) files in `/data/docs/`, extract the first occurrence of each H1 header, and create `/data/docs/index.json` mapping filenames to titles → **`index_docs_task`**  
            - **A7.** Extract the sender’s email from `/data/email.txt` and write it to `/data/email-sender.txt` → **`extract_email_task`**  
            - **A8.** Extract a credit card number from `/data/credit-card.png`, remove spaces, and save it to `/data/credit-card.txt` → **`credit_card_task`**  
            - **A9.** Find the most similar pair of comments in `/data/comments.txt` using embeddings and save them to `/data/comments-similar.txt` → **`comments_similarity_task`**  
            - **A10.** Calculate total sales for "Gold" tickets in `/data/ticket-sales.db` and write the number to `/data/ticket-sales-gold.txt` → **`ticket_sales_task`**  

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
            # if task_lower == "datagen":
            #     # Use provided user_email if available; otherwise extract from task_description.
            #     user_email = classification_json.get("user_email")
            #     if not user_email:
            #         match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', task_description)
            #         user_email = match.group(0) if match else "user@example.com"
            #     await self.install_and_run_datagen_task(task_description, user_email)
            #     results.append("Task A1 executed successfully")
            # if task_lower == "format":
            #     await self.format_markdown_task(task_description)
            #     results.append("Task A2 executed successfully")
            # elif task_lower in ["dates", "weekday"]:
            #     await self.count_weekdays_task(task_description)
            #     results.append("Task A3 executed successfully")
            if task_lower == "count_weekdays_task":
                await self.count_weekdays_task(task_description)
                results.append("Task A4 executed successfully")
            # elif task_lower == "logs":
            #     await self.logs_recent_task(task_description)
            #     results.append("Task A5 executed successfully")
            # elif task_lower == "docs":
            #     await self.index_docs_task(task_description)
            #     results.append("Task A6 executed successfully")
            # elif task_lower == "email":
            #     await self.extract_email_task(task_description)
            #     results.append("Task A7 executed successfully")
            # elif task_lower in ["credit_card", "credit-card"]:
            #     await self.credit_card_task(task_description)
            #     results.append("Task A8 executed successfully")
            # elif task_lower == "comments":
            #     await self.comments_similarity_task(task_description)
            #     results.append("Task A9 executed successfully")
            # elif task_lower in ["ticket_sales", "ticket"]:
            #     await self.ticket_sales_task(task_description)
            #     results.append("Task A10 executed successfully")
            # else:
            #     raise Exception("Unrecognized task: " + task)

        return {"input_prompt": task_description, "results": results}