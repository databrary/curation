import urllib.request
import json
import requests
from config import api_config as conf
import api_paths as paths 
from urllib.parse import urlencode

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
    
    '''helper functions'''
    def _BuildEndpoint(self, api_path:str) -> dict:
        return _BASE_URL + paths.DATABRARY_PATHS[api_path]

    def _HandleRequest(self, endpoint:str, method:str) -> dict:
        if method.lower() == "get":
            ret = self.sesh.get(endpoint)
        if method.lower() == "post":
            ret = self.sesh.post(endpoint)    
        if ret.status_code == 200:
            res = self._ParseJson(ret.text)
            return res
        if ret.status_code == 404:
            return {"status": msg['error'], 
                    "status code":str(ret.status_code), 
                    "details": "Either the resource does not exist or you must be logged in"}
        else: 
            return {"status": msg['error'], 
                    "status code":str(ret.status_code), 
                    "details": ret.text}

    def _ParseJson(self, result:str) -> dict:
        return json.loads(result)

    def _ParseParams(self, **kwargs) -> dict: #maybe a little too hacky
        return kwargs

    def _AddParameters(self, params:dict) -> str:
        return urlencode(params)
    '''/helper functions'''
    
    def login(self): 
        endpoint = self._BuildEndpoint('user_login')
        credentials = {"email": self.user, "password": self.passw}
        self.sesh.headers.update({"x-requested-with":"true"})
        return self.sesh.post(endpoint, data=credentials)

    def logout(self):
        endpoint = self._BuildEndpoint('user_logout')
        return self._HandleRequest(endpoint, "post")

    def getActivityStream(self):
        endpoint = self._BuildEndpoint('activity_stream')
        return self._HandleRequest(endpoint, "get")

    def queryUsers(self, access:int="", query:str="") -> dict:
        '''would rather that this returns the default if access is not specified'''
        endpoint = self._BuildEndpoint('query_users')
        params = self._ParseParams(access=access, query=query)
        endpoint += "?" + self._AddParameters(params)
        return self._HandleRequest(endpoint, "get")

    def getUser(self, user_id:int) -> dict:
        endpoint = self._BuildEndpoint('get_party') % (user_id)
        return self._HandleRequest(endpoint, "get")

    def getMyProfile(self):
        endpoint = self._BuildEndpoint('current_user')
        return self._HandleRequest(endpoint, "get")

    def getAllVolumes(self, query:str="", party:int="") -> dict:
        endpoint = self._BuildEndpoint('all_volumes')
        params = self._ParseParams(query=query, party=party)
        endpoint += "?" + self._AddParameters(params)
        return self._HandleRequest(endpoint, "get")

    def getFullVolume(self, v_id:int) -> dict:
        '''returns a json object for a volume that includes containers and records'''
        vol = str(v_id)
        endpoint = self._BuildEndpoint("volume_data") % vol + "?containers&records"
        return self._HandleRequest(endpoint, "get")
        
    def getVolumeRecords(self, v_id:int) -> dict:
        return self.getAllVolume(v_id)['records']
        
    def getVolumeContainers(self, v_id:int) -> dict:
        return self.getAllVolume(v_id)['containers']

    def createVolume(self):
        '''create a volume on databrary'''
        pass

    def updateVolume(self):
        '''update an existing volume on databrary'''
        pass

    def getSession(self):
        pass

    def createSession(self):
        pass

    def updateSession(self):
        pass

    def addTag(self, container:int, tag:str, segment:str="-", vote:str="true") -> str:
        container = str(container)
        params = self._ParseParams(container=container, segment=segment, vote=vote)
        endpoint = self._BuildEndpoint('add_tag') % (tag) + "?" + self._AddParameters(params)
        return self._HandleRequest(endpoint, "post") # the response on this isn't really clear that it was successful

    def getTagDetails(self, query:str) -> dict:
        endpoint = self._BuildEndpoint('get_tag') % (query) + "?containers"
        return self._HandleRequest(endpoint, "get")

    def getTopTags(self) -> dict:
        emdpoint = self._BuildEndpoint('get_top_tags')
        return self._HandleRequest(endpoint, "get")       

    def searchFunders(self, query:str) -> dict: 
        endpoint = self._BuildEndpoint('search_funders') % (query)
        return self._HandleRequest(endpoint, "get")

    def updateFunder(self):
        '''update existing funder'''
        pass


