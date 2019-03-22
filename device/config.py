import configparser

config = configparser.ConfigParser()
config.read('settings.cnf')

def createConfigTemplate():
    config['account'] = {'username':"", "password":"", "deviceId":""}
    config['connection'] = {'apiurl':"http://18.217.120.158:443", 'rtmprelay':"18.217.120.158"}

    with open('settings.cnf', "w") as config_file:
        config.write(config_file)
    config.read('settings.cnf')

def setAccountConfig(username, password):
    config.set("account", "username", username)
    config.set("account", "password", password)

    with open('settings.cnf', "w") as config_file:
        config.write(config_file)
    config.read('settings.cnf')

def setRouteConfig(apiurl, rtmprelay):
    config.set("connection", "apiurl", apiurl)
    config.set("connection", "rtmprelay", rtmprelay)
    config.read('settings.cnf')

def getUsername():
    return config.get("account", "username")

def getPassword():
    return config.get("account", "password")

# function to generate random deviceId
def setDeviceId():
    pass

def getDeviceId():
    return config.get("account", "deviceId")

def getApiUrl():
    return config.get("connection", "apiurl")

def getRtmpRelay():
    return config.get("connection", "apiurl")
