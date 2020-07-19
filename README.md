<img align="centre" alt="danvers" width="60" height="60" src="danvers.png" />

# danvers: simple file-based data version control

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/joocer/danvers/blob/master/LICENSE)

**Danvers** is a Python data version management tool, which helps you to maintain 
and reference current and previous versions of data files. 

This means you can ensure code and models run consistently when they reference 
datasets that may change and that you can ensure you keep older copies of data
files used as part of decision making, so logic and code can be rerun.

New versions are only created if the new file is different to previous 
versions. This allows infrequently updated data sets to be easily maintained 
and versioned - if it's new, Danvers will keep a copy, if it hasn't changed,
it will ignore and keep its current version.

Danvers has no dependencies, just what comes with Python. 

## Features
Danvers is simple, rather than feature-rich, but here are some of the things 
it can do:

- Access previous versions of data files
- Maintain a fixed number of verions (or all versions)
- Different trimming strategies are available (first-in-first-out, 
last-used-first-out) 
- Automatic duplicate check for data files against all known versions
