#!/usr/bin/python3

# service.py
# Date:  21/09/2020
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

""" """
import json
import logging
import pathlib
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse
from zipfile import ZipFile

from eds4jinja2.builders.report_builder import ReportBuilder

from validator.adapters.validator_wrapper import AbstractValidatorWrapper, RDFUnitWrapper
from validator.config import config
from validator.entrypoints.api.helpers import TTL_EXTENSION, HTML_EXTENSION, ZIP_EXTENSION
from validator.service_layer.helpers import create_file_name, get_custom_shacl_shape_files, SHACLShapesMissing

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)


def __copy_static_content(configuration_context: dict) -> None:
    """
    :param configuration_context: the configuration context for the currently executing processing pipeline
    :rtype: None
    """
    if pathlib.Path(configuration_context["static_folder"]).is_dir():
        copy_tree(configuration_context["static_folder"], configuration_context["output_folder"])
    else:
        logger.warning(configuration_context["static_folder"] + " is not a directory !")


def run_file_validator(data_file: str, schemas: List[str], output: Union[str, Path]) -> tuple:
    """
        Execute the RDF Unit or any other validator.
        Possibilities: upload output to a SPARQL endpoint, or write it into a file.
    :type schemas: object
    :param data_file: defines the actual location of the file
    :param schemas: schemas also required for running an evaluation
    :param output: the output directory
    :return: a tuple of the output file paths

    Please see https://github.com/AKSW/RDFUnit/wiki/CLI for a comprehensive description of the parameters
    """
    logger.debug("RDFUnitWrapper starting ...")
    validator_wrapper: AbstractValidatorWrapper
    validator_wrapper = RDFUnitWrapper("java")
    cli_output = validator_wrapper.execute_subprocess("-jar", "/usr/src/rdfunit/rdfunit-validate.jar",
                                                      "-d", data_file,
                                                      "-u", data_file,
                                                      "-s", ", ".join([schema for schema in schemas]),
                                                      "-r", 'shacl',
                                                      "-o", 'html,ttl',
                                                      "-f", str(output))
    logger.debug("RDFUnitWrapper finished with output:\n" + cli_output)

    output_file_name = str(Path(data_file).parent).replace('/', '_') + '_' + Path(
        data_file).name + ".shaclTestCaseResult"
    output_file_full_path = Path(output) / 'results' / output_file_name
    return str(output_file_full_path) + ".html", str(output_file_full_path) + ".ttl"


def run_sparql_endpoint_validator(sparql_endpoint_url: str, graphs_uris: List[str],
                                  schemas: List[str], output: Union[str, Path]) -> tuple:
    """
        Execute the RDF Unit or any other validator.
        Possibilities: upload output to a SPARQL endpoint, or write it into a file.
    :param sparql_endpoint_url: You can run RDFUnit directly on a SPARQL endpoint using this parameter
    :param graphs_uris: the URIs of the graphs
    :param schemas: schemas also required for running an evaluation
    :param output: the output directory
    :return: a tuple of the output file paths

    Please see https://github.com/AKSW/RDFUnit/wiki/CLI for a comprehensive description of the parameters
    """

    logger.debug("RDFUnitWrapper starting ...")
    validator_wrapper: AbstractValidatorWrapper
    validator_wrapper = RDFUnitWrapper("java")

    sparql_endpoint_url = sparql_endpoint_url.strip()

    if graphs_uris is None or len(graphs_uris) == 0:
        graph_param = ""
    else:
        graph_param = ", ".join([graph for graph in graphs_uris])

    cli_output = validator_wrapper.execute_subprocess("-jar", "/usr/src/rdfunit/rdfunit-validate.jar",
                                                      "-d", sparql_endpoint_url,
                                                      "-e", sparql_endpoint_url,
                                                      "-s", ", ".join([schema for schema in schemas]),
                                                      "-r", 'shacl',
                                                      "-C", "-T", "0", "-D", str(config.RDFUNIT_QUERY_DELAY_MS),
                                                      "-o", 'html,ttl',
                                                      "-f", str(output),
                                                      "-g", graph_param)
    logger.debug("RDFUnitWrapper finished with output:\n" + cli_output)

    parsed_uri = urlparse(sparql_endpoint_url)
    output_file_name = parsed_uri.netloc.replace(":", "_") + \
                       parsed_uri.path.replace("/", "_") + \
                       ".shaclTestCaseResult"
    output_file_path = Path(output) / 'results' / output_file_name
    return str(output_file_path) + ".html", str(output_file_path) + ".ttl"


def generate_validation_report(path_to_report: Union[str, Path]) -> str:
    """
        Generate the jinja HTML report.
        Warning: we have to decide what will be the report sources.
        Possibilities: (a) either write a new DataSourceAdapter in the eds4jinja project or
                       (b) use a temporary Fuseki instance,w here the validation report is
                       loaded and the report is generated from there.  (For this we have to write a Fuseki adapter)
    :param path_to_report: the location of the template file(s) that will be used to render the output
    :return: path to the html report
    """
    report_builder = ReportBuilder(path_to_report,
                                   additional_config={'conf': {'title': config.RDF_VALIDATOR_REPORT_TITLE}})
    report_builder.add_after_rendering_listener(__copy_static_content)
    report_builder.make_document()
    return str(path_to_report) + "/output/" + "main.html"


def prepare_eds4jinja_context(report_path, source_file):
    logger.debug(f"Building with template location: {config.RDF_VALIDATOR_REPORT_TEMPLATE_LOCATION}")
    copy_tree(config.RDF_VALIDATOR_REPORT_TEMPLATE_LOCATION, report_path)

    with open(Path(report_path) / "config.json", 'r+') as config_file:
        config_data = json.load(config_file)
        config_data["conf"]["report_data_file"] = source_file
        logger.debug(config_data)
        config_file.seek(0)
        json.dump(config_data, config_file)
        config_file.truncate()


def create_report(location: str, html_report: str, ttl_report: str, extension: str, file_name: str):
    logger.debug(f'start creating report with extension {extension}')
    if extension == TTL_EXTENSION:
        report_path = ttl_report
        report_filename = create_file_name(file_name_base=file_name, extension=TTL_EXTENSION)

    elif extension == HTML_EXTENSION:
        logger.debug('generate HTML report')
        prepare_eds4jinja_context(location, ttl_report)
        report_path = generate_validation_report(location)
        report_filename = create_file_name(file_name_base=file_name, extension=HTML_EXTENSION)

    elif extension == ZIP_EXTENSION:
        logger.debug('generate HTML report')
        prepare_eds4jinja_context(location, ttl_report)
        shacl_html_report = generate_validation_report(location)

        ttl_filename = create_file_name(file_name_base=file_name, extension=TTL_EXTENSION)
        html_filename = create_file_name(file_name_base=file_name, extension=HTML_EXTENSION)
        shacl_html_filename = create_file_name(file_name_base='shacl-' + file_name, extension=HTML_EXTENSION)
        report_filename = create_file_name(file_name_base=file_name, extension=ZIP_EXTENSION)

        logger.debug('zipping report')
        report_path = str(Path(location) / 'report.zip')
        with ZipFile(report_path, 'w') as zip_report:
            zip_report.write(html_report, arcname=html_filename)
            zip_report.write(shacl_html_report, arcname=shacl_html_filename)
            zip_report.write(ttl_report, arcname=ttl_filename)

    logger.debug(f'finish creating report with extension {extension}')
    return report_path, report_filename


def build_report_from_file(location: str, data_file: str, schema_files: list, extension: str) -> tuple:
    logger.debug('start building report from file')

    if config.RDF_VALIDATOR_SHACL_SHAPES_LOCATION:
        schema_files += get_custom_shacl_shape_files()
    if not schema_files:
        exception_text = f'No SHACL shape files provided for validation'
        logger.exception(exception_text)
        raise SHACLShapesMissing(exception_text)

    html_report, ttl_report = run_file_validator(data_file=data_file,
                                                 schemas=schema_files,
                                                 output=str(Path(location)) + '/')

    return create_report(location, html_report, ttl_report, extension, config.RDF_VALIDATOR_FILE_NAME_BASE)


def build_report_from_sparql_endpoint(location: str, endpoint: str, graphs: list, schema_files: list, extension: str) -> tuple:
    logger.debug('start building report from sparql endpoint')

    if config.RDF_VALIDATOR_SHACL_SHAPES_LOCATION:
        schema_files += get_custom_shacl_shape_files()
    if not schema_files:
        exception_text = f'No SHACL shape files provided for validation'
        logger.exception(exception_text)
        raise SHACLShapesMissing(exception_text)

    html_report, ttl_report = run_sparql_endpoint_validator(sparql_endpoint_url=endpoint,
                                                            graphs_uris=graphs,
                                                            schemas=schema_files,
                                                            output=str(Path(location)) + '/')

    return create_report(location, html_report, ttl_report, extension, config.RDF_VALIDATOR_FILE_NAME_BASE)
