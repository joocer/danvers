import warnings
import os
import json
import re
import datetime
import shutil

class Danvers:
    """
    Danvers is a simple file-based data versioning system.
    
    Parameters
        location: the path to where datasets are kept
    """

    def __init__(self, location):
        self.location = location
        self.EPOCH = datetime.datetime(1970, 1, 1)
        self.STRATEGIES = ['FIFO', 'LUFO']
        os.makedirs(location, exist_ok=True)


    def read_datasets(self, search=''):
        """
        Returns a list of all of the known datasets.

        Parameters
            search: (optional) regex to filter dataset names by (default matches all)
        """
        if search == '':
            search = '.+'
        results = []
        for folder_name in os.listdir(self.location):
            if re.match(search, folder_name):
                results.append(folder_name)
        return results


    def get_data_file(self, dataset, version='latest'):
        """
        latest = the last new version to be added
        """
        dataset_config = self._read_config(dataset)
        if version == 'latest':
            versions = self._get_list_of_versions(dataset)
            versions = sorted(versions, key=lambda k: k['first_added'], reverse=True)
            version = versions[0]['version']
        self._update_config_value(dataset, version, 'last_read')
        filename = self._get_filename_from_version(dataset_config, version)
        if filename == None:
            raise Exception("Version does not exist.")
        filepath = os.path.join(self.location, dataset, filename)
        if not os.path.isfile(filepath):
            raise Exception("File '" + filename + " does not exist.")
        return filepath


    def create_dataset(self, dataset, description='', max_versions=-1, strategy='FIFO'):
        """
        Create a new dataset - warns if set already exists.

        Parameters:
            dataset: name of the dataset
            description: (optional) a long name for the dataset
            max_versions: (optional) the number of versions to keep (-1 = infinite)
            strategy: (optional) method to maintain max versions (default: FIFO)
                FIFO = First In, First Out
                LUFO = Last Used, First Out

        Returns:
            Nothing
        """
        if strategy not in self.STRATEGIES:
            strategy = 'FIFO'
        config = { 
            "set": dataset,
            "description": description,
            "max_versions": max_versions,
            "strategy": strategy,
            "versions": []
        }
        path = os.path.join(self.location, dataset)
        os.makedirs(path, exist_ok=True)
        self._write_config(dataset, config)


    def create_data_file(self, dataset, file):
        """
        Test if the file is a new version, if not, return the matching version
        if it is, create a new version and return that.

        Put a copy of the file in the appropriate data directory.
        """
        config = self._read_config(dataset)
        file_hash = self._hash_file(file)

        version = self._get_version_with_matching_hash(config, file_hash)
        if version != 0:
            self._update_config_value(dataset, version, "last_added")
            return version
        
        versions = self._get_list_of_versions(dataset)
        if len(versions) > 0:
            versions = sorted(versions, key=lambda k: k['version'], reverse=True)
            version = versions[0]['version']

        extension = os.path.splitext(file)[1]
        filename = file_hash[0:16] + extension
        file_path = os.path.join(self.location, dataset, filename)
        shutil.copyfile(file, file_path)
        item = {
            "filename": filename,
            "version": version + 1,
            "first_added": datetime.datetime.now().isoformat(),
            "last_added": datetime.datetime.now().isoformat(),
            "last_read": self.EPOCH.isoformat(),
            "hash": file_hash
        }
        config['versions'].append(item)
        self._write_config(dataset, config)
        self._trim_files(dataset)
        
        return version + 1


    def _get_list_of_versions(self, dataset):
        config = self._read_config(dataset)
        versions = []
        for item in config['versions']:
            version = {
                "filename": item["filename"],
                "version": item["version"],
                "first_added": datetime.datetime.fromisoformat(item["first_added"]),
                "last_added": datetime.datetime.fromisoformat(item["last_added"]),
                "last_read": datetime.datetime.fromisoformat(item["last_read"]),
            }
            versions.append(version)
        return versions

    
    def _get_version_with_matching_hash(self, config, hash):
        for item in config['versions']:
            if item['hash'] == hash:
                return item['version']
        return 0   


    def _get_filename_from_version(self, config, version):
        for item in config['versions']:
            if item['version'] == version:
                return item['filename']
        return None


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
    
    
    def _update_config_value(self, dataset, version, attribute):
        config = self._read_config(dataset)
        for item in config['versions']:
            if item['version'] == version:
                item[attribute] = datetime.datetime.now().isoformat()
        self._write_config(dataset, config)


    def _read_config(self, dataset):
        config_filepath = os.path.join(self.location, dataset, 'danvers.json')
        if os.path.isfile(config_filepath):
            with open(config_filepath) as json_file:
                return json.load(json_file)
        return None
        
        
    def _write_config(self, dataset, config):
        config_filepath = os.path.join(self.location, dataset, 'danvers.json')
        with open(config_filepath, 'w') as outfile:
            json.dump(config, outfile, ensure_ascii=False, indent=4)
            
            
    def _trim_files(self, dataset):
        """
        If the dataset has more than the number of versions it should maintain (max_versions)
        then work out the version to remove (FIFO - first in, or LUFO - last used) and remove
        the file and update the config
        """
        config = self._read_config(dataset)
        if (config['max_versions'] > 0) and (len(config['versions']) > config['max_versions']):
            versions = self._get_list_of_versions(dataset)
            if config.get('strategy') != 'LUFO':
                versions = sorted(versions, key=lambda k: k['first_added'], reverse=False)
            else:
                versions = sorted(versions, key=lambda k: k['last_read'], reverse=True)
            version_to_delete = versions[0]['version']
            new_set_of_versions = []
            for item in config['versions']:
                if item['version'] != version_to_delete:
                    new_set_of_versions.append(item)
                else:
                    filepath = os.path.join(self.location, dataset, item['filename'])
                    os.remove(filepath)
            config['versions'] = new_set_of_versions
            self._write_config(dataset, config)