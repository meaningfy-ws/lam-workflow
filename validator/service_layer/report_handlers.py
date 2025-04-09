import logging as logger
import shutil
from json import loads, dumps
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from werkzeug.utils import secure_filename

from validator.config import config
from validator.utils.constants import EXTENSION_TO_FILETYPE
from validator.service_layer.handlers import run_file_validator, build_report, run_sparql_endpoint_validator
from validator.service_layer.helpers import get_custom_shacl_shape_files, SHACLShapesMissing
from validator.service_layer.time import get_timestamp
from validator.utils.file import copy_file_to_destination, \
    list_folders_from_path, build_unique_name, list_folder_paths_from_path


def zip_report_files(location: str, html_report: str, ttl_report: str, custom_html_report_path: str,
                     custom_json_report_path: str) -> str:
    """
    Method to zip files
    :param location: location to create zip
    :param html_report: html report location
    :param ttl_report: ttl report location
    :param custom_html_report_path: custom html report location
    :param custom_json_report_path: custom JSON report location
    :return: location of the zip
    """
    logger.debug('zipping report')
    zip_location = str(Path(location) / config.RDF_VALIDATOR_ZIP_REPORT_NAME)
    with ZipFile(zip_location, 'w') as zip_report:
        zip_report.write(html_report, arcname=config.RDF_VALIDATOR_HTML_REPORT_NAME)
        zip_report.write(ttl_report, arcname=config.RDF_VALIDATOR_TTL_REPORT_NAME)
        zip_report.write(custom_html_report_path, arcname=config.RDF_VALIDATOR_CUSTOM_HTML_REPORT_NAME)
        zip_report.write(custom_json_report_path, arcname=config.RDF_VALIDATOR_CUSTOM_JSON_REPORT_NAME)
    return zip_location


def copy_report_files(html_report: str, ttl_report: str, custom_html_report: str, custom_json_report: str,
                      zip_report: str, timestamp: str) -> Path:
    """
    Method to copy reports from temporary director to the reports location
    :param html_report: html report location
    :param ttl_report: ttl report location
    :param custom_html_report: custom html report location
    :param custom_json_report: custom JSON report location
    :param zip_report: zip location containing all reports
    :param timestamp: timestamp of creation date
    :return: location of copied reports
    """
    reports_location = Path(config.RDF_VALIDATOR_REPORTS_DB) / build_unique_name(timestamp)
    reports_location.mkdir()

    copy_file_to_destination(html_report, str(reports_location / config.RDF_VALIDATOR_HTML_REPORT_NAME))
    copy_file_to_destination(ttl_report, str(reports_location / config.RDF_VALIDATOR_TTL_REPORT_NAME))
    copy_file_to_destination(custom_html_report, str(reports_location / config.RDF_VALIDATOR_CUSTOM_HTML_REPORT_NAME))
    copy_file_to_destination(custom_json_report, str(reports_location / config.RDF_VALIDATOR_CUSTOM_JSON_REPORT_NAME))
    copy_file_to_destination(zip_report, str(reports_location / config.RDF_VALIDATOR_ZIP_REPORT_NAME))
    return reports_location


def generate_meta_file(reports_location: Path, schema_files: list, file_name: str = '', url: str = '', uid: str = '',
                       timestamp: str = '', type: str = 'file', html_report: str = '', ttl_report: str = '',
                       custom_html_report: str = '', custom_json_report: str = '', zip_report: str = '',
                       application_profile: str = '',
                       graphs: list = None) -> str:
    """
    method to generate meta file

    :param reports_location: location of validation reports
    :param file_name: the name of the file validated
    :param url: the name of the sparql endpoint validated
    :param schema_files: the locations of the schema files
    :param uid: validation unique identifier
    :param timestamp: timestamp of validation creation
    :param type: file/url
    :param html_report: name of the default html report
    :param ttl_report: name of the default ttl report
    :param custom_html_report: name of the custom html report
    :param custom_json_report: name of the custom json report
    :param zip_report: name of the zip containing all reports
    :param application_profile: application profile if provided
    :param graphs: the URIs of the graphs
    :return: location of meta file
    """
    timestamp = timestamp or get_timestamp()
    html_report = html_report or config.RDF_VALIDATOR_HTML_REPORT_NAME
    ttl_report = ttl_report or config.RDF_VALIDATOR_TTL_REPORT_NAME
    custom_html_report = custom_html_report or config.RDF_VALIDATOR_CUSTOM_HTML_REPORT_NAME
    custom_json_report = custom_json_report or config.RDF_VALIDATOR_CUSTOM_JSON_REPORT_NAME
    zip_report = zip_report or config.RDF_VALIDATOR_ZIP_REPORT_NAME

    meta = {
        "uid": uid or str(uuid4()),
        "type": type,
        "html_report": html_report,
        "file": file_name,
        "url": url,
        "graphs": graphs,
        "ttl_report": ttl_report,
        "custom_html_report": custom_html_report,
        "custom_json_report": custom_json_report,
        "zip_report": zip_report,
        "created_at": timestamp,
        "shacl_shape_files": schema_files,
        "application_profile": application_profile
    }

    meta_file = reports_location / config.RDF_VALIDATOR_REPORT_META_NAME
    meta_file.write_text(dumps(meta))
    return str(meta_file)


def read_meta_file(report_base_location: str, meta_file_name: str = '') -> dict:
    """
    method to read data from meta file
    :param report_base_location: report location
    :param meta_file_name: custom meta name, defaults to "meta.json"
    :return: contents of the meta file
    """
    meta_file_name = meta_file_name or config.RDF_VALIDATOR_REPORT_META_NAME
    return loads((Path(report_base_location) / meta_file_name).read_text())


def generate_reports_from_file(data_file: str, schema_files: list, location: str, additional_config: dict) -> tuple:
    """
    method to run validation generation for a file and build the custom report

    :param data_file: file to validate
    :param schema_files: The content of the SHACL shape files defining the validation constraints
    :param location: location to build reports
    :param additional_config: additional report builder config
    :return: locations of the reports
    """
    html_report, ttl_report = run_file_validator(data_file=data_file,
                                                 schemas=schema_files,
                                                 output=str(Path(location)) + '/')

    additional_config["conf"]["report_data_file"] = ttl_report

    custom_html_report_path = build_report(temp_dir=location,
                                           template_location=config.RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION,
                                           additional_config=additional_config)

    custom_json_report_path = build_report(temp_dir=location,
                                           template_location=config.RDF_VALIDATOR_JSON_REPORT_TEMPLATE_LOCATION,
                                           additional_config=additional_config)

    zip_location = zip_report_files(location=location, html_report=html_report, ttl_report=ttl_report,
                                    custom_html_report_path=custom_html_report_path,
                                    custom_json_report_path=custom_json_report_path)

    return html_report, ttl_report, str(custom_html_report_path), str(custom_json_report_path), zip_location


def generate_reports_from_url(sparql_endpoint: str, graphs: list, schema_files: list, location: str,
                              additional_config: dict) -> tuple:
    """
    method to run validation generation for a url  and build the custom report

    :param sparql_endpoint: endpoint to validate data from
    :param graphs: the URIs of the graphs
    :param schema_files: The content of the SHACL shape files defining the validation constraints
    :param location: location to build reports
    :param additional_config: additional report builder config
    :return: locations of the reports
    """
    html_report, ttl_report = run_sparql_endpoint_validator(sparql_endpoint_url=sparql_endpoint,
                                                            graphs_uris=graphs,
                                                            schemas=schema_files,
                                                            output=str(Path(location)) + '/')

    additional_config["conf"]["report_data_file"] = ttl_report

    custom_html_report_path = build_report(temp_dir=location,
                                           template_location=config.RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION,
                                           additional_config=additional_config)

    custom_json_report_path = build_report(temp_dir=location,
                                           template_location=config.RDF_VALIDATOR_JSON_REPORT_TEMPLATE_LOCATION,
                                           additional_config=additional_config)

    zip_location = zip_report_files(location=location, html_report=html_report, ttl_report=ttl_report,
                                    custom_html_report_path=custom_html_report_path,
                                    custom_json_report_path=custom_json_report_path)

    return html_report, ttl_report, str(custom_html_report_path), str(custom_json_report_path), zip_location


def build_report_from_file(location: str, data_file: str, schema_files: list, application_profile: str = '',
                           uid: str = '') -> str:
    """
    method to build file validation reports and copy them to the report destination location

    :param location: location to build reports
    :param data_file: file to validate
    :param schema_files: shacl schema files
    :param application_profile: application profile if provided
    :param uid: validation identifier
    :return: reports location
    """
    logger.debug('start building report from file')
    uid = uid or str(uuid4())
    timestamp = get_timestamp()

    if config.RDF_VALIDATOR_SHACL_SHAPES_LOCATION:
        schema_files += get_custom_shacl_shape_files()
    if not schema_files:
        exception_text = f'No SHACL shape files provided for validation'
        logger.exception(exception_text)
        raise SHACLShapesMissing(exception_text)

    additional_config = {
        "conf": {
            "application_profile": application_profile,
            "timestamp": timestamp,
            "title": config.RDF_VALIDATOR_REPORT_TITLE
        }
    }
    html_report, ttl_report, custom_html_report, custom_json_report, zip_report = generate_reports_from_file(
        data_file=data_file,
        schema_files=schema_files,
        location=location,
        additional_config=additional_config)

    reports_location = copy_report_files(html_report=html_report, ttl_report=ttl_report,
                                         custom_html_report=custom_html_report, custom_json_report=custom_json_report,
                                         zip_report=zip_report, timestamp=timestamp)

    generate_meta_file(reports_location=reports_location, file_name=data_file, schema_files=schema_files,
                       timestamp=timestamp, type='file', application_profile=application_profile, uid=uid)

    return str(reports_location)


def build_report_from_url(location: str, sparql_endpoint: str, graphs: list, schema_files: list,
                          application_profile: str = '', uid: str = '') -> str:
    """
    method to build spqrql endpoint validation reports and copy them to the report destination location

    :param location: location to build reports
    :param sparql_endpoint: sparql endpoint to validate
    :param graphs: the URIs of the graphs
    :param schema_files: shacl schema files
    :param application_profile: application profile if provided
    :param uid: validation identifier
    :return: reports location
    """
    logger.debug('start building report from url')
    uid = uid or str(uuid4())
    timestamp = get_timestamp()

    if config.RDF_VALIDATOR_SHACL_SHAPES_LOCATION:
        schema_files += get_custom_shacl_shape_files()
    if not schema_files:
        exception_text = f'No SHACL shape files provided for validation'
        logger.exception(exception_text)
        raise SHACLShapesMissing(exception_text)

    additional_config = {
        "conf": {
            "application_profile": application_profile,
            "timestamp": timestamp,
            "sparql_endpoint": sparql_endpoint,
            "title": config.RDF_VALIDATOR_REPORT_TITLE
        }
    }
    html_report, ttl_report, custom_html_report, custom_json_report, zip_report = generate_reports_from_url(
        sparql_endpoint,
        graphs,
        schema_files,
        location,
        additional_config)

    reports_location = copy_report_files(html_report=html_report, ttl_report=ttl_report,
                                         custom_html_report=custom_html_report, custom_json_report=custom_json_report,
                                         zip_report=zip_report, timestamp=timestamp)

    generate_meta_file(reports_location=reports_location, url=sparql_endpoint, graphs=graphs, schema_files=schema_files,
                       timestamp=timestamp, type='url', application_profile=application_profile, uid=uid)

    return str(reports_location)


def build_validation_reports_location(validation_uid: str, db_location: str) -> str:
    """
    method to search for report based on the validation id
    :param validation_uid: uid of the validation
    :param db_location: which file system location to use to perform the action
    :return: location of reports
    """
    for location in list_folders_from_path(Path(db_location)):
        content = read_meta_file(Path(db_location) / location)
        if content.get('uid', None) == validation_uid:
            return str(Path(db_location) / location)

    return ''


def get_available_validations(reports_location: str = config.RDF_VALIDATOR_REPORTS_DB) -> list:
    """
    Method to get all available validation
    :param reports_location: location to search for reports
    :return: list of meta data content for found reports
    """
    reports = list()
    for validation_location in list_folder_paths_from_path(Path(reports_location)):
        reports.append(read_meta_file(str(validation_location)))

    return reports


def get_report(validation_uid: str, extension: str, db_location: str) -> tuple:
    """
    build absolute report path including the filename

    :param validation_uid: uid of the validation
    :param extension: report extension
    :param db_location: which file system location to use to perform the action
    :return: absolute path
    """
    report_base_location = build_validation_reports_location(validation_uid, db_location)
    meta = read_meta_file(report_base_location)
    filename = secure_filename(f"{meta['uid']}-{meta['created_at']}.{extension}")

    return Path(report_base_location) / meta[EXTENSION_TO_FILETYPE[extension]], filename


def remove_report(validation_uid: str, db_location: str = config.RDF_VALIDATOR_REPORTS_DB) -> bool:
    """
    remove report

    :param validation_uid: validation id
    :param db_location: which file system location to use to perform the action
    :return: if report successfully deleted return true otherwise return false
    """
    report_location = build_validation_reports_location(validation_uid=validation_uid, db_location=db_location)
    try:
        shutil.rmtree(report_location)
        return True
    except FileNotFoundError as e:
        logger.debug(
            f'no validation with {validation_uid} exists. nothing to delete.')

    return False


def remove_all_reports(db_location: str = config.RDF_VALIDATOR_REPORTS_DB):
    """
    remove all reports
    :param db_location: which file system location to use to perform the action
    """
    for meta in get_available_validations(db_location):
        remove_report(meta.get('uid'), db_location)
