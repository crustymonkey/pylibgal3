
__all__ = ['Gallery3']

from Requests import *
from G3Items import getItemFromResp
from urllib import quote
import urllib2 , os , json

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
        self.root = None
        self._rootUri = 'index.php/rest/item/1'
        self._opener = None
        self._buildOpener()

    def getRoot(self):
        """
        Returns the root item (album)
        """
        if self.root is None:
            resp = self.getRespFromUri(self._rootUri)
            self.root = getItemFromResp(resp , self)
        return self.root

    def getRespFromUrl(self , url):
        """
        This returns the response object given a full url rather than just a
        uri defining the location on the server

        url(str) : The url to the resource
        """
        req = GetRequest(url , self.apiKey)
        resp = self._opener.open(req)
        return resp

    def getRespFromUri(self , uri):
        """
        Performs the request for the given uri and returns the "addinfourl" 
        response

        uri(str) : The uri string defining the resource on the defined host
        """
        url = self._buildUrl(uri)
        return self.getRespFromUrl(url)

    def addAlbum(self , parent , albumName , title):
        """
        Adds an album to the given parent album

        parent(Album)       : The parent Album object
        albumName(str)      : The name of the album
        title(str)          : The album title
        """
        data = {
            'type': 'album' ,
            'name': albumName ,
            'title': title
        }
        req = PostRequest(parent.url , self.apiKey , data)
        resp = self._opener.open(req)
        newObjUrl = self._getUrlFromResp(resp)
        item = getItemFromResp(self.getRespFromUrl(newObjUrl) , self , parent)
        parent._members.append(newObjUrl)
        parent.members.append(item)
        return item

    def addImage(self , parent , image , name='' , title='' , description=''):
        # TODO: implement this
        pass

    def _buildOpener(self):
        cp = urllib2.HTTPCookieProcessor()
        self._opener = urllib2.build_opener(cp)
        if self.ssl:
            self._opener.add_handler(urllib2.HTTPSHandler())

    def _buildUrl(self , resource):
        url = '%s://%s:%d/%s/%s' % (self.protocol , self.host , self.port , 
            quote(self.g3Base) , quote(resource))
        return url

    def _getUrlFromResp(self , resp):
        d = json.loads(resp.read())
        return d['url']
