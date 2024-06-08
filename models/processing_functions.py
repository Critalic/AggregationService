import pandas as pd


def get_pivoted_by_provider(forecast_dataframe: pd.DataFrame, historical_dataframe: pd.DataFrame, column_name: str):
    pivoted = forecast_dataframe.pivot_table(index=['city_id', 'forecast_type_id', 'time'], columns='provider_id',
                                             values=column_name).reset_index()
    pivoted.dropna(inplace=True)
    pivoted = pd.merge(pivoted, historical_dataframe[['city_id', 'forecast_type_id', 'time', column_name]],
                       on=['city_id', 'forecast_type_id', 'time'])

    new_col_names = []
    for i in pivoted.columns:
        if isinstance(i, int):
            new_col_names.append(f'{column_name}{i}')
        else:
            new_col_names.append(i)

    pivoted.columns = new_col_names
    return pivoted


def prepare_time_features(dataframe: pd.DataFrame):
    dataframe['month'] = dataframe['time'].dt.month
    dataframe['day'] = dataframe['time'].dt.day
    dataframe['hour'] = dataframe['time'].dt.hour
    return dataframe
