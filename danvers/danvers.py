"""
Danvers is a simple file-based data versioning system.
"""

import warnings
import os
import json
import re
import datetime

class Danvers:

    def __init__(self, location):
        self.location = location

    def get_sources(self, source_regex=''):
        if source_regex == '':
            source_regex = '.+'
        results = []
        for folder_name in os.listdir(self.location):
            if re.match(source_regex, folder_name):
                results.append(folder_name)
        return results

    def get_source(self, source):
        config_file = os.path.join(self.location, source, 'danvers.json')
        if os.path.isfile(config_file):
            with open(config_file) as json_file:
                return json.load(json_file)
        else:
            raise Exception("Source of '" + source + \
                "' does not exist or does not have valid danvers.json file.")

    def get_data(self, source, version='latest'):
        source_config = self.get_source(source)
        if version == 'latest':
            version = self._get_latest_version(source_config)
        filename = self._get_filename_from_version(source_config, version)
        """
        TODO: if the file is older than the update frequency, raise a warning
        TODO: if the file doesn't exist, raise a warning
        """
        return filename

    def put_source(self, a):
        """
        expected update frequency location
        """
        pass

    def put_data(self, source, data):
        import difflib
        """
        get the latest version
        compare hashes
        calculate a ratio difference
        """
        pass

    def _get_latest_version(self, config):
        pass

    def _get_filename_from_version(self, config, version):
        pass