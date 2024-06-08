import pandas as pd
import json
import logging
from app.util.utility_functions import not_in_list, not_in_list_comma_separated

logger = logging.getLogger(__name__)


def preprocess_data(forecast_data: pd.DataFrame):
    print('Start preprocessing')
    with open('static/condition-mappings/visualCrossingConditions.json', 'r') as file:
        visualCrossingConditions = json.load(file)

    prepared_forecast_data = forecast_data.copy()
    prepared_forecast_data['conditions'] = prepared_forecast_data['conditions'].fillna('Unknown')

    prepared_forecast_data = map_OpenMeteo(prepared_forecast_data)
    __check_OpenMeteo(prepared_forecast_data, visualCrossingConditions)
    prepared_forecast_data = map_TIO(prepared_forecast_data)
    __check_TomorrowIO(prepared_forecast_data, visualCrossingConditions)

    prepared_forecast_data['humidity'] = (
        prepared_forecast_data.groupby([prepared_forecast_data['time'].dt.date, 'city_id'])['humidity']
        .transform(lambda x: x.fillna(x.mean())))

    prepared_forecast_data['pressure'] = (
        prepared_forecast_data.groupby([prepared_forecast_data['time'].dt.date, 'city_id'])['pressure']
        .transform(lambda x: x.fillna(x.mean())))

    print('Preprocessing finished')
    return prepared_forecast_data


def map_TIO(dataframe: pd.DataFrame):
    with open('static/condition-mappings/tomorrowIOMappings.json', 'r') as file:
        tomorrowIOMappings = json.load(file)

    dataframe['conditions'] = dataframe.apply(lambda row: __map_TIO_row(row, tomorrowIOMappings), axis=1)
    return dataframe


def map_OpenMeteo(dataframe: pd.DataFrame):
    with open('static/condition-mappings/openMeteoMappings.json', 'r') as file:
        openMeteoMappings = json.load(file)

    dataframe.loc[dataframe['provider_id'] == 3, 'conditions'] = (
        dataframe.loc[dataframe['provider_id'] == 3, 'conditions'].map(openMeteoMappings))
    return dataframe


def __map_TIO_row(row, tomorrowIOMappings, TIOproviderId=2):
    if row['provider_id'] == TIOproviderId:
        conditions = row['conditions'].split(' and ')
        replaced_conditions = [tomorrowIOMappings.get(condition) for condition in conditions]
        return ', '.join(replaced_conditions)
    else:
        return row['conditions']


def __check_OpenMeteo(dataframe: pd.DataFrame, visualCrossingConditions):
    not_mapped = not_in_list(dataframe[dataframe['provider_id'] == 3]['conditions'].unique().tolist(),
                             visualCrossingConditions)
    if len(not_mapped) != 0:
        logger.error('Unmapped OpenMeteo conditions detected: ')
        for i in not_mapped:
            logger.error(i + '\n')

        raise ValueError('Unmapped OpenMeteo conditions detected')


def __check_TomorrowIO(dataframe: pd.DataFrame, visualCrossingConditions):
    not_mapped = not_in_list_comma_separated(dataframe[dataframe['provider_id'] == 2]['conditions'].unique().tolist(),
                                             visualCrossingConditions)
    if len(not_mapped) != 0:
        logger.error('Unmapped TomorrowIO conditions detected: ')
        for i in not_mapped:
            logger.error(i + '\n')

        raise ValueError('Unmapped TomorrowIO conditions detected')
