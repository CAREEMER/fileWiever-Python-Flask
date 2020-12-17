from configparser import ConfigParser

def read(varName, groupName, cfgPath):
    config_object = ConfigParser()
    config_object.read(cfgPath)
    cfg = config_object[groupName]
    return cfg[varName]

def write(varName, groupName, cfgPath, content):
    config_object = ConfigParser()
    config_object.read(cfgPath)
    cfg = config_object[groupName]
    cfg[varName] = content
    with open(cfgPath, 'w') as conf:
        config_object.write(conf)