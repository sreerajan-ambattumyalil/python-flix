from setuptools import setup

setup(
    name="WhatFlix",
    version = "1.0",
    py_module=["run"],
    install_requires=[
        "Click"
    ],
    entry_points='''
        [console_scripts]
        run=run:cli
    '''
)