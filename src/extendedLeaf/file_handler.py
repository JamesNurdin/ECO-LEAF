import json
import os
import re

from src.extendedLeaf.power import PowerDomain
from datetime import datetime


class FileHandler:

    def __init__(self, power_domain: PowerDomain):
        self.power_domain = power_domain
        self.creation_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = self.create_results_dir()

    def create_results_dir(self) -> str:
        """ Creates a directory for the results. """
        results_dir = self.get_results_dir()
        dir_name = f"{self.creation_time}_results"
        absolute_path = os.path.join(results_dir, dir_name)
        if os.path.exists(absolute_path):
            raise FileExistsError(f"Error: directory {dir_name} exists")
        os.makedirs(absolute_path)
        return absolute_path

    def get_results_dir(self) -> str:
        """ Returns the filepath to the results' directory. """
        current_script_path = os.path.abspath(__file__)
        target_directory = "project-carbon-emissions-estimation-in-edge-cloud-computing-simulations"
        dir_path = current_script_path

        while not dir_path.endswith(target_directory):
            dir_path = os.path.dirname(dir_path)
        filepath = os.path.join(dir_path, "src", "results")
        return filepath

    def write_out_results(self, dir_path: str = None, filename: str = "output.json"):
        """ Allows user to write raw data to file, allows for a desired filepath and filename
            if either are absent the missing aspects are defaulted, """
        if not self.is_valid_filename(filename):
            filename = "output.json"

        if dir_path is None or not os.path.exists(dir_path):
            dir_path = self.results_dir

        filepath = os.path.join(dir_path, filename)

        # Convert dictionary to JSON format
        json_data = json.dumps(self.power_domain.captured_data, indent=2)

        # Write JSON data to a file
        with open(filepath, 'w') as json_file:
            json_file.write(json_data)
        return filepath, json_data

    def is_valid_filename(self, filename):
        pattern = re.compile(r'^[a-zA-Z0-9_-]+\.json$')
        return bool(pattern.match(filename))

