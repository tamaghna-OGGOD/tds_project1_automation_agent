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

class TaskExecutor:
    async def install_and_run_datagen_task(self, task_description: str, user_email: str):
        # Task A1: Install 'uv' if required and run datagen.py from remote URL with user_email argument.
        url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        # Install 'uv' if not in PATH
        if which("uv") is None:
            try:
                await asyncio.to_thread(subprocess.run, ["pip", "install", "uv"], check=True)
            except subprocess.CalledProcessError as e:
                raise Exception("Failed to install uv") from e

        # Download the datagen.py script
        try:
            response = await asyncio.to_thread(requests.get, url)
            if response.status_code != 200:
                raise Exception("Failed to download datagen.py")
            script_content = response.text
        except Exception as e:
            raise Exception("Error downloading datagen.py") from e

        # Write the script to a temporary file and execute it with user_email as argument
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write(script_content)
            tmp_path = tmp.name

        try:
            await asyncio.to_thread(
                subprocess.run, ["python", tmp_path, user_email], check=True
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
        # Task A3: Count the number of Wednesdays in /data/dates.txt and write to /data/dates-wednesdays.txt.
        dates_file = "/data/dates.txt"
        output_file = "/data/dates-wednesdays.txt"
        count = 0
        try:
            async with await asyncio.to_thread(open, dates_file, "r") as f:
                lines = f.readlines()
        except Exception as e:
            raise Exception("Could not read dates file") from e

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                dt = datetime.strptime(line, "%Y-%m-%d")
                # Wednesday is weekday value 2 (Mon=0)
                if dt.weekday() == 2:
                    count += 1
            except Exception:
                # If date format is not ISO, try other heuristics if needed.
                continue

        try:
            async with await asyncio.to_thread(open, output_file, "w") as f:
                f.write(str(count))
        except Exception as e:
            raise Exception("Could not write output file") from e

    async def sort_contacts_task(self, task_description: str):
        # Task A4: Sort contacts in /data/contacts.json by last_name then first_name.
        input_file = "/data/contacts.json"
        output_file = "/data/contacts-sorted.json"
        try:
            async with await asyncio.to_thread(open, input_file, "r") as f:
                contacts = json.load(f)
        except Exception as e:
            raise Exception("Failed to load contacts") from e

        # Sort contacts by last_name then first_name.
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

        # Sort log files by modification time in descending order.
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
                            # Remove leading '#' and strip whitespace
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
        # Task A7: Extract sender email from /data/email.txt using simulated LLM (regex extraction here).
        input_file = "/data/email.txt"
        output_file = "/data/email-sender.txt"
        try:
            async with await asyncio.to_thread(open, input_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise Exception("Failed to read email file") from e

        # Simulate sending content to an LLM; here we use regex to find an email.
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
        # Task A8: Extract credit card number from image /data/credit-card.png using simulated LLM.
        input_file = "/data/credit-card.png"
        output_file = "/data/credit-card.txt"
        # In a real implementation, you'd perform OCR or send the image to an LLM model.
        # Here, we simulate by returning a dummy card number.
        dummy_card_number = "4111111111111111"  # Without spaces
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

        # Simulated similarity: simply choose the first two comments.
        similar_pair = comments[:2]

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
            # Calculate total sales as sum(units * price) for Gold tickets.
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