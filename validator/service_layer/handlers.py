#!/usr/bin/python3

# service.py
# Date:  21/09/2020
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

""" """
import json
import logging as logger
import pathlib
from distutils.dir_util import copy_tree
from pathlib import Path
from shutil import copytree
from typing import List, Union
from urllib.parse import urlparse

from eds4jinja2.builders.report_builder import ReportBuilder
from werkzeug.exceptions import UnprocessableEntity

from validator.adapters.validator_wrapper import AbstractValidatorWrapper, RDFUnitWrapper
from validator.config import config


def __copy_static_content(configuration_context: dict) -> None:
    """
    :param configuration_context: the configuration context for the currently executing processing pipeline
    :rtype: None
    """
    if pathlib.Path(configuration_context["static_folder"]).is_dir():
        copytree(configuration_context["static_folder"], configuration_context["output_folder"])
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
    cli_output = validator_wrapper.execute_subprocess("-jar", config.RDF_VALIDATOR_RDFUNIT_LOCATION,
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

    cli_output = validator_wrapper.execute_subprocess("-jar", config.RDF_VALIDATOR_RDFUNIT_LOCATION,
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


def build_report(temp_dir: str, template_location: str, additional_config: dict):
    """
    :param temp_dir: location to temporarily save the report
    :param template_location: report location
    :param application_profile: application profile for report identification
    :param dataset_id: dataset name
    :param dataset: data about dataset
    :param timestamp: time of report creation
    :param source_file: ttl file
    :return:
    """
    logger.debug(f'template location {template_location}')

    copy_tree(template_location, temp_dir)

    try:
        with open(Path(temp_dir) / 'config.json', 'r') as config_file:
            config_content = json.load(config_file)

        logger.debug(f'template file {config_content["template"]}')
    except FileNotFoundError as e:
        logger.exception(str(e))
        raise UnprocessableEntity("config.json file is missing from the chosen template variant folder")

    report_builder = ReportBuilder(target_path=temp_dir, additional_config=additional_config)
    report_builder.make_document()
    return Path(str(temp_dir)) / f'output/{config_content["template"]}'
