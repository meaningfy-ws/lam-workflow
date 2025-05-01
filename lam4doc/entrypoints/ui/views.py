#!/usr/bin/python3

import logging
import os
import tempfile
from json import loads

from flask import render_template, flash, redirect, url_for, send_file, request

from lam4doc.entrypoints.ui import app
from lam4doc.entrypoints.ui.api_wrapper import upload_rdf as api_upload_rdf, \
    get_lam_report_async as api_get_lam_report_async, get_indexes_async as api_get_indexes_async, \
    get_lam_files_async as api_get_lam_files_async, get_reports as api_get_reports, \
    get_task_status as api_get_task_status, get_active_tasks as api_get_active_tasks, \
    download_report as api_download_report, delete_report as api_delete_report, \
    stop_running_task as api_stop_running_task
from lam4doc.entrypoints.ui.forms import ReportTypeForm, UploadRDFFilesForm

logger = logging.getLogger(__file__)


def get_error_message_from_response(response):
    return f'Status: {loads(response).get("status")}. Title: {loads(response).get("title")}' \
           f' Detail: {loads(response).get("detail")}'


@app.route('/', methods=['GET'])
def index():
    logger.debug('request index view')
    return render_template(template_name_or_list='index.html',
                           title='LAM Workflow')


@app.route('/lam-report', methods=['GET', 'POST'])
def download_lam_report():
    form = ReportTypeForm()

    if form.validate_on_submit():
        # Use the async API call
        response, status = api_get_lam_report_async(form.report_extension.data)

        if status != 200:
            logging.exception(response)
            flash(f"Error starting report generation: {response}", 'error')
        else:
            # Extract task ID from the response and redirect to task status page
            task_id = response.get('task_id')
            if task_id:
                flash(f'Report generation task started. You can track its progress on this page.', 'success')
                return redirect(url_for('task_status', task_id=task_id))
            else:
                flash('Failed to start report generation task.', 'error')

    logger.debug('render LAM report clean view')
    return render_template('report.html', form=form, title='Get LAM report')


@app.route('/indexes-report', methods=['GET'])
def download_indexes():
    logger.debug('request LAM indexes view')

    # Use the async API call
    response, status = api_get_indexes_async()

    if status != 200:
        logging.exception(response)
        flash(f"Error starting indexes generation: {response}", 'error')
        return redirect(url_for('index'))

    # Extract task ID from the response and redirect to task status page
    task_id = response.get('task_id')
    if task_id:
        flash(f'Indexes generation task started. You can track its progress on this page or in Tasks & Reports page.',
              'success')
        return redirect(url_for('task_status', task_id=task_id))
    else:
        flash('Failed to start indexes generation task.', 'error')
        return redirect(url_for('index'))


@app.route('/lam-files', methods=['GET'])
def download_lam_files():
    logger.debug('request all LAM files view')

    # Use the async API call
    response, status = api_get_lam_files_async()

    if status != 200:
        logging.exception(response)
        flash(f"Error starting LAM files generation: {response}", 'error')
        return redirect(url_for('index'))

    # Extract task ID from the response and redirect to task status page
    task_id = response.get('task_id')
    if task_id:
        flash(f'LAM files generation task started. You can track its progress on this page or in Tasks & Reports page.',
              'success')
        return redirect(url_for('task_status', task_id=task_id))
    else:
        flash('Failed to start LAM files generation task.', 'error')
        return redirect(url_for('index'))


@app.route('/upload-rdf', methods=['GET', 'POST'])
def upload_rdf():
    logging.info('request upload RDFs view')

    form = UploadRDFFilesForm()

    if form.validate_on_submit():
        response, status = api_upload_rdf(
            dataset_name=form.dataset_name.data,
            lam_properties_document=form.lam_properties_document.data,
            lam_classes_document=form.lam_classes_document.data,
            celex_classes_document=form.celex_classes_document.data
        )
        if status != 200:
            logging.info(response)
            flash(response, 'error')
        else:
            flash('Files upload successful', 'success')
            form = UploadRDFFilesForm()
            return render_template('upload_rdf.html', form=form, title='Upload RDF Files')

    logging.debug('upload RDFs clean view')
    return render_template('upload_rdf.html', form=form, title='Upload RDF Files')


@app.route('/tasks', methods=['GET'])
def tasks():
    """View all tasks and reports"""
    logger.debug('request tasks view')

    # Get active tasks and reports
    tasks_response, tasks_status = api_get_active_tasks()
    reports_response, reports_status = api_get_reports()

    tasks = []
    reports = []

    if tasks_status == 200:
        tasks = tasks_response
    else:
        flash(f'Error retrieving tasks: {tasks_response}', 'error')

    if reports_status == 200:
        reports = reports_response
    else:
        flash(f'Error retrieving reports: {reports_response}', 'error')

    # Sort the list by created_at
    sorted_reports = sorted(
        reports,
        key=lambda x: x['finished_at'],
        reverse=True  # newest first
    )


    return render_template(template_name_or_list='tasks.html',
                           title='LAM Workflow',
                           tasks=tasks,
                           reports=sorted_reports)


@app.route('/task/<task_id>', methods=['GET'])
def task_status(task_id):
    """View status of a specific task"""
    logger.debug(f'request task status view for task {task_id}')

    response, status = api_get_task_status(task_id)

    if status != 200:
        flash(f'Error retrieving task: {response}', 'error')
        return redirect(url_for('tasks'))

    return render_template('task_status.html', title=f'Task {task_id}', task=response)


@app.route('/download-report/<report_id>', methods=['GET'])
def download_report(report_id):
    """Download a specific report"""
    logger.debug(f'request download report for report {report_id}')

    try:
        response, status, content_disposition = api_download_report(report_id)

        if status != 200:
            flash(f'Error downloading report: {response}', 'error')
            return redirect(url_for('tasks'))

        # Extract filename from Content-Disposition header
        filename = "report.zip"
        if content_disposition:
            # Parse Content-Disposition header to extract filename
            parts = content_disposition.split(';')
            for part in parts:
                part = part.strip()
                if part.startswith('filename='):
                    filename = part[9:].strip('"')

        # Save the file to a temporary location and serve it
        with tempfile.TemporaryDirectory() as temp_folder:
            file_path = os.path.join(temp_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(response)
            return send_file(file_path, as_attachment=True, download_name=filename)

    except Exception as e:
        logger.exception(str(e))
        flash(str(e), 'error')
        return redirect(url_for('tasks'))


@app.route('/delete-report/<report_id>', methods=['POST'])
def delete_report(report_id):
    """Delete a specific report"""
    logger.debug(f'request delete report for report {report_id}')

    response, status = api_delete_report(report_id)

    if status != 200:
        flash(f'Error deleting report: {response}', 'error')
    else:
        flash('Report deleted successfully', 'success')

    # Redirect back to the page that called this route
    return redirect(request.referrer or url_for('tasks'))


@app.route('/stop-task/<task_id>', methods=['POST'])
def stop_task(task_id):
    """Stop a running task"""
    logger.debug(f'request stop task for task {task_id}')

    response, status = api_stop_running_task(task_id)

    if status != 200:
        flash(f'Error stopping task: {response}', 'error')
    else:
        flash('Task stopped successfully', 'success')

    # Redirect back to the page that called this route
    return redirect(request.referrer or url_for('tasks'))
