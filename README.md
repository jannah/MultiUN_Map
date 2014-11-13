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
