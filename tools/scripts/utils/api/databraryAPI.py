import urllib.request
import json
import requests
from config import api_config as conf
import api_paths as paths 

_BASE_URL = conf.access_points.dev
_USER = conf.creds.email
_PASS = conf.creds.dev_password

msg = {
    "error": "Something failed",
    "success": "It went fine, good job"}

class Api:        

    def __init__(self, user=None, passw=None, sesh=None):

        self.user = _USER
        self.passw = _PASS
        self.sesh = requests.Session() 

    def _BuildEndpoint(self, api_path:str) -> str:
        return _BASE_URL + paths.DATABRARY_PATHS[api_path]

    def _HandleRequest(self, endpoint:str, method:str) -> dict:
        if method.lower() == "get":
            ret = self.sesh.get(endpoint)
        if method.lower() == "post":
            ret = self.sesh.post(endpoint)
        res = self._ParseJson(ret.text)
        if ret.status_code == 200:
            return res
        else: 
            return msg['error'] + ", " + "status ruturned was: " + str(res.status_code)

    def _ParseJson(self, result:str) -> dict:
        return json.loads(result)

    def login(self): 
        endpoint = self._BuildEndpoint('user_login')
        credentials = {"email": self.user, "password": self.passw}
        self.sesh.headers.update({"x-requested-with":"true"})
        return self.sesh.post(endpoint, data=credentials)

    def logout(self):
        endpoint = self._BuildEndpoint('user_logut')
        

    def getMyProfile(self):
        endpoint = self._BuildEndpoint('current_user')
        return self._HandleRequest(endpoint, "get")

    def getAllVolume(self, v_id:int) -> dict:
        '''returns a json object for a volume that includes containers and records'''
        vol = str(v_id)
        endpoint = self._BuildEndpoint("volume_data") % vol + "?containers&records"
        return self._HandleRequest(endpoint, "get")
        
    def getVolumeRecords(self, v_id:int) -> dict:
        return self.getAllVolume(v_id)['records']
        
    def getVolumeContainers(self, v_id:int) -> dict:
        return self.getAllVolume(v_id)['containers']

    def addTag(self, container:int, tag:str, segment:str="-", vote:str="true") -> str:
        container = str(container)
        endpoint = self._BuildEndpoint('add_tag') % (tag) + "?container=" + container + "&segment=" + segment + "&vote=" + vote
        ret = self.sesh.post(endpoint)
        res = self._ParseJson(ret.text)

        if ret.status_code == 200:
            return msg['success'] + ": " + ret.text 
        else:
            return msg['error'] + ": " + ret.text

    def getTagDetails(self, query:str) -> dict:
        endpoint = self._BuildEndpoint('get_tag') % (query) + "?containers"
        return self._HandleRequest(endpoint, "get")

    def getTopTags(self) -> dict:
        emdpoint = self._BuildEndpoint('get_top_tags')
        return self._HandleRequest(endpoint, "get")       

    def searchFunders(self, query:str) -> dict: 
        endpoint = self._BuildEndpoint('search_funders') % (query)
        return self._HandleRequest(endpoint, "get")

