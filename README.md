MultiUN_Map
===========

check requirements.txt for required modules
Run the below command inside your virtualenv to install all requieremnts
    
    pip install -r requirements.txt

To use the module, put this on top of your code

    MODULES_PATH = '''..\\modules\\multi_un_module.py'''
    import imp
    NF = imp.load_source('multi_un_module', MODULES_PATH)
    import multi_un_module as mun


# Test Files
for testing, extract the zip files
* data/TOP_100.zip --> data\multiUN.en\un\xml\en\TOP_100
* data/TOP_1000.zip --> data\multiUN.en\un\xml\en\TOP_1000

*Note*: Make sure the extracted files are in .gitignore

# Running the App
There are two ways to explore the functionality of the main module:
## UI Flask App
Simple Flask App to faclitate search and processing of documents.

###for to run on the full corpus
    python multiun.py 

###for to run on sample corpus (PICK ONE)
    python multiun.py map_100.json
    python multiun.py map_1000.json


## IPython Notebook
An IPython notebook was created to replicat the main functionality of the user interface.
Open the **"moduules\Search the Corpus and Process.ipynb**" notebook
