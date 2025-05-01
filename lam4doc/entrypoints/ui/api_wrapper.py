#!/usr/bin/python3

# api_wrapper.py
# Date:  03/11/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com 

"""
Service to consume validator API.
"""
import logging

import requests
from requests import Timeout
from werkzeug.datastructures import FileStorage

from lam4doc.config import config

logger = logging.getLogger(config.LAM_LOGGER)


def get_lam_report(report_extension: str) -> tuple:
    """
    Method to connect to the lam api to get the report
    :type report_extension: report extension type
    :return: html report
    :rtype: file, int
    """
    logger.debug(f'start get report api call with {report_extension} format')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/generate-report',
                                params={'report_extension': report_extension},
                                timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))

    logger.debug('finish get report api call')
    return response.content, response.status_code


def get_indexes() -> tuple:
    """
    Method to connect to the lam api to get the indexes
    :return: zip file
    :rtype: file, int
    """
    logger.debug('start get indexes api call')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/generate-indexes', timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))

    logger.debug('finish get indexes api call')
    return response.content, response.status_code


def get_lam_files() -> tuple:
    """
    Method to connect to the lam api to get all LAM files
    :return: zip file
    :rtype: file, int
    """
    logger.debug('start get all lam files api call')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/lam-files', timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))

    logger.debug('finish get all lam files api call')
    return response.content, response.status_code


def upload_rdf(lam_properties_document: FileStorage, lam_classes_document: FileStorage,
               celex_classes_document: FileStorage, dataset_name: str) -> tuple:
    """
    Method to connect to the lam api to upload LAM RDF files
    :param lam_properties_document:
    :param lam_classes_document:
    :param celex_classes_document:
    :param dataset_name: name of the dataset for the files to be uploaded to
    :return:
    """
    data = {
        'dataset_name': dataset_name,
    }

    lam_properties_document = (lam_properties_document.filename, lam_properties_document.stream,
                               lam_properties_document.mimetype) if lam_properties_document else None
    lam_classes_document = (lam_classes_document.filename, lam_classes_document.stream,
                            lam_classes_document.mimetype) if lam_classes_document else None
    celex_classes_document = (celex_classes_document.filename, celex_classes_document.stream,
                              celex_classes_document.mimetype) if celex_classes_document else None

    files = {
        'lam_properties_document': lam_properties_document,
        'lam_classes_document': lam_classes_document,
        'celex_classes_document': celex_classes_document
    }

    response = requests.post(config.LAM_API_SERVICE + '/upload-rdf', data=data, files=files)
    return response.content, response.status_code


# New async API functions
def get_lam_report_async(report_extension: str) -> tuple:
    """
    Method to connect to the lam api to start async report generation
    :param report_extension: report extension type
    :return: task info, status code
    """
    logger.debug(f'start async get report api call with {report_extension} format')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/generate-report-async',
                                params={'report_extension': report_extension},
                                timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500

    logger.debug('finish async get report api call')
    return response.json(), response.status_code


def get_indexes_async() -> tuple:
    """
    Method to connect to the lam api to start async indexes generation
    :return: task info, status code
    """
    logger.debug('start async get indexes api call')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/generate-indexes-async',
                               timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500

    logger.debug('finish async get indexes api call')
    return response.json(), response.status_code


def get_lam_files_async() -> tuple:
    """
    Method to connect to the lam api to start async LAM files generation
    :return: task info, status code
    """
    logger.debug('start async get all lam files api call')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/lam-files-async',
                               timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500

    logger.debug('finish async get all lam files api call')
    return response.json(), response.status_code


def get_reports() -> tuple:
    """
    Method to connect to the lam api to get all available reports
    :return: reports list, status code
    """
    logger.debug('start get reports api call')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/reports',
                                timeout=config.LAM_DEFAULT_TIMEOUT)

        # Check if the request was successful before parsing JSON
        if response.status_code == 200:
            return response.json(), response.status_code
        else:
            # For non-200 responses, return an empty list and the status code
            logger.error(f"Error fetching reports: HTTP {response.status_code}")
            return [], response.status_code

    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500
    except requests.exceptions.JSONDecodeError as e:
        logger.exception(f"Invalid JSON response: {e}")
        return [], 500
    finally:
        logger.debug('finish get reports api call')


def get_task_status(task_id: str) -> tuple:
    """
    Method to connect to the lam api to get the status of a task
    :param task_id: ID of the task
    :return: task status, status code
    """
    logger.debug(f'start get task status api call for task {task_id}')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + f'/tasks/{task_id}',
                               timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500

    logger.debug('finish get task status api call')
    return response.json(), response.status_code


def get_active_tasks() -> tuple:
    """
    Method to connect to the lam api to get all active tasks
    :return: tasks list, status code
    """
    logger.debug('start get active tasks api call')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + '/tasks',
                                timeout=config.LAM_DEFAULT_TIMEOUT)

        # Check if the request was successful before parsing JSON
        if response.status_code == 200:
            return response.json(), response.status_code
        else:
            # For non-200 responses, return an empty list and the status code
            logger.error(f"Error fetching tasks: HTTP {response.status_code}")
            return [], response.status_code

    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500
    except requests.exceptions.JSONDecodeError as e:
        logger.exception(f"Invalid JSON response: {e}")
        return [], 500
    finally:
        logger.debug('finish get active tasks api call')


def download_report(report_id: str) -> tuple:
    """
    Method to connect to the lam api to download a specific report
    :param report_id: ID of the report
    :return: report content, status code
    """
    logger.debug(f'start download report api call for report {report_id}')
    try:
        response = requests.get(url=config.LAM_API_SERVICE + f'/reports/{report_id}',
                               timeout=config.LAM_DEFAULT_TIMEOUT,
                               stream=True)
    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500

    logger.debug('finish download report api call')
    return response.content, response.status_code, response.headers.get('Content-Disposition', '')


def delete_report(report_id: str) -> tuple:
    """
    Method to connect to the lam api to delete a specific report
    :param report_id: ID of the report
    :return: response content, status code
    """
    logger.debug(f'start delete report api call for report {report_id}')
    try:
        response = requests.delete(url=config.LAM_API_SERVICE + f'/reports/{report_id}',
                                 timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500

    logger.debug('finish delete report api call')
    return response.json(), response.status_code


def stop_running_task(task_id: str) -> tuple:
    """
    Method to connect to the lam api to stop a running task
    :param task_id: ID of the task
    :return: response content, status code
    """
    logger.debug(f'start stop task api call for task {task_id}')
    try:
        response = requests.post(url=config.LAM_API_SERVICE + f'/tasks/{task_id}/stop',
                                timeout=config.LAM_DEFAULT_TIMEOUT)
    except Timeout as exception:
        logger.exception(str(exception))
        return str(exception), 500

    logger.debug('finish stop task api call')
    return response.json(), response.status_code