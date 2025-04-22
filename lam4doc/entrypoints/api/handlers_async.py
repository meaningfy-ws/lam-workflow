import logging
import uuid
from pathlib import Path

from flask import send_file
from werkzeug.exceptions import InternalServerError, UnprocessableEntity, BadRequest, NotFound, NotAcceptable

from lam4doc.adapters.celery import async_generate_report, async_generate_indexes, async_generate_all_files
from lam4doc.services.db import create_persistent_folder

from lam4doc.services.tasks import flatten_active_tasks, retrieve_active_tasks, retrieve_task, kill_task
from lam4doc.services.report_handlers import get_available_reports, get_report, remove_report, remove_all_reports

from lam4doc.config import config, DEFAULT_REPORT_TYPE, REPORT_EXTENSIONS

logger = logging.getLogger(config.LAM_LOGGER)

def generate_lam_report_async(report_extension: str = DEFAULT_REPORT_TYPE) -> tuple:
    """
    API method for generating and requesting LAM report asynchronously.
    :param report_extension: format of report: html, pdf
    :return: task id
    """
    logger.debug('Start generate lam report async endpoint')

    if report_extension not in REPORT_EXTENSIONS:
        exception_text = 'Wrong report_extension format. Accepted formats: ' \
                         f'{", ".join([format for format in REPORT_EXTENSIONS])}'
        logger.exception(exception_text)
        raise UnprocessableEntity(exception_text)  # 422

    try:


        task = async_generate_report.delay(report_extension)

        logger.debug('finish generate lam report async endpoint')
        return {'task_id': task.id}, 200
    except Exception as e:
        logger.exception(str(e))
        raise InternalServerError(str(e))  # 500


def generate_indexes_async() -> tuple:
    """
    API method for generating and requesting the LAM indexes asynchronously.
    :return: task id
    """
    logger.info('start generate lam indexes async endpoint')
    try:
        task = async_generate_indexes.delay()

        logger.debug('finish generate lam indexes async endpoint')
        return {'task_id': task.id}, 200
    except Exception as e:
        logger.exception(str(e))
        raise InternalServerError(str(e))  # 500


def get_lam_files_async() -> tuple:
    """
    API method for generating and requesting all LAM files asynchronously.
    :return: task id
    """
    logger.info('start get lam files async endpoint')
    try:
        task = async_generate_all_files.delay()

        logger.debug('finish get lam files async endpoint')
        return {'task_id': task.id}, 200
    except Exception as e:
        logger.exception(str(e))
        raise InternalServerError(str(e))  # 500


def get_reports() -> tuple:
    """
    Get available reports with their metadata.
    :return: list of report details
    """
    logger.debug('start get reports endpoint')
    reports = get_available_reports(config.LAM_REPORTS_DB)
    return reports, 200


def get_task_status(task_id: str) -> tuple:
    """
    Get specified task status data
    :param task_id: Id of task to get status for
    :return: dict
    """
    task = retrieve_task(task_id)
    if task:
        return {
            "task_id": task.id,
            "task_status": task.status,
            "task_result": task.result
        }, 200
    raise NotFound('task not found')  # 404


def get_active_tasks() -> tuple:
    """
    Get all active celery tasks
    :return: dict of celery workers and their active tasks
    """
    try:
        tasks = flatten_active_tasks(retrieve_active_tasks())
    except AttributeError:
        return [], 200
    return tasks, 200


def download_report(report_id: str):
    """
    Download a generated report by ID
    :param report_id: report ID
    :return: report file
    """
    try:
        file_path, filename = get_report(report_id, config.LAM_REPORTS_DB)
        return send_file(path_or_file=file_path, download_name=filename, as_attachment=True)
    except FileNotFoundError as e:
        raise NotFound(str(e))  # 404


def delete_report(report_id: str) -> tuple:
    """
    Delete a report by ID
    :param report_id: report ID
    :return: confirmation message
    """
    removed = remove_report(report_id, config.LAM_REPORTS_DB)
    if removed:
        return {'message': f'Report with {report_id} successfully removed'}, 200
    else:
        raise NotFound(f'Report with {report_id} does not exist')


def delete_reports() -> tuple:
    """
    Delete all reports
    :return: confirmation message
    """
    remove_all_reports(config.LAM_REPORTS_DB)
    return {'message': 'Successfully removed all reports'}, 200


def stop_running_task(task_id: str) -> tuple:
    """
    Revoke a task
    :param task_id: Id of task to revoke
    :return: confirmation message
    """
    try:
        tasks = flatten_active_tasks(retrieve_active_tasks())
        task = next(task for task in tasks if task["id"] == task_id)
        kill_task(task, config.LAM_REPORTS_DB)
    except:
        raise NotAcceptable('task already finished executing or does not exist')  # 406

    return {'message': f'task {task_id} set for revoking.'}, 200