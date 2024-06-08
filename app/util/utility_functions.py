from datetime import datetime

import pandas as pd

date_format = '%Y-%m-%d %H:%M:%S'

def not_in_list(toCheck, againstCheck):
    not_in_l = [x for x in toCheck if x not in againstCheck]
    return not_in_l


def not_in_list_comma_separated(toCheck, againstCheck):
    not_in_l = []
    for x in toCheck:
        x = x.split(', ')
        not_in_l+=[s for s in x if s not in againstCheck]

    return not_in_l

def prepare_time_features(dataframe: pd.DataFrame):
    dataframe['month'] = dataframe['time'].dt.month
    dataframe['day'] = dataframe['time'].dt.day
    dataframe['hour'] = dataframe['time'].dt.hour
    return dataframe


def is_valid_datetime(date_string:str):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False
