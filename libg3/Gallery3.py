
__all__ = ['Gallery3']

from Errors import G3Error
from Requests import *
from Response import *
from urllib import quote
import urllib2 , os

class Gallery3(object):
    """
    This is the main utility class that should be instantiated and used for all
    calls
    """
    def __init__(self , host , apiKey , g3Base='/gallery3' , port=80 , 
            ssl=False):
        """
        Initializes and sets up the gallery 3 object

        host(str)   : The hostname of the gallery site
        apiKey(str) : The api key to use for the connections
        g3Base(str) : The remote url path to your gallery 3 install
                      (default: /gallery3)
        port(int)   : The port number to connect to (default: 80)
        ssl(bool)   : If true, use SSL for the connection (default: 80)
        """
        self.host = host
        self.apiKey = apiKey
        self.port = int(port)
        self.ssl = ssl
        self.g3Base = g3Base.strip('/')
        self.protocol = ('http' , 'https')[ssl]
        self._rootUri = 'index.php/rest/item/1'
        self._opener = None
        self._buildOpener()

    def getRoot(self):
        url = self._buildUrl(self._rootUri)
        req = GetRequest(url , self.apiKey)
        resp = self._opener.open(req)
        return resp

    def _buildOpener(self):
        self._opener = urllib2.build_opener()
        if self.ssl:
            self._opener.add_handler(urllib2.HTTPSHandler())

    def _buildUrl(self , resource):
        url = '%s://%s:%d/%s/%s' % (self.protocol , self.host , self.port , 
            quote(self.g3Base) , quote(resource))
        return url
