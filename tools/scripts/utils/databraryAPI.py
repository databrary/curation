import urllib.request
import json
import requests
from data import api_config as conf 

_BASE_URL = conf.access_points.dev
_USER = conf.creds.email
_PASS = conf.creds.dev_password

class Api:        

    def __init__(self, user=None, passw=None, sesh=None):

        self.user = _USER
        self.passw = _PASS
        self.sesh = requests.Session() 

    def login(self):
        login_path = 'user/login' 
        login_url = _BASE_URL + login_path
        credentials = {"email": self.user, "password": self.passw}
        self.sesh.headers.update({"x-requested-with":"true"})
        return self.sesh.post(login_url, data=credentials)


    def profile(self):
        endpoint = _BASE_URL+'profile'
        return self.sesh.get(endpoint)


    def getVolume(self, v_id):
        vol = str(v_id)
        endpoint = _BASE_URL+'volume/'+vol+"?containers&records"
        res = self.sesh.get(endpoint)
        return json.loads(res.text)
        
