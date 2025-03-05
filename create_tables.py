from database_engine import engine
from models import Base

# Create tables in the database
Base.metadata.create_all(bind=engine)