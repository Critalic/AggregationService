import logging


def configure_logging():
    logger_error = logging.getLogger()
    logger_error.setLevel(logging.ERROR)

    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(formatter)

    logger_error.addHandler(error_handler)
