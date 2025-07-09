from setuptools import setup, Extension

example_module = Extension[
    'example',
    sources=['testplugin.c']
]

setup(
    name="example",
    version="0.1",
    description = "Example module in C",
    ext_modules=[example_module],
)