# Fit Tracker Application

Fit Tracker API is a web service implemented using FastAPI that interacts with a fit tracker device, retrieves user data (steps, heart rate, MET, height, weight), 
stores it in a database, and provides endpoints to access and export the data. 
The service is created using token-based authentication, WebSocket communication for real-time data.


## Installation

1. Clone the repository: 
   * git clone https://github.com/AkankshaDwivedi/fit-tracker.git
3. Navigate to the project directory:
   * cd fit-tracker
5. Create Database in the choice of your workbench:
   * fit_tracker
7. For creating the tables use command:
   * python3 create_tables.py
8. Create a virtual environment:
   * python3 -m venv venv
   * source venv/bin/activate
9. Install dependencies:
   * pip install -r requirements.txt
11. Set up environment variables:
    * Create an .env file
13. Run the application: 
    * uvicorn app:app --host 0.0.0.0 --port 8000 --reload


## Directory Structure

- .env : This file store environment-specific variables, such as API keys, database credentials, and configuration settings
- README.md : This file is the main documentation for a project. It helps developers set up the project and provides the necessary information.
- app.py : This file contains the endpoints for the Fit Tracker application.
- create_tables.py : This file is used to create the tables in the database.
- database_engine.py : This file contains the database configuration for the project, including: database connection setup, engine creation.
- models.py: This file contains the database models and Pydantic schemas for handling user fitness data and daily summaries.
- requirements.txt: This file includes a list of all the Python dependencies that the project needs to run.
- settings.py: This file includes configuration and environment variables required to set up the project.


## Logging

All loggings are saved in fit_tracker_logs.log file

## API Endpoints Usage

Once the application is up and running, visit http://localhost:8000/docs to view and exceute the endpoints in your browser.

Listing the endpoints exposed via fit tracker api.
<img width="668" alt="image" src="https://github.com/user-attachments/assets/0e1a1d31-e357-4619-b176-bdf89cd8144d" />

## API Endpoints Response

Adding response for the endpoint:
1. Get User Info (/users/{user_id}
* Response: A JSON response containing latest 15 entries for the user data.
  <img width="504" alt="image" src="https://github.com/user-attachments/assets/c09ded0b-8c58-4a1a-8517-0e9913cd01a7" />

2. Get And Store Summary Data (/user/get-summary/{user_id})
* Response: A JSON response containing user_id, total_steps, distance, average_heart_beat kcal_burned and date.
  <img width="504" alt="image" src="https://github.com/user-attachments/assets/564d0659-258c-40a8-a46f-d076760e8a98" />

3. Export Data CSV (/export/csv)
* Response: A CSV file including user_id, total_steps, distance, average_heart_beat kcal_burned and date.
  <img width="504" alt="image" src="https://github.com/user-attachments/assets/a1f897ea-9530-4ebc-84d5-ff3c029162f8" />


## API Endpoints Documentation

To view the endpoints documentation, visit http://localhost:8000/redoc

1. Get User Info
<img width="963" alt="image" src="https://github.com/user-attachments/assets/00bc6831-e4f5-4b9b-952a-bfe795fb1fbc" /><br>

2. Get And Store Summary Data
<img width="963" alt="image" src="https://github.com/user-attachments/assets/1bf9f3c3-a472-4b5a-8a96-d8ae5a0f5989" /><br>

3. Export Data CSV
<img width="963" alt="image" src="https://github.com/user-attachments/assets/07010982-6fc3-48b7-8476-84e1eb7be869" /><br>

## WebSocket Integration

The application connects to a WebSocket server to retrieve real-time fitness data. When the WebSocket connection is established, user data like steps, heart rate, and MET are received and saved to the database.

WebSocket URL: <websocket_base_url>/api/v1/traces
The token is sent as an authorization header for authentication.
