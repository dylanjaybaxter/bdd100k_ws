from setuptools import setup, find_packages

setup(
    name='image_streamer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'flask',
        'opencv-python',
    ],
)
