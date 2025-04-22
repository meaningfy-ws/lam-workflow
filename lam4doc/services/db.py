import logging
from pathlib import Path
from uuid import uuid4

from lam4doc.config import config

logger = logging.getLogger(config.LAM_LOGGER)


def create_persistent_folder(base_path: str, uid: str = None) -> str:
    """
    Create a persistent folder for report storage
    :param base_path: Base directory for reports
    :param uid: Optional unique identifier for the folder
    :return: Path to the persistent folder
    """
    import os
    from pathlib import Path
    import uuid

    folder_id = uid if uid else str(uuid.uuid4())
    folder_path = Path(base_path) / folder_id
    folder_path.mkdir(parents=True, exist_ok=True)

    return str(folder_path)