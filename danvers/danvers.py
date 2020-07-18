import warnings
import os
import json
import re
import datetime
import shutil

class Danvers:
    """
    Danvers is a simple file-based data versioning system.
    """

    def __init__(self, location):
        self.location = location
        os.makedirs(location, exist_ok=True)


    def read_datasets(self, dataset_regex=''):
        if dataset_regex == '':
            dataset_regex = '.+'
        results = []
        for folder_name in os.listdir(self.location):
            if re.match(dataset_regex, folder_name):
                results.append(folder_name)
        return results


    def read_dataset(self, dataset):
        config_file = os.path.join(self.location, dataset, 'danvers.json')
        if os.path.isfile(config_file):
            with open(config_file) as json_file:
                return json.load(json_file)
        else:
            raise Exception("Data Set of '" + dataset + \
                "' does not exist or does not have valid danvers.json file.")


    def get_data_file(self, dataset, version='latest'):
        dataset_config = self.read_dataset(dataset)
        if version == 'latest':
            version = self._get_last_updated_version(dataset_config)
        filename = self._get_filename_from_version(dataset_config, version)
        filepath = os.path.join(self.location, dataset, filename)
        if not os.path.isfile(filepath):
            raise Exception("File '" + filename + " does not exist.")
        return filepath


    def create_dataset(self, dataset, description='', max_versions=-1):
        """
        Create a new dataset - warns if set already exists.

        Parameters:
            dataset: name of the dataset
            description: (optional) a long name for the dataset
            max_versions: (options) the number of versions to keep (-1 = infinite)

        Returns:
            Nothing
        """
        config = { 
            "set": dataset,
            "description": description,
            "max_versions": max_versions,
            "versions": []
        }
        path = os.path.join(self.location, dataset)
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, 'danvers.json')
        if os.path.exists(filepath):
            warnings.warn("Data set (" + dataset + ") already exists.", UserWarning)
        with open(filepath, 'w') as outfile:
            json.dump(config, outfile, ensure_ascii=False, indent=4)


    def create_data_file(self, dataset, file):
        """
        Test if the file is a new version, if not, return the matching version
        if it is, create a new version and return that.

        Put a copy of the file in the appropriate data directory.
        """
        config = self.read_dataset(dataset)
        file_hash = self._hash_file(file)

        version = self._get_version_with_matching_hash(config, file_hash)
        if version != 0:
            # TODO: update the config
            return version
        version = self._get_last_version(config)

        extension = os.path.splitext(file)[1]
        filename = file_hash[0:16] + extension
        file_path = os.path.join(self.location, dataset, filename)

        shutil.copyfile(file, file_path)

        item = {
            "filename": filename,
            "version": version + 1,
            "first_added": datetime.datetime.now().isoformat(),
            "last_added":datetime.datetime.now().isoformat(),
            "hash": file_hash
        }

        config['versions'].append(item)
        
        if (config['max_versions'] > 0) and (len(config['versions']) > config['max_versions']):
            pass
        # TODO:
        # if versions > number of versions
        #   get the oldest version
        #   delete the oldest version
        
        self._update_dataset_config(dataset, config)

        return version + 1


    def _get_last_updated_version(self, config):
        EPOCH = datetime.datetime(1970, 1, 1)
        last_added = EPOCH
        version = 0
        for item in config['versions']:
            if datetime.datetime.fromisoformat(item['last_added']) > last_added:
                last_added = datetime.datetime.fromisoformat(item['last_added'])
                version = item['version']
        return version


    def _get_last_version(self, config):
        version = 0
        for item in config['versions']:
            if item['version'] > version:
                version = item['version']
        return version


    def _get_first_updated_version(self, config):
        NOW = datetime.datetime.now()
        first_added = NOW
        version = 0
        for item in config['versions']:
            if datetime.datetime.fromisoformat(item['last_added']) < first_added:
                first_added = datetime.datetime.fromisoformat(item['last_added'])
                version = item['version']
        return version


    def _get_version_with_matching_hash(self, config, hash):
        for item in config['versions']:
            if item['hash'] == hash:
                return item['version']
        return 0   


    def _get_filename_from_version(self, config, version):
        for item in config['versions']:
            if item['version'] == version:
                return item['filename']
        return 0


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


    def _update_dataset_config(self, dataset, config):
        config_file = os.path.join(self.location, dataset, 'danvers.json')
        with open(config_file, 'w') as outfile:
            json.dump(config, outfile, ensure_ascii=False, indent=4)