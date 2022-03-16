# Pathway Generator 

This repository contains the implementation of the Pathway Generator. It is developed in the context of the [H2020 easyRights project](https://www.easyrights.eu/) and implements state-of-the-art NLP technonoliges to translate verbose and lengthy documents describing processes such as Asylum Seeking into a set of actionable, step-wise, instructions in a format that we call Pathway.

# Setup virtual environment

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

Enable doccano client
```bash
cd doccano_api_client
pip3 install -e ./
cd ..
```

Enable the library that is utilized to numerize sentences
```bash
cd sentence-transformers
pip3 install -e ./
cd ..
```

# Requirements
Doccano to store the output of the annotations and the pathway generation. Check api/rest.py to insert credentials.
