from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   name='danvers',
   version='1.0.0',
   description='Simple, file-based data version control',
   long_description=long_description,
   long_description_content_type="text/markdown",
   author='Joocer',
   author_email='justin.joyce@joocer.com',
   packages=find_packages(),
   url="https://github.com/joocer/danvers",
   install_requires=[]
)