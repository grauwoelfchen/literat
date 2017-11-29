# pylint: disable=invalid-name
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, *('doc', 'DESCRIPTION.rst'))) as f:
    DESCRIPTION = f.read()
with open(os.path.join(here, 'CHANGELOG')) as f:
    CHANGELOG = f.read()

requires = [
    'Click',
    'Chameleon',
    'PyYAML',
]

development_requires = [
    'flake8',
    'flake8_docstrings',
    'pylint',
]

testing_requires = [
]

setup(
    name='literat',
    version='0.0.1',
    description='literat',
    long_description=DESCRIPTION + '\n\n' + CHANGELOG,
    classifiers=[
        "Programming Language :: Python",
    ],
    author='',
    author_email='',
    url='',
    keywords='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'development': development_requires,
        'testing': testing_requires,
    },
    install_requires=requires,
    message_extractors={'literat': [
        ('**.py', 'python', None),
    ]},
    entry_points="""\
    [console_scripts]
    literat = literat.command:cli
    """,
)
