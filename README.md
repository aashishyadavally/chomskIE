# chomskIE : NLP Pipeline for Relation Extraction

## Project Description
A substantial amount of valuable knowledge is recorded in the form of unstructured text data, such as news, emails, journal articles, etc. The task of identifying semantic relations among the text entities is referred to as *relation  extraction*. The goal of this project was to build a system to extract information templates of the following forms:

* **BORN** (Person/Organization, Date, Location)
* **ACQUIRE** (Organization, Organization, Date)
* **PART_OF**

   * PART_OF (Organization, Organization)

   * PART_OF (Location, Location)

To build this system, we were provided with 30 text files containing Wikipedia articles that are split as follows:
* 10 articles related to _Organizations_
* 10 articles related to _Persons_
* 10 articles related to _Locations_

### Architecture
The general architecture of the information extraction pipeline is as follows:

<p align="center">
  <img width="690" height="400" src="https://github.com/aashishyadavally/chomskIE/blob/main/assets/images/architecture.png">
</p>

For more details about the intricacies of the approach and general implementation details, read [this](https://github.com/aashishyadavally/chomskIE/blob/main/assets/report.pdf).

### Extracted Relations
<pre>
1. <b>BORN</b>

  * Abraham Lincoln was born on February 12, 1809, as the second child of Thomas and Nancy Hanks Lincoln, 
    in a one-room log cabin on Sinking Spring Farm near Hodgenville, Kentucky.
      <i>Argument-1</i>: Abraham Lincoln
      <i>Argument-2</i>: February 12, 1809
      <i>Argument-3</i>: Hodgenville

  * In May 2002, Musk founded SpaceX, an aerospace manufacturer and spacetransport services company, of
    which he is CEO and lead designer.
      <i>Argument-1</i>: SpaceX
      <i>Argument-2</i>: May 2002.  

2. <b>ACQUIRE</b>

  * Compaq acquired Zip2 for US$307 million in cash and US$34 million instock options in February 1999.
      <i>Argument-1</i>: Compaq
      <i>Argument-2</i>: Zip2
      <i>Argument-3</i>: February 1999
  
  * In 2015, Tesla acquired Riviera Tool & Die (with 100 employees inMichigan), one of its suppliers of
    stamping items.
      <i>Argument-1</i>: Tesla
      <i>Argument-2</i>: Riviera Tool & Die
      <i>Argument-3</i>: 2015
  
3.  <b>PART_OF</b>
  
  * They met in Springfield, Illinois in December 1839 and were engaged a year later.
      <i>Argument-1</i>: Springfield
      <i>Argument-2</i>: Illinois
  
  * The Mahatma Gandhi District in Houston, Texas, United States, an ethnic Indian enclave, is officially
    named after Gandhi.
      <i>Argument-1</i>: Houston
      <i>Argument-2</i>: Texas
</pre>

## Getting Started
This section describes the preqrequisites, and contains instructions, to get the project up and running.

### Setup
This project can easily be set up with all the prerequisite packages by following these instructions:
  1. Install [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) using the `conda_install.sh` file, with the command: `$ bash conda_install.sh`
  2. Create a conda environment from the included `environment.yml` file using the following command:
     
     `$ conda env create -f environment.yml`
  3. Activate the environment
     
     `$ conda activate chomskIE`
  4. To install the package with setuptools extras, use the following command in the top-level directory containing the `setup.py` file:
     
     `$ pip install .`

### Usage
The user can get a description of the options by using the command: 

`> python __main__.py --help`

To run the relation extraction pipeline on a batch of documents:

`> python __main__.py --input_path <path-to-input-dir> --output_path <path-to-output-dir>`

To run the relation extraction pipeline on a single document:

`> python __main__.py --input_path <path-to-input-dir> --output_path <path-to-output-dir> --transform`

### Built With
1. python >= 3.7
2. spaCy
3. textaCy == 0.11.0


## Contributing Guidelines
There are no specific guidelines for contributing, apart from a few general guidelines we tried to follow, such as:
* Code should follow PEP8 standards as closely as possible
* We use [Google-Style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) to document the Python modules in this project.

If you see something that could be improved, send a pull request! 
We are always happy to look at improvements, to ensure that `chomskIE`, as a project, is the best version of itself. 

If you think something should be done differently (or is just-plain-broken), please create an issue.

## License
See the [LICENSE](https://github.com/aashishyadavally/chomskIE/blob/master/LICENSE) file for more details.
