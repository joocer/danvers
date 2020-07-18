"""
Danvers is a simple file-based data versioning system.
"""

import warnings
import os
import json
import re
import datetime
import shutil

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


    def get_filename(self, source, version='latest'):
        source_config = self.get_source(source)
        if version == 'latest':
            version, version_dict = self._get_latest_version(source_config)
        filename = self._get_filename_from_version(source_config, version)
        filepath = os.path.join(self.location, source, filename)
        if not os.path.isfile(filepath):
            raise Exception("File '" + filename + " does not exist.")
        return filepath


    def put_source(self, source, description=''):
        config = { 
            "name": source,
            "description": description,
            "versions": []
        }
        path = os.path.join(self.location, source)
        os.makedirs(path)
        filepath = os.path.join(path, 'danvers.json')
        with open(filepath, 'w') as outfile:
            json.dump(config, outfile, ensure_ascii=False, indent=4)


    def put_data(self, source, file):
        """
        Test if the file is a new version, if not, return the matching version
        if it is, create a new version and return that.

        Put a copy of the file in the appropriate data directory.
        """
        config = self.get_source(source)
        file_hash = self._hash_file(file)
        try:
            version, latest_version = self._get_latest_version(config)
            if file_hash == latest_version['hash']:
                return version
            latest_version = version
        except:
            # we're here if there are not existing versions
            version = 0

        extension = os.path.splitext(file)[1]
        filename = file_hash[0:16] + extension
        file_path = os.path.join(self.location, source, filename)

        shutil.copyfile(file, file_path)

        item = {
            "filename": filename,
            "version": version + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "hash": file_hash
        }

        config['versions'].append(item)
        self._put_source_config(source, config)

        return version + 1


    def _get_latest_version(self, config):
        version = 0
        version_dict = {}
        for item in config['versions']:
            if item['version'] > version:
                version = item['version']
                version_dict = item
        if version == 0:
            raise Exception('No versions found')
        return version, version_dict


    def _get_filename_from_version(self, config, version):
        for item in config['versions']:
            if item['version'] == version:
                return item['filename']
        raise Exception('Version not found')


    def _hash_file(self, filename):
        # https://nitratine.net/blog/post/how-to-hash-files-in-python
        import hashlib
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha256()
        with open(filename, 'rb') as f:
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(BLOCK_SIZE)
        return file_hash.hexdigest()


    def _put_source_config(self, source, config):
        config_file = os.path.join(self.location, source, 'danvers.json')
        with open(config_file, 'w') as outfile:
            json.dump(config, outfile, ensure_ascii=False, indent=4)
