MultiUN_Map
===========
To use the module, put this on top of your code

    MODULES_PATH = '''..\\modules\\multi_un_module.py'''
    import imp
    NF = imp.load_source('multi_un_module', MODULES_PATH)
    import multi_un_module as mun
