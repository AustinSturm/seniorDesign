import requests
import config

class HandlerBase():

    def __init__(self, username='', password='', deviceId=''):
        self.APIURL = config.getApiUrl()

        self.username = username
        self.password = password

        self.token = ""
        if username and password:
            self.token = self.getToken_post()

        self.userId = self.getUserDetails_get()[0]['id']
        self.deviceId = deviceId # need to set this somehow
        self.devicePK = self.createDevice_post()


    def get(self, relativePath=''):
        try:
            response = requests.get(self.APIURL + relativePath, headers={'Authorization': 'Token ' + self.token})
            print(response.json())
            return response.json()
        except:
            pass

    def post(self, relativePath='', data=''):
        try:
            response = requests.post(self.APIURL + relativePath, headers={'Authorization': 'Token ' + self.token}, data=data)
            print(response.json())
            return response.json()
        except:
            pass

    def delete(self, relativePath='', data=''):
        try:
            response = requests.delete(self.APIURL + relativePath, headers={'Authorization': 'Token ' + self.token}, data=data)
            print(response.json())
            return response
        except:
            pass

    # sets instance for the token
    def getToken_post(self):
        request = requests.post(self.APIURL + "/auth/login", data={'username':self.username, 'password':self.password})
        token = request.json()['token']
        return token

    def getUserDetails_get(self):
        response = self.get('/auth/user/')
        return response

    def getDevicePK_post(self):
        response = self.post('/devices/detail', {"deviceId":self.deviceId})
        return response['id']

    # Checks if it has been created already then creates -> returns devicePK
    def createDevice_post(self):
        devicePK = self.getDevicePK_post()
        if devicePK : return devicePK
        response = self.post('/devices/', {"deviceId":self.deviceId, "user":self.userId})
        return response['id']

    def streamRoute_post(self):
        response = self.post('/devices/stream', {'deviceId':self.deviceId})
        return response

    # takes the data as param, fron't enable, rear enable:true
    def streamEnables_post(self, data):
        response = self.post('devices/stream', {'deviceId':self.deviceId}.update(data))
        pass

    def getAlerts_post(self):
        response = self.post('/devices/alerts', {'deviceId':self.deviceId})
        return response

    # create new alert -> returns that alerts json object
    def createAlert_post(self, alertType, alertDetails):
        try:
            response = self.post('/devices/alert', {'device':self.devicePK, 'alertType':alertType, 'alertDetails':alertDetails})
        except Exception as e:
            print(e)
        return response

    def networkList_get(self):
        response = self.post('/devices/networkList', {'deviceId':self.deviceId})
        return response

    def getQueue_get(self):
        response = self.post('/devices/events', {'deviceId':self.deviceId})
        return response

    def delEvent_delete(self, uid):
        response = self.delete('/devices/event', {'deviceId':self.deviceId, 'uid':uid})
        return response

    def createStat_post(self, x, y, z):
        response = self.post('/devices/statistic', {'deviceId':self.deviceId,'x':x, 'y':y,'z':z})
        return response

    def clearStats_delete(self):
        response = self.delete('/devices/statistic', {'deviceId':self.deviceId})
        return response

    def createLoc_post(self, long, lat, alt):
        response = self.post('/devices/location', {'deviceId':self.deviceId, 'longitude':long, 'latitude':lat, 'altitude':alt})
        return response

    def clearLoc_delete(self):
        response = self.delete('/devices/location', {'deviceId':self.deviceId})
        return response
