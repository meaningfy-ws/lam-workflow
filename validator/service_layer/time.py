from datetime import datetime

from pytz import timezone

from validator.config import config


def get_timestamp() -> str:
    """
    generate a string timestamp based on the project's time format
    :return: timestamp
    """
    return datetime.now(tz=timezone(config.RDF_VALIDATOR_TIMEZONE)).strftime(config.RDF_VALIDATOR_TIME_FORMAT)
