from setuptools import setup, Extension

setup(
    name="testplugin1",
    version="0.1",
    ext_modules=[
        Extension("testplugin1", sources=["testplugin.c"])
    ]
)