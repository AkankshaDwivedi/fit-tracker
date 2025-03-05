# Fit Tracker Application

Fit Tracker API is a web service that interacts with a fit tracker device, retrieves user data (steps, heart rate, MET, height, weight), 
stores it in a database, and provides endpoints to access and export the data. 
The service is created using token-based authentication, WebSocket communication for real-time data.


## Installation

1. Clone the repository: git clone https://github.com/AkankshaDwivedi/fit-tracker.git
2. Navigate to the project directory: cd fit-tracker-api
3. Create Database: fit_tracker
4. For creating the tables use command - python3 create_tables.py
5. Create a virtual environment:
    python3 -m venv venv
    source venv/bin/activate
6. Install dependencies: pip install -r requirements.txt
7. Set up environment variables: Create an .env file
8. Run the application: uvicorn app:app --host 0.0.0.0 --port 8000 --reload


## Directory Structure
- .env : This file contains the environment variables
- app.py : This file contains the fit tracker endpoints
- create_tables.py : This file is used to create the tables in the database
- database_engine.py :
- model.py - 

## Logging
All loggings are saved in fit_tracker_logs.log file

## Usage
Once the application is up and running, visit http://localhost:8000/docs to view and exceute the endpoints in your browser.


## API Endpoints
To view the endpoints documentation, visit http://localhost:8000/redoc

1. Get User Info
<img width="963" alt="image" src="https://github.com/user-attachments/assets/00bc6831-e4f5-4b9b-952a-bfe795fb1fbc" />

2. Get User Info
<img width="986" alt="image" src="https://github.com/user-attachments/assets/1bf9f3c3-a472-4b5a-8a96-d8ae5a0f5989" />

3. Export Data CSV
<img width="987" alt="image" src="https://github.com/user-attachments/assets/07010982-6fc3-48b7-8476-84e1eb7be869" />
