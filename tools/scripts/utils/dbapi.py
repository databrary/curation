import requests
import logging

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
import re
import os

logger = logging.getLogger('logs')

class DatabraryApi:
    __base_api_url = 'https://nyu.databrary.org/api/'
    __base_url = 'https://nyu.databrary.org/'
    __session = None
    __instance = None

    @staticmethod
    def getInstance(username=None, password=None):
        if DatabraryApi.__instance is None:
            DatabraryApi(username, password)
        return DatabraryApi.__instance

    def __init__(self, username, password):
        if DatabraryApi.__instance is not None:
            raise Exception('This class is a singleton.')
        else:
            self.__username = username
            self.__password = password
            try:
                self.__session = self.__login(username, password)
            except AttributeError as e:
                logger.error(e)
                raise
            DatabraryApi.__instance = self

    def __login(self, username, password):
        """
        Login to Databrary
        :param username: a valid user name (email)
        :param password: Databrary password
        :return:
        """
        session = requests.Session()
        url = urljoin(self.__base_api_url, 'user/login')
        logger.debug('Login URL %s', url)
        credentials = {
            "email": username,
            "password": password
        }

        response = session.post(url=url, json=credentials)
        if response.status_code == 200:
            logger.info("User %s login successful.", username)
        else:
            raise AttributeError('Login failed, please check your username and password')

        return session

    def logout(self):
        """
        Disconnect from the Databrary session
        :return:
        """
        url = urljoin(self.__base_api_url, 'user/logout')
        logger.debug('Logout URL %s', url)
        response = self.__session.post(url=url)
        if response.status_code == 200:
            logger.info("User %s Disconnected.", self.__username)
            DatabraryApi.__instance = None
            del self.__session
        else:
            raise AttributeError('Login failed, please check your username and password')

    def get_csv(self, volume, target_dir):
        """
        Download a CSV file from a Databrary volume, read access to the volume is required.
        :param volume: Databrary volume id
        :param target_dir: CSV file directory target
        :return: Path to the CSV file
        """

        def get_filename_from_cd(cd):
            """
            Get filename from content-disposition
            """
            if not cd:
                return None
            fname = re.findall('filename="(.+)"', cd)
            if len(fname) == 0:
                return None
            return fname[0]

        url = urljoin(self.__base_url, 'volume/' + str(volume) + '/csv')
        logger.debug('CSV url %s', url)

        response = self.__session.get(url, allow_redirects=True)
        if response.status_code == 200:
            file_name = get_filename_from_cd(response.headers.get('content-disposition'))
            file_path = os.path.join(target_dir, file_name)
            open(file_path, 'wb').write(response.content)
            logger.info("CSV File %s downloaded from volume %d.", file_name, volume)
            return file_path
        else:
            raise AttributeError('Cannot download CSV file in volume %d', volume)

    def get_sessions(self, volume):
        """
        Get a list of containers(session) from a Databrary volume
        :param volume: Databrary volume id
        :return: a list of session ids in JSON format
        """
        url = urljoin(self.__base_api_url, 'volume/' + str(volume) + '?containers')

        logger.debug('Getting session URL %s', url)
        response = self.__session.get(url=url)
        if response.status_code == 200:
            logger.info("Found %d sessions.", len(response.json()['containers']))
            return response.json()['containers']
        else:
            raise AttributeError('Cannot retrieve sessions list from volume %d', volume)

    def get_session_assets(self, volume, session):
        """
        Get volume's asset list
        :param volume: Databrary volume id
        :param session: Databrary session id
        :return: a list of session ids in JSON format
        """
        payload = {'assets': 1}
        url = urljoin(self.__base_api_url, 'volume/' + str(volume) + '/slot/' + str(session))

        logger.debug('Getting volume assets URL %s', url)
        response = self.__session.get(url=url, params=payload)
        if response.status_code == 200:
            logger.info("Found %d assets in session %s.", len(response.json()['assets']), session)
            return response.json()['assets']
        else:
            raise AttributeError('Cannot retrieve asset list from session %d in volume %d', session, volume)
