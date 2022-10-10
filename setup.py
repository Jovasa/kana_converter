from setuptools import setup, find_packages

setup(
    name='kana_converter',
    version='0.4.0',
    license="BSD-2-Clause",
    package_dir={'kana_converter': 'src'},
    packages=["kana_converter"],
    package_data={
        "kana_converter": ["data/*.json"]
    },
    py_modules=["kana_converter"]
)
