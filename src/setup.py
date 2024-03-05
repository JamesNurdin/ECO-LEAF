from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='extended_LEAF',
    version='1',
    packages=find_packages(),
    install_requires=[requirements],
    author="James Andrew Nurdin",
    url="https://stgit.dcs.gla.ac.uk/2570809n/project-carbon-emissions-estimation-in-edge-cloud-computing-simulations",
    license="",
    author_email="2570809n@student.gla.ac.uk",
    description="An extended version of the LEAF simulation package by Lauritz Thamsen and Philipp Wiesner to introduce power sources and carbon awareness."
)
