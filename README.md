# My FastAPI Automation App

This project is a FastAPI application that automates the execution of various tasks through an API. It provides endpoints to run specific tasks and read files from a designated directory.

## Project Structure

```
my-fastapi-automation-app
├── src
│   ├── main.py          # Entry point of the FastAPI application
│   ├── tasks.py         # Contains the TaskExecutor class for task execution
│   └── utils.py         # Utility functions for the application
├── requirements.txt      # Lists the project dependencies
├── README.md             # Documentation for the project
└── .env                  # Environment variables for configuration
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd my-fastapi-automation-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables in the `.env` file as needed.

## Usage

To run the FastAPI application, execute the following command:
```
uvicorn src.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Run Task

- **Endpoint:** `POST /run`
- **Description:** Executes a specified task.
- **Request Body:** 
  ```json
  {
    "task": "task_name"
  }
  ```

### Read File

- **Endpoint:** `GET /read`
- **Description:** Reads the content of a file from the `/data` directory.
- **Query Parameter:** `path` (string) - The path of the file to read.

## License

This project is licensed under the MIT License.