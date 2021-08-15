from setuptools import setup, find_packages

setup(
    name='kana_converter',
    version='0.2.0',
    license="BSD-2-Clause",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data = {
        "data": ["*.json"]
    }
)
