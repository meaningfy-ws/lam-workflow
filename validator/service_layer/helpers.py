#!/usr/bin/python3

# helpers.py
# Date:  06/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com 

""" """
import logging
from pathlib import Path
from typing import List

from validator.config import config
from validator.entrypoints.api.helpers import TTL_EXTENSION

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)


class SHACLShapesMissing(Exception):
    """
        An exception to be raised when the lookup for the SHACL shape files fails.
    """


def create_file_name(filename: str, file_type: str = TTL_EXTENSION) -> str:
    return Path(filename).stem + f'-report.{file_type}'


def get_custom_shacl_shape_files() -> List[str]:
    """
    Get the SHACL shape files from RDF_VALIDATOR_SHACL_SHAPES_PATH if path is specified
    :return: list of SHACL shapes files
    """
    shacl_shape_files = list()
    if config.RDF_VALIDATOR_SHACL_SHAPES_LOCATION:
        shacl_shape_files = [str(item) for item in Path(config.RDF_VALIDATOR_SHACL_SHAPES_LOCATION).iterdir()]
        if not shacl_shape_files:
            exception_text = f'No SHACL shape files found at {config.RDF_VALIDATOR_SHACL_SHAPES_LOCATION}'
            logger.exception(exception_text)
            raise SHACLShapesMissing(exception_text)

    return shacl_shape_files
