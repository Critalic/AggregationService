from app.persistence.persistence_service import read_forecasts_with_timestamp, \
    persist_forecasts
from app.service.prediction_service import build_predictions


def aggregate_forecast_for_timestamp(timestamp: str):
    forecasts = read_forecasts_with_timestamp(timestamp)
    predictions_dataframe = build_predictions(forecasts)
    predictions_dataframe['provider_id'] = 4
    predictions_dataframe['time_stamp'] = timestamp
    persist_forecasts(predictions_dataframe)
