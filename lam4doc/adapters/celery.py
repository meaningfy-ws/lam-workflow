import logging
import traceback
from datetime import datetime
from pathlib import Path

from celery import Celery

from lam4doc.config import config
from lam4doc.services.db import create_persistent_folder
from lam4doc.services.report_handlers import add_report_metadata

logger = logging.getLogger(config.LAM_LOGGER)

celery_worker = Celery('lam4doc-tasks',
                       broker=config.LAM_REDIS_SERVICE,
                       backend=config.LAM_REDIS_SERVICE)
celery_worker.conf.update(result_extended=True)

CELERY_GENERATE_REPORT = 'generate_report'
CELERY_GENERATE_INDEXES = 'generate_indexes'
CELERY_GENERATE_ALL_FILES = 'generate_all_files'


def _handle_task_error(task_request_id, task_type, db_location, exception, context=None):
    """
    Helper function to handle task errors consistently.

    Args:
        task_request_id: The Celery task request ID
        task_type: The type of task (report, indexes, all)
        db_location: The database location folder
        exception: The caught exception
        context: Optional additional context info (dict)

    Returns:
        Path to the created error file
    """
    error_file_path = Path(db_location) / f"error_{task_type}_{task_request_id}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(error_file_path, 'w') as f:
        f.write(f"Error occurred at {timestamp}\n")
        f.write(f"Task: {task_type}\n")

        # Write additional context if provided
        if context:
            f.write("\nContext:\n")
            for key, value in context.items():
                f.write(f"{key}: {value}\n")

        f.write(f"\nError: {str(exception)}\n\n")
        f.write("Traceback:\n")
        f.write(traceback.format_exc())

    # Add error report metadata
    add_report_metadata(
        task_request_id,
        f"error_{task_type}",
        str(error_file_path),
        str(Path(db_location).parent)
    )

    logger.error(f'Error in {task_type} task: {str(exception)}. Error details saved at {error_file_path}')
    return error_file_path


@celery_worker.task(name=CELERY_GENERATE_REPORT, bind=True)
def async_generate_report(self, report_extension: str):
    """
    Task to generate LAM report

    NOTE: the order of the first arg is important for task cancellation, don't change its order
    :param report_extension: report extension (html, pdf)
    """
    from lam4doc.services.handlers import generate_lam_report

    db_location = create_persistent_folder(config.LAM_REPORTS_DB, self.request.id)

    try:
        report_file_info = generate_lam_report(db_location, report_extension)
        add_report_metadata(self.request.id, report_extension, str(report_file_info.location),
                            str(Path(db_location).parent))
        logger.debug(f'finish report generation at {report_file_info.location}')
        return str(report_file_info.location)
    except Exception as e:
        _handle_task_error(
            self.request.id,
            report_extension,
            db_location,
            e,
            context={"report_extension": report_extension}
        )
        raise


@celery_worker.task(name=CELERY_GENERATE_INDEXES, bind=True)
def async_generate_indexes(self):
    """
    Task to generate LAM indexes

    NOTE: the order of the first arg is important for task cancellation, don't change its order
    """
    from lam4doc.services.handlers import generate_indexes, zip_files

    db_location = create_persistent_folder(config.LAM_REPORTS_DB, self.request.id)

    try:
        index_files_info = generate_indexes(db_location)
        archive = zip_files(db_location, index_files_info, config.LAM_INDEXES_ZIP_NAME)

        add_report_metadata(self.request.id, "indexes", str(Path(db_location) / config.LAM_INDEXES_ZIP_NAME),
                            str(Path(db_location).parent))

        logger.debug(f'finish indexes generation at {archive}')
        return str(archive)
    except Exception as e:
        _handle_task_error(
            self.request.id,
            "indexes",
            db_location,
            e
        )
        raise


@celery_worker.task(name=CELERY_GENERATE_ALL_FILES, bind=True)
def async_generate_all_files(self):
    """
    Task to generate all LAM files

    NOTE: the order of the first arg is important for task cancellation, don't change its order
    """
    from lam4doc.services.handlers import generate_lam_report, generate_indexes, zip_files

    db_location = create_persistent_folder(config.LAM_REPORTS_DB, self.request.id)

    try:
        files_to_zip = []
        files_to_zip.append(generate_lam_report(db_location, 'pdf'))
        files_to_zip.append(generate_lam_report(db_location, 'html'))
        files_to_zip += generate_indexes(db_location)

        archive = zip_files(db_location, files_to_zip, config.LAM_ALL_ZIP_NAME)

        add_report_metadata(self.request.id, "all", str(Path(db_location) / config.LAM_ALL_ZIP_NAME),
                            str(Path(db_location).parent))

        logger.debug(f'finish all files generation at {archive}')
        return str(archive)
    except Exception as e:
        _handle_task_error(
            self.request.id,
            "all",
            db_location,
            e,
            context={"task": "Generate all files (PDF, HTML, indexes)"}
        )
        raise
