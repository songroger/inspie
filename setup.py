import os
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as fh:
    readme = fh.read()

setup(
    name='inspie',
    version=__import__('inspie').__version__,
    description='inspie',
    long_description=readme,
    packages=find_packages(),
    install_requires=[
        "requests>=2.11.1",
        "requests-toolbelt>=0.7.0",
        "moviepy>=0.2.3.2"
    ],

    # extras_require=extras_require,
    package_data={
        'inspie': [
        ],
    },
)
