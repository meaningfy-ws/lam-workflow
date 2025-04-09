import logging as logger

from celery.result import AsyncResult

from validator.adapters.celery import celery_worker
from validator.service_layer.report_handlers import remove_report


def flatten_active_tasks(tasks: dict) -> list:
    return tasks.get(list(tasks.keys())[0], [])


def retrieve_active_tasks(worker=None) -> dict:
    """
    Get all currently running tasks
    :param worker: which celery worker to get tasks from
    :return: active celery tasks
    """
    worker = worker if worker else celery_worker
    inspector = worker.control.inspect()

    return inspector.active()


def retrieve_task(task_id: str, worker=None) -> AsyncResult:
    """
    Get specific celery task
    :param task_id: task id to retrieve data from
    :param worker: which celery worker to get tasks from
    :return: task info
    """
    worker = worker if worker else celery_worker
    task = AsyncResult(task_id, app=worker)

    return task


def revoke_task(task_id: str, terminate: bool = False, worker=None):
    """
    Kill a thread
    :param task_id: task id to terminate
    :param terminate: whether to kill task even if it already started
    :param worker: which celery worker to get tasks from
    :return:
    """
    worker = worker if worker else celery_worker

    worker.control.revoke(task_id, terminate=terminate)


def kill_task(task: dict, db_location: str):
    """
    Kill a currently running task
    :param task: task to kill
    :param db_location: which db to be used for cleanup
    :return:
    """
    revoke_task(task['id'], True)
    logger.debug('cleanup validation create')

    cleanup_validation(validation_uid=task['args'][0], db_location=db_location)


def cleanup_validation(validation_uid: str, db_location: str):
    """
    undo all actions for validation

    :param validation_uid: validation id
    :param db_location: which db to be used for cleanup
    """
    logger.debug('request to revoke task received. initiating cleanup process.')
    remove_report(validation_uid, db_location)