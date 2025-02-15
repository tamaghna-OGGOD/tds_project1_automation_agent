FROM python:3.12-slim

WORKDIR /app

# Create a virtual environment (best practice)
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files (src directory)
COPY src ./src

EXPOSE 8000

# Use a production-ready WSGI server like Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "4", "main:app"]