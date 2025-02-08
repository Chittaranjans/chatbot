from sqlalchemy import create_engine , MetaData, Table
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Create the SQLAlchemy engine
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Connection successful!")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create a session
    session = SessionLocal()

    # Reflect the tables
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Print the table names
    print("Tables in the database:")
    for table_name in metadata.tables.keys():
        print(table_name)

    # Query data from each table
    for table_name in metadata.tables.keys():
        table = Table(table_name, metadata, autoload_with=engine)
        print(f"\nData from {table_name}:")
        query = session.query(table).limit(5).all()  # Limit to 5 rows for brevity
        for row in query:
            print(row)

    # Close the session
    session.close()
except Exception as e:
    print(f"Failed to connect: {e}")