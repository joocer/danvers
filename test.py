from danvers import Danvers

vers = Danvers(r'data')

dataset = 'marvel_movies'
if not dataset in vers.get_sources():
    vers.put_source(dataset)

version = vers.put_data(dataset, r'test_data\movies_phase_1.csv')
print(version, vers.get_filename(dataset))
version = vers.put_data(dataset, r'test_data\movies_phase_1.csv')
print(version, vers.get_filename(dataset))
version = vers.put_data(dataset, r'test_data\movies_phase_1+2.csv')
print(version, vers.get_filename(dataset))
version = vers.put_data(dataset, r'test_data\movies_phase_1+2+3.csv')
print(version, vers.get_filename(dataset))
print(1, vers.get_filename(dataset, 1))
print(2, vers.get_filename(dataset, 2))
print(3, vers.get_filename(dataset, 3))