from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# DB Configurations
db_username = os.getenv('MYSQL_USER', 'root')
db_name = os.getenv('MYSQL_DATABASE', "fit_tracker")
db_host = os.getenv('MYSQL_HOST', 'localhost')
db_port = os.getenv('MYSQL_PORT', "Please enter database port")

# Fit-Tracker Connection Configuratios
client_id = os.getenv('CLIENT_ID', 'Please enter the fit tracker client ID.')
client_secret = os.getenv('CLIENT_SECRET', 'Please enter the fit tracker client secret.')
base_url = os.getenv('BASE_URL', 'Please enter the fit tracker base url.')
websocket_base_url = os.getenv('WEBSOCKET_BASE_URL', 'Please enter the fit tracker websocket url.')