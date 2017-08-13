"""
setup.py
"""
from setuptools import setup, find_packages


def load(filename):
    """
    utility requirements.txt loading
    """
    with open(filename) as input_file:
        return input_file.read().split('\n'),


setup(
    name='flume',
    version="0.5.0",
    author='Rodney Gomes',
    author_email='rodneygomes@gmail.com',
    url='',
    setup_requires=['pytest-runner==2.11.1'],
    install_requires=load('requirements.txt'),
    tests_require=load('test-requirements.txt'),
    test_suite='test.unit',
    keywords=[''],
    py_modules=['flume'],
    packages=find_packages(exclude=['test']),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'flume=flume.cli:main'
        ]
    },

    license='Apache 2.0 License',
    description='flume (pronounced: floom) is a stream processing framework',
    long_description='README: http://github.com/rlgomes/flume',
)
