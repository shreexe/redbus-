import pandas as pd
from sqlalchemy import create_engine

def store_data_to_sql(csv_file):
    # Load the scraped data from CSV file
    df = pd.read_csv(csv_file)

    # Create SQLAlchemy engine (SQLite used here; replace with your DB connection string)
    engine = create_engine('sqlite:///redbus_data.db')

    # Store DataFrame in SQL table
    df.to_sql('bus_routes', con=engine, if_exists='replace', index=False)

if __name__ == "__main__":
    store_data_to_sql('redbus_data.csv')
