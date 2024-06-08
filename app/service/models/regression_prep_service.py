import pandas as pd

from app.util.utility_functions import prepare_time_features


def prepare_regression_frame(dataframe: pd.DataFrame, column: str):
    prep_forecasts = __get_pivoted_by_provider(dataframe, column)
    prepare_time_features(prep_forecasts)
    return prep_forecasts


def __get_pivoted_by_provider(forecast_dataframe: pd.DataFrame, column_name: str):
    pivoted = forecast_dataframe.pivot_table(index=['city_id', 'forecast_type_id', 'time'], columns='provider_id',
                                             values=column_name).reset_index()
    pivoted.dropna(inplace=True)

    new_col_names = []
    for i in pivoted.columns:
        if isinstance(i, int):
            new_col_names.append(f'{column_name}{i}')
        else:
            new_col_names.append(i)

    pivoted.columns = new_col_names
    return pivoted
