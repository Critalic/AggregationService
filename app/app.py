from authlib.integrations.flask_oauth2 import ResourceProtector
from flask import Flask, jsonify, Response, request

from app.service.business_service import aggregate_forecast_for_timestamp
from app.util.utility_functions import is_valid_datetime
from app.configuration.logging_config import configure_logging
from app.service.security_validator import Auth0JWTBearerTokenValidator

require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    "https://EXAMPLE.auth0.com/",
    "example@gmail.com"
)
require_auth.register_token_validator(validator)

APP = Flask(__name__)
configure_logging()


@APP.route("/api/v1/checkstate")
@require_auth(None)
def public():
    response = (
        "Server is running"
    )
    return jsonify(message=response)


@APP.route("/api/v1/weather/aggregate")
@require_auth(None)
def aggregate_for_timestamp():
    timestamp = request.args.get('timestamp')
    print(f'Input to aggregate_for_timestamp: {timestamp}')

    if (timestamp is not None) and is_valid_datetime(timestamp):
        aggregate_forecast_for_timestamp(timestamp)
        return Response(status=200)
    else:
        return Response(status=400)
