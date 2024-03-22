# Readme

The Project source code is seperated into a few core directories.
* `extendedLeaf` the directory for source code for the project.
* `extended_Examples` the directory used to access examples, this consists of:
  * `development_examples` the directory for examples used throughout the development process to test features.
  * `main_examples` the directory for examples used in the dissertation.
* `results` the directory which stores results from examples, NB. each set of results exists in timestamped directories.
* `dataSets` the directory that holds the csv data files needed for power sources.
* `test` the directory for python unit tests. 

## Build instructions

### Requirements

* Python versions between `3.9 and 3.10` inclusive
* Packages: listed in `requirements.txt` alongside pip for installation
* Tested on Windows 10

### GitLab
* The gitlab link to the full repository used for the project can be found [HERE](https://stgit.dcs.gla.ac.uk/2570809n/project-carbon-emissions-estimation-in-edge-cloud-computing-simulations)
### Build steps
Using a listed version of python, navigate to the `src` directory of the project.
Once inside the directory, either by using a new or existing python environment, issue the command: `pip install extended_LEAF-1.0.tar.gz` to install the dependencies onto the python environment.

## Running examples
If an IDE is being used, i.e. PyCharm:
* Simply right-click the example that is desired to be run and click `run`.
* Alternatively, enter the python console and issue the command `execfile('<Name_of_example_file.py>')`



