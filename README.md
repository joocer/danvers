<img align="centre" alt="danvers" width="60" height="60" src="danvers.png" />

# danvers

Danvers is a simple file-based data versioning system.

This allows you to maintain versions of data files so you can ensure code and 
models run consistently when datasets may change.

The version is only updated if the new file is different to the most recent
version. This allows infrequently updated data sets to be more easily
maintained - if it's new, Danvers will keep a copy, if it hasn't changed,
it will ignore and keep its current version.

Danvers has no dependencies, just what comes with Python. 

See test.py for example of usage.