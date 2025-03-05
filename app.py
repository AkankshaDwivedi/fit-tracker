
import asyncio
from database_engine import get_db
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
import logging
from models import UserData, UserDailySummary, UserResponse, UserDailySummaryResponse
import pandas as pd
import json
import requests
from settings import client_id, client_secret, base_url, websocket_base_url
from sqlalchemy.orm import Session

import websockets
import base64
import time
from models import UserData
from datetime import datetime


# Initialize and set logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("fit_tracker_logs.log"),
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/get_token", include_in_schema=False)
async def get_token():

    try:
        data={
            "clientId": client_id,
            "clientSecret": client_secret
        }   
        response = requests.post(f"{base_url}/api/v1/token", json=data)
        token = response.json().get('accessToken')
        logger.info("Token retrieved successfully inside get_token HTTP method!")
        return token
    except requests.RequestException as e:
        logger.error(f"An error occurred while requesting the token: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while requesting the token: {e}")
    except Exception as e:
        logger.error(f"An error occurred while requesting the token: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while requesting the token: {e}")
    


# Startup event handler and run websocket connection as a background task
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting the application!")
        token = await get_token()
        logger.info("Token retrieved successfully.")
        # Run WebSocket connection in the background
        asyncio.create_task(connect_to_fit_tracker(token))
        logger.info("Connected to fit-tracker and data retrieval started.")
    except Exception as e:
        logger.error(f"Exception occurred during startup: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during startup: {e}")


def decode_data(message):
    decoded_bytes = base64.b64decode(message)
    decoded_message = decoded_bytes.decode('utf-8')
    decoded_message = json.loads(decoded_message)
    logger.info(f"Websocket message decoded successfully: {decoded_message}.")
    return decoded_message


async def connect_to_fit_tracker(token: str):
    
    websocket_url = f"{websocket_base_url}//api/v1/traces"
    
    # Connect to WebSocket with Authorization token
    while True:
        try:
            async with websockets.connect(websocket_url, additional_headers={"Authorization": f"{token}"}) as websocket:
                while True:
                    message = await websocket.recv()
                    decoded_message = decode_data(message)

                    # Get the user data
                    user_id = decoded_message.get('userId')
                    steps = decoded_message.get('steps')
                    heart_beat = decoded_message.get('heartBeat')
                    met = decoded_message.get('met')

                    # Get height and weight for the user from fit tracker app
                    logger.info(f"Invoking get_height_weight HTTP method to get the height and weight for the user")
                    user_info = await get_height_weight(user_id)
                    height = user_info.get('height')
                    weight = user_info.get('weight')
                    
                    # Save the user details to the DB
                    db = next(get_db())
                    db_item = UserData(user_id=user_id, steps=steps, heart_beat=heart_beat, met=met, height=height, weight=weight)
                    db.add(db_item)
                    db.commit()
                    logger.info(f"User data saved for {user_id}. Steps: {steps}, Heart Beat: {heart_beat}, MET: {met}, Height: {height}, Weight: {weight}.")
                    db.refresh(db_item)
        except websockets.exceptions.ConnectionClosedError as e:
            logger.info(f"Connection closed : {e}")
        except Exception as e:
            logger.info(f"An unexpected error occurred : {e}")
        
        # If the connection is closed, wait and try to reconnect
        logger.info("Reconnecting to WebSocket server......")
        await asyncio.sleep(5) 



@app.get("/get_height_weight", include_in_schema=False)
async def get_height_weight(user_id): 

    url = f"{base_url}//api/v1/users/{user_id}"
    token = await get_token()
    logger.info("Token retrieved successfully.")
    headers = {'Authorization': token}
   
    try:
        response = requests.get(url, headers=headers)
        user_data = response.json()
        logger.info(f"User height and weight retrieved successfully: {user_data}")
        # return {"weight": user_data.get('weight'), "height": user_data.get('height')}
        return user_data
    except requests.RequestException as e:
        logger.error(f"An error occurred while fetching the user details: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching the user details:{e}")
    except Exception as e:
        logger.error(f"An error occurred while fetching the user details: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching the user details: {e}")


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_info(user_id: str, db: Session = Depends(get_db)):
    """
    The HTTP GET method is used to retrieve user information by user_id.
    This endpoint fetches user details such as steps, heartbeat, met, height and weight from the database.

    **Parameters**:
    - user_id: Id of the user whose information is to be retrived.

    **Returns**:
    - A JSON response containing the user data, including user_id, steps, heartbeat, met, height and weight.
    
    **Exceptions**:
    - 404 Not Found: If there is no user with the user_id.
    - 500 Internal Server Error: If there is a some server side exception.
    """

    try:
        user = db.query(UserData).filter(UserData.user_id == user_id).first()

        if user is None:
            logger.warning(f"User with user_id {user_id} not found.")
            raise HTTPException(status_code=404, detail=f"User with user_id {user_id} not found")
        
        logger.info(f"User found: {user.user_id}, steps: {user.steps}, heart_beat: {user.heart_beat}, met: {user.met}, height: {user.height}, weight: {user.weight}.")           
        return user
    except requests.RequestException as e:
        logger.error(f"An error occurred while fetching user data: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching user data: {e}")
    except Exception as e:
        logger.error(f"An error occurred while fetching user data: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching user data: {e}")


@app.get("/user/get-summary/{user_id}", response_model=UserDailySummaryResponse)
def get_and_store_daily_summary(user_id: str, date: str, db: Session = Depends(get_db)):
    """
    The HTTP GET method is used to retrieve and store a user's daily summary.
    This endpoint calculates total steps, distance, average heartbeat and kcal burned for the specified date. 
    It stores the summary in the database and also returns the data.

    **Parameters**:
    - user_id: Id of the user whose information is to be retrived.
    - date (str): The date in the format YYYY-MM-DD.

    **Returns**:
    - A JSON response containing the user data, including user_id, total_steps, distance, average_heart_beat kcal_burned and date.
    
    **Exceptions**:
    - 404 Not Found: If there is no data found for the user on the given date.
    - 500 Internal Server Error: If there is a some server side exception while processing or saving the data.
    """

    start_of_day = f"{date} 00:00:00"
    end_of_day = f"{date} 23:59:59"
    
    results = db.query(UserData).filter(UserData.user_id == user_id, UserData.timestamp >= start_of_day, UserData.timestamp <= end_of_day).all()

    if not results:
        logger.error(f"No data found for this user on the given date.")
        raise HTTPException(status_code=404, detail="No data found for this user on the given date")

    # Calculate the total steps, distance, average heart beat and kcal burned
    weight = results[0].weight
    total_steps = sum(result.steps for result in results)
    total_heart_beat = sum(result.heart_beat for result in results)
    total_met = sum(result.met for result in results)
    total_time = len(results)
    distance = round((total_steps/1000) * 0.7, 2)  # 1000 steps = 0.7 km
    average_heart_beat = round(total_heart_beat/total_time, 2)
    kcal_burned = round(total_time * (total_met * 3.5 * weight / 200), 2)
    logger.info(f"User total steps:{total_steps}, distance:{distance}, average heart beat:{average_heart_beat}, kcal burned: {kcal_burned} calculated.")

    # Save the daily summary for the user to the database
    try:
        # Check if the record already exists for the user_id
        user_record = db.query(UserDailySummary).filter(UserDailySummary.user_id == user_id).first()
        if user_record:
            # If the record exists, update its fields
            logger.error(f"User record exists, updating the field in the DB.")
            user_record.total_steps = total_steps
            user_record.distance = distance
            user_record.average_heart_beat = average_heart_beat
            user_record.kcal_burned = kcal_burned
            user_record.date = datetime.strptime(date, "%Y-%m-%d")
        else:
            # If no record is found, create and add the new record to the session
            logger.error(f"User record does not exist, creating record in the DB.")
            daily_summary = UserDailySummary(
                user_id=user_id,
                total_steps=total_steps,
                distance=distance,
                average_heart_beat=average_heart_beat,
                kcal_burned=kcal_burned,
                date=datetime.strptime(date, "%Y-%m-%d")
            )
            db.add(daily_summary)
        logger.error(f"User data updated in the DB.")
        db.commit()
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        db.rollback()

    return UserDailySummary(
        user_id=user_id,
        total_steps=total_steps,
        distance=distance,
        average_heart_beat=average_heart_beat,
        kcal_burned=kcal_burned,
        date=date
    )


@app.get("/export/csv")
async def export_data_csv(db: Session = Depends(get_db)):
    """
    The HTTP GET method is used to export user's daily summary data as a CSV file.
    This endpoint retrieves all user daily summary data from the database and exports it as a CSV file.

    The CSV file contains the following columns:user_id, total_steps, distance, average_heart_beat, kcal_burned and date

    **Returns**:
    - A CSV file containing the user data.

    **Exceptions**:
    - **404 Not Found**: If there is no user data available in the database.
    - **500 Internal Server Error**: If an error occurs during the process of exporting data to CSV.
    """

    try:
        # Retrieve user daily data (from database or mock data)
        user_data = db.query(UserDailySummary).all()

        if not user_data:
            logger.warning("No user data found for export.")
            raise HTTPException(status_code=404, detail="No user data available for export.")

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame([{
            "user_id": entry.user_id,
            "total_steps": entry.total_steps,
            "distance": entry.distance,
            "average_heart_beat": entry.average_heart_beat,
            "kcal_burned": entry.kcal_burned,
            "date": entry.date.strftime("%Y-%m-%d"),
        } for entry in user_data])
        
        # Save the DataFrame to a CSV in memory (using StringIO to avoid file I/O)
        csv_data = df.to_csv(index=False)
        
        # Return the CSV as a response
        logger.info("User data CSV exported successfully.")
        return StreamingResponse(csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=user_data.csv"})
    except Exception as e:
        logger.error(f"An error occurred while exporting user data to CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while exporting the data.")