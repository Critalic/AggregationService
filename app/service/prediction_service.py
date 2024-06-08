import pickle
import numpy as np
import tensorflow_hub as hub
import pandas as pd

from app.service.models.preprocessing_service import preprocess_data
from app.service.models.regression_prep_service import prepare_regression_frame
from app.service.models.classification_prep_service import prepare_classification_frame, decode_predicted_conditions, \
    prepare_encoded_classification_frame

embedding = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")


def build_predictions(forecasts: pd.DataFrame):
    print('Building predictions')
    forecasts_prepared = preprocess_data(forecasts)

    conditions_predicted = predict_classify_encoded('conditions', 'net_classifier', forecasts_prepared)

    humidity_predicted = __predict_regress('humidity', 'humidity_regressor', forecasts_prepared)
    temperature_predicted = __predict_regress('temperature', 'temperature_regressor', forecasts_prepared)
    pressure_predicted = __predict_regress('pressure', 'pressure_regressor', forecasts_prepared)
    win_direction_predicted = __predict_regress('wind_direction', 'win_direction_regressor', forecasts_prepared)
    win_speed_predicted = __predict_regress('wind_speed', 'win_speed_regressor', forecasts_prepared)

    result = pd.merge(humidity_predicted[['city_id', 'forecast_type_id', 'time', 'predicted_humidity']],
                      temperature_predicted[['city_id', 'forecast_type_id', 'time', 'predicted_temperature']],
                      on=['city_id', 'forecast_type_id', 'time'])
    result = pd.merge(result,
                      conditions_predicted[['city_id', 'forecast_type_id', 'time', 'predicted_conditions']],
                      on=['city_id', 'forecast_type_id', 'time'])
    result = pd.merge(result,
                      pressure_predicted[['city_id', 'forecast_type_id', 'time', 'predicted_pressure']],
                      on=['city_id', 'forecast_type_id', 'time'])
    result = pd.merge(result,
                      win_direction_predicted[['city_id', 'forecast_type_id', 'time', 'predicted_wind_direction']],
                      on=['city_id', 'forecast_type_id', 'time'])
    result = pd.merge(result,
                      win_speed_predicted[['city_id', 'forecast_type_id', 'time', 'predicted_wind_speed']],
                      on=['city_id', 'forecast_type_id', 'time'])

    result.rename(columns={'predicted_humidity': 'humidity',
                           'predicted_temperature': 'temperature',
                           'predicted_conditions': 'conditions',
                           'predicted_pressure': 'pressure',
                           'predicted_wind_direction': 'wind_direction',
                           'predicted_wind_speed': 'wind_speed'}, inplace=True)

    print('Predictions built')
    return result


def __predict_regress(target_name: str, model_name: str, dataframe: pd.DataFrame):
    prepared_df = prepare_regression_frame(dataframe, target_name)
    features = prepared_df[[col for col in prepared_df.columns if (col != 'time')]]

    with open(f'static/{model_name}.pkl', 'rb') as file:
        data = pickle.load(file)
    regressor_loaded = data["model"]
    predicted = regressor_loaded.predict(features)

    prepared_df[f'predicted_{target_name}'] = predicted
    return prepared_df


def predict_classify(target_name: str, model_name: str, dataframe: pd.DataFrame):
    prepared_df = prepare_classification_frame(dataframe)
    features = prepared_df[['city_id', 'forecast_type_id', 'c1_enc', 'c2_enc', 'c3_enc', 'month', 'day', 'hour']]

    with open(f'static/{model_name}.pkl', 'rb') as file:
        data = pickle.load(file)
    classifier_loaded = data["model"]
    predicted = decode_predicted_conditions(classifier_loaded.predict(features))

    prepared_df[f'predicted_{target_name}'] = predicted
    shrunken = prepared_df.groupby(['time', 'city_id', 'forecast_type_id'], as_index=False).agg({
        f'predicted_{target_name}': lambda x: ','.join(set(x))
    })
    return shrunken


def predict_classify_encoded(target_name: str, model_name: str, dataframe: pd.DataFrame):
    prepared_df = prepare_encoded_classification_frame(dataframe)
    embedded_conditions = embedding(prepared_df['condtions_merged'].to_list()).numpy()

    with open(f'static/{model_name}.pkl', 'rb') as file:
        data = pickle.load(file)
    classifier_loaded = data["model"]
    predicted = classifier_loaded.predict(embedded_conditions)
    predicted_unembedded = decode_predicted_conditions([np.argmax(i) for i in predicted])

    prepared_df[f'predicted_{target_name}'] = predicted_unembedded
    return prepared_df
