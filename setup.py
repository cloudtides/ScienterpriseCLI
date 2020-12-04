from setuptools import setup

setup(
    name='scienterprise',
    version='0.1',
    py_modules=['scienterprise'],
    install_requires=[
        'Click', 'paramiko', 'docker'
    ],
    entry_points='''
        [console_scripts]
        scienterprise=scienterprise:cli
    ''',
)