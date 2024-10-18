# Project Name

Brief description of your project.

## Installation

To set up this project, follow these steps:

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the server directory and add the following:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_APP=main.py
FLASK_ENV=development
   ```

6. Set up the database:
   - Ensure you have MySQL installed and running.
   - Create a database named `bigbrother`.
   - Update the database configuration in `server/main.py` if necessary:

