<h1 align="center">
  <a href="https://github.com/D2KLab/PathwayGenerator" title="Pathway Generator">
    <img alt="Pathway Generator" src="image1.png" width="200px" height="100px" />
  </a>
  <br/>
  Pathway Generator
</h1>

<p align="center">
  Creation of an intelligent system capable of analyzing the requirements in order to access some services starting from its documentation and generate simplified steps to follow.
</p>

## Table of Contents
* [Table of Contents](#table-of-contents)
* [Preliminary Operations](#preliminary-operations)
    - [Setup Virtual Environment](#setup-virtual-environment)
    - [Pre trained Model](#pre-trained-model)
* [Pathway Generation pipe](#pathway-generation-pipe)
    - [Document conversion](#document-conversion)
    - [Named Entity Recognition](#named-entity-recognition)
    - [Entity Aggregation](#entity-aggregation)
    - [Pathway Generation](#pathway-generation)

## Preliminary Operations

This repo joins and extends the works present in Transer (https://github.com/D2KLab/Transner) and doc2txt(https://github.com/D2KLab/doc2txt): please see this two repositories in order to get started.

### Setup virtual environment

In order to install and use the external libraries used in this repository, we recommend the use of a virtual environment.
It can be created using the following command:

```bash
python3 -m venv env
```

You can now activate the virtual environment using the command:

```bash
source env/bin/activate
```

And use ```deactivate``` to disable it.

Once your virtual is activated, you can install the external libraries:

```python
pip3 install -r requirements.txt
```

### Pre trained Model

In order to use a pretrained model, download one of the models present at the following link: and insert it in the folder named ```transner```

## Pathway Generation pipe
test

### Document conversion
test

### Named Entity Recognition
test

### Entity Aggregation
test

### Pathway Generation
test
