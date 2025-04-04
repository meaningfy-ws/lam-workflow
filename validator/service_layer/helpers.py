#!/usr/bin/python3

# helpers.py
# Date:  06/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com 

""" """
import logging as logger
from datetime import datetime
from pathlib import Path
from typing import List

from shortuuid import ShortUUID

from validator.config import config


class SHACLShapesMissing(Exception):
    """
        An exception to be raised when the lookup for the SHACL shape files fails.
    """


def create_file_name(file_name_base: str, extension: str, uuid_length: int = 6) -> str:
    now = datetime.now()
    return f'{file_name_base}-{now.year}-{now.month}-{now.day}-{ShortUUID().random(length=uuid_length)}.{extension}'


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
