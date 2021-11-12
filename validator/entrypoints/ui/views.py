#!/usr/bin/python3

# views.py
# Date:  24/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
UI pages

"""
import logging
import tempfile
from pathlib import Path

from flask import render_template, flash, send_from_directory, redirect, url_for

from validator.config import config
from validator.entrypoints.api.helpers import TTL_EXTENSION
from validator.entrypoints.ui import app
from validator.entrypoints.ui.api_wrapper import validate_file as api_validate_file, \
    validate_sparql_endpoint as api_validate_sparql_endpoint
from validator.entrypoints.ui.forms import ValidateFromFileForm, ValidateSPARQLEndpointForm
from validator.entrypoints.ui.helpers import get_error_message_from_response
from validator.service_layer.helpers import create_file_name

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)


@app.route('/', methods=['GET'])
def index():
    logger.debug('request index view')
    logger.debug('redirect to validate file view')
    return redirect(url_for('validate_file'))


@app.route('/validate-file', methods=['GET', 'POST'])
def validate_file():
    logger.debug('request validate file view')

    form = ValidateFromFileForm()

    if form.validate_on_submit():
        response, status = api_validate_file(
            report_extension=form.report_extension.data,
            data_file=form.data_file.data,
            schema_files=form.schema_files.data
        )

        if status != 200:
            exception_text = get_error_message_from_response(response)
            logger.exception(exception_text)
            flash(exception_text, 'error')
        else:
            report_extension = form.report_extension.data if form.report_extension.data else TTL_EXTENSION

            with tempfile.TemporaryDirectory() as temp_folder:
                file_name = create_file_name(config.RDF_VALIDATOR_FILE_NAME_BASE, report_extension)
                report = Path(temp_folder) / file_name
                report.write_bytes(response)
                logger.debug('render validate file view')
                return send_from_directory(Path(temp_folder), file_name, as_attachment=True)

    logger.debug('render validate file clean view')
    return render_template('validate/file.html', form=form, title='Validate File',
                           validator_name=config.RDF_VALIDATOR_UI_NAME,
                           render_shacl_shapes=config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES)


@app.route('/validate-sparql-endpoint', methods=['GET', 'POST'])
def validate_sparql_endpoint():
    logger.debug('request validate sparql endpoint view')

    form = ValidateSPARQLEndpointForm()

    if form.validate_on_submit():
        response, status = api_validate_sparql_endpoint(
            report_extension=form.report_extension.data,
            sparql_endpoint_url=form.endpoint_url.data,
            schema_files=form.schema_files.data,
            graphs=form.graphs.data.split()
        )

        if status != 200:
            exception_text = get_error_message_from_response(response)
            logger.exception(exception_text)
            flash(exception_text, 'error')
        else:
            report_extension = form.report_extension.data if form.report_extension.data else TTL_EXTENSION

            with tempfile.TemporaryDirectory() as temp_folder:
                file_name = create_file_name(config.RDF_VALIDATOR_FILE_NAME_BASE, report_extension)
                report = Path(temp_folder) / file_name
                report.write_bytes(response)
                logger.debug('render validate sparql endpoint view')
                return send_from_directory(Path(temp_folder), file_name, as_attachment=True)

    logger.debug('request validate sparql endpoint clean view')
    return render_template('validate/sparql_endpoint.html', form=form, title='Validate SPARQL Endpoint',
                           validator_name=config.RDF_VALIDATOR_UI_NAME,
                           render_shacl_shapes=config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES)
