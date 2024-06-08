import json
import pandas as pd

from app.util.utility_functions import prepare_time_features

with open('static/condition-mappings/visualCrossingEncodings.json', 'r') as file:
    visualCrossingEncodings = json.load(file)
visualCrossingEncodings_reversed = {v: k for k, v in visualCrossingEncodings.items()}


def prepare_classification_frame(prepared_forecast_data: pd.DataFrame):
    conditions1 = prepared_forecast_data[prepared_forecast_data['provider_id'] == 1][
        ['city_id', 'forecast_type_id', 'time', 'conditions']]
    conditions1.rename(columns={'conditions': 'conditions1'}, inplace=True)

    conditions2 = prepared_forecast_data[prepared_forecast_data['provider_id'] == 2][
        ['city_id', 'forecast_type_id', 'time', 'conditions']]
    conditions2.rename(columns={'conditions': 'conditions2'}, inplace=True)

    conditions3 = prepared_forecast_data[prepared_forecast_data['provider_id'] == 3][
        ['city_id', 'forecast_type_id', 'time', 'conditions']]
    conditions3.rename(columns={'conditions': 'conditions3'}, inplace=True)

    cond_final = pd.merge(conditions1, conditions2[['city_id', 'forecast_type_id', 'time', 'conditions2']],
                          on=['city_id', 'forecast_type_id', 'time'])
    cond_final = pd.merge(cond_final, conditions3[['city_id', 'forecast_type_id', 'time', 'conditions3']],
                          on=['city_id', 'forecast_type_id', 'time'])

    cond_final_exp = __expand_conditions(cond_final, 'conditions1')
    cond_final_exp = __expand_conditions(cond_final_exp, 'conditions2')

    cond_final_exp['c1_enc'] = cond_final_exp['conditions1'].map(visualCrossingEncodings)
    cond_final_exp['c2_enc'] = cond_final_exp['conditions2'].map(visualCrossingEncodings)
    cond_final_exp['c3_enc'] = cond_final_exp['conditions3'].map(visualCrossingEncodings)
    prepare_time_features(cond_final_exp)
    return cond_final_exp


def decode_predicted_conditions(predicted):
    return [visualCrossingEncodings_reversed[value] for value in predicted]



def __expand_conditions(df: pd.DataFrame, col_name: str):
    # Split the condition column by comma and strip any whitespace
    df_expanded = df[col_name].str.split(',', expand=True).stack().reset_index(level=1, drop=True)
    df_expanded = df_expanded.str.strip()
    # Join the expanded conditions with the original DataFrame
    df_expanded = df.drop(columns=[col_name]).join(df_expanded.rename(col_name))
    return df_expanded


def prepare_encoded_classification_frame(prepared_forecast_data:pd.DataFrame):
    conditions1 = prepared_forecast_data[prepared_forecast_data['provider_id'] == 1][
        ['city_id', 'forecast_type_id', 'time', 'conditions']]
    conditions1.rename(columns={'conditions': 'conditions1'}, inplace=True)

    conditions2 = prepared_forecast_data[prepared_forecast_data['provider_id'] == 2][
        ['city_id', 'forecast_type_id', 'time', 'conditions']]
    conditions2.rename(columns={'conditions': 'conditions2'}, inplace=True)

    conditions3 = prepared_forecast_data[prepared_forecast_data['provider_id'] == 3][
        ['city_id', 'forecast_type_id', 'time', 'conditions']]
    conditions3.rename(columns={'conditions': 'conditions3'}, inplace=True)

    cond_final = pd.merge(conditions1, conditions2[['city_id', 'forecast_type_id', 'time', 'conditions2']],
                          on=['city_id', 'forecast_type_id', 'time'])
    cond_final = pd.merge(cond_final, conditions3[['city_id', 'forecast_type_id', 'time', 'conditions3']],
                          on=['city_id', 'forecast_type_id', 'time'])

    cond_final['condtions_merged'] = cond_final[['conditions1', 'conditions2', 'conditions3']].agg('. '.join, axis=1)
    return cond_final
