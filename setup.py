from setuptools import setup

setup(
    name = 'hyposchema',
    packages = ['hyposchema'], # this must be the same as the name above
    version = '0.2.3',
    description = 'Generate Hypothesis generators from a json schema definition',
    author = 'Mark Lakewood',
    author_email = 'underplank@gmail.com',
    url = 'https://github.com/mlakewood/hypo_schema', # use the URL to the github repo
    download_url = 'https://github.com/mlakewood/hypo_schema/tarball/0.1', # I'll explain this in a second
    keywords = ['testing', 'hypothesis', 'json_schema', 'generative'], # arbitrary keywords
    classifiers = [],
    install_requires=[
        'jsonschema',
        'hypothesis',
      ],
)
