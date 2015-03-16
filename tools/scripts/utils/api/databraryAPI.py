import urllib.request
import json
import requests
from data import api_config as conf
from data import api_paths as paths 

_BASE_URL = conf.access_points.dev
_USER = conf.creds.email
_PASS = conf.creds.dev_password

msg = {
    
    "error": "Something failed",
    "success": "It went fine, good job"

}

class Api:        

    def __init__(self, user=None, passw=None, sesh=None):

        self.user = _USER
        self.passw = _PASS
        self.sesh = requests.Session() 

    def _ParseJson(self, result:str) -> dict:
        return json.loads(result)

    def login(self):
        login_path = 'user/login' 
        login_url = _BASE_URL + login_path
        credentials = {"email": self.user, "password": self.passw}
        self.sesh.headers.update({"x-requested-with":"true"})
        return self.sesh.post(login_url, data=credentials)


    def profile(self):
        endpoint = _BASE_URL+'profile'
        return self.sesh.get(endpoint)


    def getVolume(self, v_id:int) -> dict:
        '''returns a json object for a volume that includes containers and records'''
        vol = str(v_id)
        endpoint = _BASE_URL+'volume/'+vol+"?containers&records"
        res = self.sesh.get(endpoint)
        if res.status_code == 200:
            return self._ParseJson(res.text)
        else:
            return msg['error'] + ", " + "status ruturned was: " + str(res.status_code)
        
        #get records - relies on getVolume
        #get containers - relies on getVolume
        #get assets
    

    def addTag(self, container:int, tag:str, segment:str="-", vote:str="true") -> str:
        container = str(container)
        endpoint = _BASE_URL + paths.DATABRARY_PATHS['add_tag'] % (tag) + "?container=" + container + "&segment=" + segment + "&vote=" + vote
        ret = self.sesh.post(endpoint)
        res = self._ParseJson(ret.text)

        if ret.status_code == 200:
            return msg['success'] + ": " + ret.text 
        else:
            return msg['error'] + ": " + ret.text
