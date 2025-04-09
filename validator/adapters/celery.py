import logging as logger
import shutil

from celery import Celery

from validator.config import config
from validator.service_layer.report_handlers import build_report_from_file, build_report_from_url

celery_worker = Celery('rdf-validator-tasks',
                       broker=config.RDF_VALIDATOR_REDIS_SERVICE,
                       backend=config.RDF_VALIDATOR_REDIS_SERVICE)
celery_worker.conf.update(result_extended=True)

CELERY_VALIDATE_FILE = 'validate_file'
CELERY_VALIDATE_URL = 'validate_url'


@celery_worker.task(name=CELERY_VALIDATE_FILE, bind=True)
def async_validate_file(self, uid: str, data_file: str, shacl_shapes: list, db_cleanup_location: str,
                        application_profile: str = ''):
    """
    Task that to validate a file

    NOTE: the order of the first arg is important for task cancellation, don't change its order
    :param uid: validation identifier
    :param data_file: The file to be validated
    :param shacl_shapes: The content of the SHACL shape files defining the validation constraints
    :param db_cleanup_location: location to cleanup
    :param application_profile: application profile if provided
    """
    report_path = build_report_from_file(location=db_cleanup_location,
                                         data_file=str(data_file),
                                         schema_files=shacl_shapes,
                                         application_profile=application_profile,
                                         uid=uid)

    shutil.rmtree(db_cleanup_location)

    logger.debug(f'finish file validation  at {report_path}')
    return True


@celery_worker.task(name=CELERY_VALIDATE_URL, bind=True)
def async_validate_url(self, uid: str, sparql_endpoint: str, graphs: list, shacl_shapes: list, db_cleanup_location: str,
                       application_profile: str = ''):
    """
    Task that to validate a sparql endpoint

    NOTE: the order of the first arg is important for task cancellation, don't change its order
    :param uid: validation identifier
    :param sparql_endpoint: SPARQL endpoint to validate data from
    :param graphs: the URIs of the graphs
    :param shacl_shapes: The content of the SHACL shape files defining the validation constraints
    :param db_cleanup_location: location to cleanup
    :param application_profile: application profile if provided
    """
    report_path = build_report_from_url(location=db_cleanup_location,
                                        sparql_endpoint=sparql_endpoint,
                                        graphs=graphs,
                                        schema_files=shacl_shapes,
                                        application_profile=application_profile,
                                        uid=uid)

    if db_cleanup_location:
        shutil.rmtree(db_cleanup_location)

    logger.debug(f'finish url validation  at {report_path}')
    return True
