from setuptools import setup, find_packages

setup(
    name='extended_LEAF',
    version='1.0',
    packages=find_packages(),
    install_requires=["numpy~=1.23.0",
                      "simpy~=4.1.1",
                      "setuptools~=63.2.0",
                      "networkx~=2.7.1",
                      "matplotlib~=3.5.1",
                      "pandas~=2.1.4",
                      "plotly~=5.18.0",
                      "kaleido~=0.1.0.post1"],
    author="James Andrew Nurdin",
    url="https://stgit.dcs.gla.ac.uk/2570809n/project-carbon-emissions-estimation-in-edge-cloud-computing-simulations",
    license="",
    author_email="2570809n@student.gla.ac.uk",
    description="An extended version of the LEAF simulation package by Lauritz Thamsen and Philipp Wiesner to introduce power sources and carbon awareness."
)
