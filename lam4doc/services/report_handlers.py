import logging
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from lam4doc.config import config

logger = logging.getLogger(config.LAM_LOGGER)


def get_report_metadata(db_location: str) -> Dict:
    """
    Get all available reports metadata
    :param db_location: which db to be used
    :return: report metadata
    """
    metadata_path = Path(db_location) / 'metadata.json'

    if not metadata_path.exists():
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_path, 'w') as f:
            json.dump({}, f)
        return {}

    with open(metadata_path, 'r') as f:
        return json.load(f)


def save_report_metadata(metadata: Dict, db_location: str):
    """
    Save report metadata
    :param metadata: metadata to save
    :param db_location: which db to be used
    """
    metadata_path = Path(db_location) / 'metadata.json'
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)


def add_report_metadata(uid: str, report_type: str, file_path: str, db_location: str):
    """
    Add report metadata
    :param uid: report id
    :param report_type: type of report (html, pdf, indexes, all)
    :param file_path: path to the generated file
    :param db_location: which db to be used
    """
    metadata = get_report_metadata(db_location)

    metadata[uid] = {
        'type': report_type,
        'file_path': file_path,
        'filename': Path(file_path).name,
        'finished_at': f'{datetime.now().isoformat()}',
    }

    save_report_metadata(metadata, db_location)


def get_available_reports(db_location: str) -> List[Dict]:
    """
    Get all available reports with their metadata
    :param db_location: which db to be used
    :return: list of available reports
    """
    metadata = get_report_metadata(db_location)

    return [
        {
            'uid': uid,
            'type': data['type'],
            'finished_at': data['finished_at']
        }
        for uid, data in metadata.items()
    ]


def get_report(report_uid: str, db_location: str) -> Tuple[str, str]:
    """
    Get a specific report file
    :param report_uid: report id
    :param db_location: which db to be used
    :return: file path and filename
    """
    metadata = get_report_metadata(db_location)

    if report_uid not in metadata:
        raise FileNotFoundError(f"Report with UID {report_uid} not found")

    report_data = metadata[report_uid]
    file_path = str(Path(db_location) / report_uid / report_data['filename']) #report_data['file_path']

    if not Path(file_path).exists():
        raise FileNotFoundError(f"Report file at {file_path} not found")

    return file_path, report_data['filename']


def remove_report(report_uid: str, db_location: str) -> bool:
    """
    Remove a specific report
    :param report_uid: report id
    :param db_location: which db to be used
    :return: True if removed, False otherwise
    """
    metadata = get_report_metadata(db_location)

    if report_uid not in metadata:
        return False

    report_data = metadata[report_uid]
    file_path = report_data['file_path']

    try:
        if Path(file_path).exists():
            os.remove(file_path)

        folder_path = Path(db_location) / report_uid
        if folder_path.exists() and folder_path.is_dir():
            shutil.rmtree(folder_path)
    except Exception as e:
        logger.error(f"Error removing report file: {e}")

    del metadata[report_uid]
    save_report_metadata(metadata, db_location)

    return True


def remove_all_reports(db_location: str):
    """
    Remove all reports
    :param db_location: which db to be used
    """
    metadata = get_report_metadata(db_location)

    for uid in list(metadata.keys()):
        remove_report(uid, db_location)