import logging as logger
from pathlib import Path
from uuid import uuid4

from werkzeug.datastructures import FileStorage

from validator.config import config
from validator.utils.file import save_file


def save_data_for_validation(file_to_validate: FileStorage, shacl_shapes: list,
                             location: str = config.RDF_VALIDATOR_FILE_DB):
    """
    service to save files to be used by the celery tasks
    :param file_to_validate: validation file to be saved to local storage
    :param shacl_shapes: list of shapes to be saved to local storage
    :param location: location of storage
    :return: local storage location, validation file location, list of shapes locations
    """
    location_to_save = Path(location) / str(uuid4())
    location_to_save.mkdir()

    try:
        saved_file_to_validate = save_file(file_to_validate, location_to_save)
    except TypeError:
        saved_file_to_validate = None
        logger.debug('no validation file to save')
    saved_shacl_files = [save_file(shacl_file, location_to_save) for shacl_file in shacl_shapes]

    return str(location_to_save), saved_file_to_validate, saved_shacl_files
