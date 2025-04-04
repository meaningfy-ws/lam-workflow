import pathlib
from typing import List

from validator.utils.file import dir_exists, list_folders_from_path, list_files_from_path, list_files_paths_from_path
from validator.config import config


class ApplicationProfileManager:
    """
    This class will get details about application profiles
    """

    def __init__(self, application_profile: str = None,
                 root_folder: pathlib.Path = pathlib.Path(config.RDF_VALIDATOR_APS_LOCATION)):
        self.root_folder = root_folder
        self.application_profile = application_profile

    def get_path_to_ap_folder(self) -> pathlib.Path:
        """
            Method to get the path to the chosen AP folder
            :return:  pathlib.Path
        """
        if not dir_exists(self.root_folder):
            raise FileNotFoundError(f"The root folder '{self.root_folder}' is not found.")
        return self.root_folder / self.application_profile

    def list_aps(self) -> List[str]:
        """
            Method to list the APs discovered in the root folder
            :return: List[APs]
        """
        if not dir_exists(self.root_folder):
            raise FileNotFoundError(f"The root folder '{self.root_folder}' is not found.")
        return list_folders_from_path(self.root_folder)

    def list_ap_files(self):
        """
            Method to list the files discovered in the chosen file folder
            :return: List[APs]
        """
        if not dir_exists(self.get_path_to_ap_folder()):
            raise LookupError(f"the AP named '{self.application_profile}' is not found.")
        return list_files_from_path(self.get_path_to_ap_folder())

    def list_ap_files_paths(self):
        """
            Method to list the file paths discovered in the chosen file folder
            :return: List[APs]
        """
        if not dir_exists(self.get_path_to_ap_folder()):
            raise LookupError(f"the AP named '{self.application_profile}' is not found.")
        return list_files_paths_from_path(self.get_path_to_ap_folder())
