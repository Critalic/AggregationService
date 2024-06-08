from sqlalchemy import create_engine, text
import pandas as pd
from sqlalchemy.orm import sessionmaker

Engine = create_engine("mysql+mysqlconnector://root:1111@localhost:3306/new_schema")
Session = sessionmaker(bind=Engine)


def read_forecasts_with_timestamp(timestamp: str):
    print(f'Fetching forecasts')
    connection = Engine.connect()
    return pd.read_sql(text(f'select * from forecast where time_stamp=\'{timestamp}\''), connection)


def persist_forecasts(forecasts: pd.DataFrame):
    print(f'Start saving {len(forecasts)} forecasts')

    try:
        forecasts.to_sql(name='forecast', con=Engine, if_exists='append', index=False)

        print('Saving complete')
    except Exception as e:
        print(f"An error occurred: {e}")
