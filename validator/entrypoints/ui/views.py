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

from flask import render_template, flash, redirect, url_for, send_from_directory

from validator.config import config
from validator.entrypoints.ui import app
from validator.entrypoints.ui.api_wrapper import validate_file as api_validate_file, \
    validate_sparql_endpoint as api_validate_sparql_endpoint, \
    validate_sparql_endpoint_with_ap as api_validate_sparql_endpoint_with_ap, \
    validate_file_with_ap as api_validate_file_with_ap, get_active_tasks as api_get_active_tasks, \
    revoke_task as api_revoke_task, get_validations, get_report, delete_validation as api_delete_validation
from validator.entrypoints.ui.forms import SHACLShapesDataFileForm, ApplicationProfileDataFileForm, \
    SHACLShapesURLForm, ApplicationProfileURLForm
from validator.entrypoints.ui.helpers import get_error_message_from_response

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)


@app.route('/', methods=['GET'])
def index():
    """
    Home page containing the list of available validation reports.
    """
    logger.debug('request index view')
    validations, _ = get_validations()

    logger.debug('render index view')
    return render_template('index.html', validations=validations,
                           validator_name=config.RDF_VALIDATOR_UI_NAME)


@app.route('/validate/shapes/file', methods=['GET', 'POST'])
def validate_shapes_file():
    logger.debug('request validate shapes file view')

    form = SHACLShapesDataFileForm()

    if form.validate_on_submit():
        response, status = api_validate_file(
            data_file=form.data_file.data,
            schema_files=form.schema_files.data
        )

        if status != 200:
            exception_text = get_error_message_from_response(response)
            logger.exception(exception_text)
            flash(exception_text, 'error')
        else:
            flash('validation successfully started', 'success')
            logger.debug('render create diff view')

    logger.debug('render validate file clean view')
    return render_template('validate/file.html', form=form, title='Validate File',
                           validator_name=config.RDF_VALIDATOR_UI_NAME,
                           render_shacl_shapes=config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES)


@app.route('/validate/ap/file', methods=['GET', 'POST'])
def validate_file_with_ap():
    logger.debug('request validate file view')

    form = ApplicationProfileDataFileForm()

    if form.validate_on_submit():
        response, status = api_validate_file_with_ap(
            data_file=form.data_file.data,
            application_profile=form.application_profile.data
        )

        if status != 200:
            exception_text = get_error_message_from_response(response)
            logger.exception(exception_text)
            flash(exception_text, 'error')
        else:
            flash('validation successfully started', 'success')
            logger.debug('render create diff view')

    logger.debug('render validate file clean view')
    return render_template('validate/file_with_ap.html', form=form, title='Validate File with AP',
                           validator_name=config.RDF_VALIDATOR_UI_NAME,
                           render_shacl_shapes=config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES)


@app.route('/validate/shapes/url', methods=['GET', 'POST'])
def validate_sparql_endpoint():
    logger.debug('request validate sparql endpoint view')

    form = SHACLShapesURLForm()

    if form.validate_on_submit():
        response, status = api_validate_sparql_endpoint(
            sparql_endpoint_url=form.endpoint_url.data,
            schema_files=form.schema_files.data,
            graphs=form.graphs.data.split()
        )

        if status != 200:
            exception_text = get_error_message_from_response(response)
            logger.exception(exception_text)
            flash(exception_text, 'error')
        else:
            flash('validation successfully started', 'success')
            logger.debug('render create diff view')

    logger.debug('request validate sparql endpoint clean view')
    return render_template('validate/sparql_endpoint.html', form=form, title='Validate SPARQL Endpoint',
                           validator_name=config.RDF_VALIDATOR_UI_NAME,
                           render_shacl_shapes=config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES)


@app.route('/validate/ap/url', methods=['GET', 'POST'])
def validate_sparql_endpoint_with_ap():
    logger.debug('request validate sparql endpoint with ap view')

    form = ApplicationProfileURLForm()

    if form.validate_on_submit():
        response, status = api_validate_sparql_endpoint_with_ap(
            sparql_endpoint_url=form.endpoint_url.data,
            application_profile=form.application_profile.data,
            graphs=form.graphs.data.split()
        )

        if status != 200:
            exception_text = get_error_message_from_response(response)
            logger.exception(exception_text)
            flash(exception_text, 'error')
        else:
            flash('validation successfully started', 'success')
            logger.debug('render create diff view')

    logger.debug('request validate sparql endpoint clean view')
    return render_template('validate/sparql_endpoint_with_ap.html', form=form, title='Validate SPARQL Endpoint with AP',
                           validator_name=config.RDF_VALIDATOR_UI_NAME,
                           render_shacl_shapes=config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES)


@app.route('/validations/<validation_id>/<report_type>')
def download_report(validation_id: str, report_type: str):
    logger.debug(f'request validation report view for: {validation_id}')
    try:
        with tempfile.TemporaryDirectory() as temp_folder:
            report_content, _ = get_report(validation_id, report_type)
            file_name = f"validation-report.{report_type}"
            report = Path(temp_folder) / file_name
            report.write_bytes(report_content)
            logger.debug(f'render validation report view for: {validation_id}')
            return send_from_directory(Path(temp_folder), file_name, as_attachment=True)
    except Exception as e:
        logger.exception(str(e))

        flash(str(e), 'error')
        return redirect(url_for('index'))


@app.route('/validations/<validation_id>/')
def delete_validation(validation_id: str):
    logger.debug(f'request removal of validation report view for: {validation_id}')
    response, status = api_delete_validation(validation_id=validation_id)

    if status != 200:
        exception_text = get_error_message_from_response(response)
        logger.exception(exception_text)
        flash(exception_text, 'error')
    else:
        flash('validation successfully removed', 'success')

    return redirect(url_for('index'))


@app.route('/tasks')
def get_active_tasks():
    """
    Page containing the list of active tasks.
    """
    logger.debug('request active tasks view')
    tasks, _ = api_get_active_tasks()

    logger.debug(tasks)
    logger.debug('render active tasks view')
    return render_template('tasks/view_active_tasks.html', tasks=tasks, validator_name=config.RDF_VALIDATOR_UI_NAME)


@app.route('/revoke-task/<task_id>')
def revoke_task(task_id: str):
    """
    helper to revoke task from UI
    :param task_id: task to kill
    """
    logger.debug(f'request revoking for : {task_id}')
    message, status = api_revoke_task(task_id)
    if status == 200:
        flash(message, 'success')
    else:
        logger.exception(message)
        flash(message, 'error')

    return redirect(url_for('get_active_tasks'))
