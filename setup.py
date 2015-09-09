from setuptools import find_packages
from setuptools import setup

setup(
    name='partial_flake8',
    description='Tool for checking for flake8 in commits',
    url='https://github.com/asottile/reorder_python_imports',
    version='0.0.0',
    author='Trung Phan',
    author_email='trung.phan@studitemps.de',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    packages=find_packages('.', exclude=('tests*', 'testing*')),
    install_requires=[
        'flake8',
        'simplejson',
        'whatthepatch',
        'six',
    ],
    entry_points={
        'console_scripts': [
            'partial-flake8 = pre_commit_hooks.partial_flake8:main',
        ],
    },
)
