
__all__ = ['Gallery3']

from Errors import G3Error
from Request import *
from Response import *
import urllib2

class Gallery3(object):
    """
    This is the main utility class that should be instantiated and used for all
    calls
    """
    def __init__(self , host , apiKey , port=80 , ssl=False , username=None ,
            passwd=None , httpRealm=None):
        """
        Initializes and sets up the gallery 3 object

        host(str) : The hostname of the gallery site
        apiKey(str) : The api key to use for the connections
        port(int) : The port number to connect to (default: 80)
        ssl(bool) : If true, use SSL for the connection (default: 80)
        """
        self.host = host
        self.apiKey = apiKey
        self.port = port
        self.ssl = ssl
        self._opener = self._buildOpener()

    def _buildOpener(self):
        self._opener = urllib2.build_opener()
        if ssl:
            self._opener.add_handler(urllib2.HTTPSHandler())

    def getRoot(self):

