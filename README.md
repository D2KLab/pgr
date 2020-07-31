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
* [Output files](#output-files)

## Preliminary Operations

This repo joins and extends the works present in Transer (https://github.com/D2KLab/Transner) and doc2txt (https://github.com/D2KLab/doc2txt): please see this two repositories in order to get started.

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

In order to use a pretrained model, download one of the models present at the following link: https://istitutoboella-my.sharepoint.com/:f:/g/personal/alberto_benincasa_linksfoundation_com/EtYto0b7K7NKlfjPdGRWJf0BXyz-m2GxT-FoeGIc8BTNGg?e=IwFbwd and insert it in the folder named ```transner```

## Pathway Generation pipe

Example of use: 

```bash
python3 usage.py --files Documentation/es/Asylum_and_Employment_Procedimiento_plazas.pdf
```

### Document conversion
The purpose of this module is to take a file and convert it into one that can be sent as input to the Entity Recognition Model to be able to annotate it.

Here, the file is firstly converted into the ```.txt``` format and it is subsequently cleaned of all the URLs present, each replaced by a symble ```[cont]``` where ```cont``` is an incremental counter; at the end of this operation, a new file is created, in which are mapped the pairs ```cont - URL```.
After that, the text is formatted in order to have a complete sentece (ended with a dot) for each line.

Finally, the text is saved in file with the same name of the original one with the extension ```.txt```.
In order to integrate with the next module, there is also a function to convert each line of the file into a string that is inserted into a Python List.

### Named Entity Recognition
This module take as input a list of strings, like

```python
strings_list = [
  "Mario Rossi è nato all'ospedale San Raffaele",
  "Marco e Luca sono andati a Magenta in aereo"                  
]
```
and returns as output a dict object containing the extracted entities, with the following format:

```python
{
  "results": [
    {
      "entities": [
        {
          "start_offset": 0,
          "end_offset": 11,
          "confidence": 0.99,
          "type": "PERSON",
          "value": "mario rossi"
        },
        {
          "start_offset": 21,
          "end_offset": 42,
          "confidence": 0.99,
          "type": "ORGANIZATION",
          "value": "ospedale San Raffaele"
        }
      ],
      "sentence": "Mario Rossi è nato all'ospedale San Raffaele"
    },
    {
      "entities": [
        {
          "start_offset": 0,
          "end_offset": 5,
          "confidence": 0.99,
          "type": "PERSON",
          "value": "marco"
        },
        {
          "start_offset": 8,
          "end_offset": 12,
          "confidence": 0.99,
          "type": "PERSON",
          "value": "luca"
        },
        {
          "start_offset": 27,
          "end_offset": 34,
          "confidence": 0.99,
          "type": "LOCATION",
          "value": "magenta"
        },
        {
          "start_offset": 29,
          "end_offset": 37,
          "confidence": 0.99,
          "type": "MISCELLANEOUS",
          "value": "in aereo"
        }
      ],
      "sentence": "Marco e Luca sono andati a Magenta in aereo"
    }
  ],
  "timestamp": 1581065432.7972977
}
```

### Entity Aggregation
The purpose of this module is to take as input the result of the previous module and then aggregate the dictionary into a single output.

```python
{
  "text" : "Mario Rossi è nato all'ospedale San Raffaele. Marco e Luca sono andati a Magenta in aereo",
  "entities": [
    "LOCATION": [
        {
          "start_offset": 73,
          "end_offset": 80,
          "confidence": 0.99,
          "value": "magenta"
        }
    ],
    "ORGANIZATION": [
        {
          "start_offset": 23,
          "end_offset": 44,
          "confidence": 0.99,
          "value": "ospedale San Raffaele"
        }
    ],
    "PERSON": [
        {
          "start_offset": 0,
          "end_offset": 11,
          "confidence": 0.99,
          "value": "mario rossi"
        },
        {
          "start_offset": 46,
          "end_offset": 51,
          "confidence": 0.99,
          "value": "marco"
        },
        {
          "start_offset": 54,
          "end_offset": 58,
          "confidence": 0.99,
          "value": "luca"
        }
    ],
    "MISCELLANEOUS": [
        {
          "start_offset": 82,
          "end_offset": 90,
          "confidence": 0.99,
          "value": "in aereo"
        }
    ]
  ]
}

```
### Pathway Generation
In this module, the entities are grouped as follows:

- **WHERE** groups entities of type ORGANIZATION, LOCATION
- **WHEN** groups entities of type TIME
- **HOW** groups entities of type MISCELLANEOUS

The output is formatted as follows:

```python
[
  {"step": "how", "entity": "in aereo"},
  {"step": "where", "entity": "ospedale San Raffaele"},
  {"step": "where", "entity": "magenta"},
  {"step": "when", "entity": ""}

]
```

NB: non abbiamo when perchè non abbiamo ancora inserito il tag TIME
## Output files

We have two output files
- ```doccano_annotated.json``` is the file we can import in the Doccano Sequence Labeling project type, in order to visualize the tagged entities
- ```doccano_pathway.jsonl``` is the file we can import in the Doccano Sequence to Sequence project type, in order to visualize the pathway text
