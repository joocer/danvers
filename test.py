from danvers import Danvers
import time

# instantiate with the location the data is stored
vers = Danvers(r'data')

# create the dataset if it doesn't exist already
dataset = 'marvel_movies'
if not dataset in vers.read_datasets():
    vers.create_dataset(dataset)

# add the first data file, should return verion 1
version = vers.create_data_file(dataset, r'test_data\movies_phase_1.csv')
print(version, vers.get_data_file(dataset))
time.sleep(1)

# adding the same data file should return version 1 again
version = vers.create_data_file(dataset, r'test_data\movies_phase_1.csv')
print(version, vers.get_data_file(dataset))
time.sleep(1)

# adding a new data file should return version 2
version = vers.create_data_file(dataset, r'test_data\movies_phase_1+2.csv')
print(version, vers.get_data_file(dataset))
time.sleep(1)

# adding another new data file should return version 3
version = vers.create_data_file(dataset, r'test_data\movies_phase_1+2+3.csv')
print(version, vers.get_data_file(dataset))
time.sleep(1)

# getting specific versions, the filenames should match the instances above
print(1, vers.get_data_file(dataset, 1))
print(2, vers.get_data_file(dataset, 2))
print(3, vers.get_data_file(dataset, 3))