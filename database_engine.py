from settings import db_username, db_name, db_host, db_port
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Configurations
db_url = f"mysql+mysqlconnector://{db_username}@{db_host}:{db_port}/{db_name}"

# Create Database Engine
try:
    engine = create_engine(db_url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print("Exception ********************", e)

Base = declarative_base()

# Method to get new DB sessionß
def get_db():
    db = SessionLocal()
    print(db)
    try:
        yield db
    finally:
        db.close()