
__all__ = ['Gallery3' , 'login']

from Requests import *
from Errors import G3RequestError
from G3Items import getItemFromResp , BaseRemote
from urllib import quote , urlencode
from uuid import uuid4
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
        resp = self._openReq(req)
        return resp

    def getRespFromUri(self , uri):
        """
        Performs the request for the given uri and returns the "addinfourl" 
        response

        uri(str) : The uri string defining the resource on the defined host
        """
        url = self._buildUrl(uri)
        return self.getRespFromUrl(url)

    def addAlbum(self , parent , albumName , title , description=''):
        """
        Adds an album to the given parent album

        parent(Album)       : The parent Album object
        albumName(str)      : The name of the album
        title(str)          : The album title
        description(str)    : The album description

        returns(Album)      : The Album object that was created
        """
        data = {
            'type': 'album' ,
            'name': albumName ,
            'title': title ,
            'description': description ,
        }
        req = PostRequest(parent.url , self.apiKey , data)
        resp = self._openReq(req)
        newObjUrl = self._getUrlFromResp(resp)
        item = getItemFromResp(self.getRespFromUrl(newObjUrl) , self , parent)
        parent._members.append(newObjUrl)
        parent.members.append(item)
        return item

    def addImage(self , parent , image , title='' , description='' , name=''):
        """
        Add a LocalImage to the parent album.

        parent(Album)           : The parent album to add the image to
        image(LocalImage)       : The local image to upload and add to the 
                                  parent
        title(str)              : The image title
        description(str)        : The image description
        name(str)               : The image file name

        returns(RemoteImage)    : The RemoteImage instance for the item
                                  uploaded
        """
        if name:
            image.Filename = name
        entity = {
            'name': image.filename ,
            'type': image.type ,
            'title': title ,
            'description': description ,
        }
        boundary = str(uuid4())
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % 
            boundary}
        # this is more complicated than adding an album.  We have to
        # construct the upload MIME headers, including build the string
        # data section
        data = '--%s\r\n' % boundary
        data += 'Content-Disposition: form-data; name="entity"\r\n'
        data += 'Content-Type: text/plain; ' \
            'charset=UTF-8\r\n'
        data += 'Content-Transfer-Encoding: 8bit\r\n'
        data += '\r\n'
        data += '%s\r\n' % json.dumps(entity , separators=(',' , ':'))
        data += '--%s\r\n' % boundary
        data += image.getUploadContent()
        data += '--%s--\r\n' % boundary
        req = PostRequest(parent.url , self.apiKey , data , headers)
        resp = self._openReq(req)
        newObjUrl = self._getUrlFromResp(resp)
        item = getItemFromResp(self.getRespFromUrl(newObjUrl) , self , parent)
        parent._members.append(newObjUrl)
        parent.members.append(item)
        return item

    def addMovie(self , parent , movie , title='' , description='' , name=''):
        """
        Add a LocalMovie to the parent album.

        parent(Album)           : The parent album to add the movie to
        image(LocalMovie)       : The local movie to upload and add to the 
                                  parent
        title(str)              : The movie title
        description(str)        : The movie description
        name(str)               : The movie file name

        returns(RemoteMovie)    : The RemoteMovie instance for the movie 
                                  uploaded
        """
        return self.addImage(parent , movie , title , description , name)

    def updateItem(self , item):
        """
        Updates a remote item's title and description

        item(BaseRemote)        : An item descended from BaseRemote

        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        try:
            self._isItemValid(item , BaseRemote)
        except Exception , e:
            return (False , e.message)
        data = {
            'title': item.title ,
            'description': item.description ,
        }
        req = PutRequest(item.url , self.apiKey , data)
        try:
            resp = self._openReq(req)
        except G3RequestError , e:
            return (False , e.message)
        return (True , '')

    def updateAlbum(self , album):
        """
        Update the title and description for an album.
        
        image(Album)                    : Updates the title and/or description 
                                          for the Album

        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        return self.updateItem(album)

    def updateImage(self , image):
        """
        Update the title and description for an image.
        
        image(RemoteImage)  : Updates the title and/or description for the
                              RemoteImage

        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        return self.updateItem(image)

    def updateMovie(self , movie):
        """
        Update the title and description for a movie.
        
        image(RemoteMovie)  : Updates the title and/or description for the
                              RemoteMovie

        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        return self.updateItem(movie)

    def deleteItem(self , item):
        """
        Deletes the given item.  Item must be descended from BaseRemote.

        item(BaseRemote)                : The item to delete

        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        try:
            self._isItemValid(item , BaseRemote)
        except Exception , e:
            return (False , e.message)
        req = DeleteRequest(item.url , self.apiKey)
        try:
            resp = self._openReq(req)
        except G3RequestError , e:
            return (False , e.message)
        return (True , '')

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

    def _openReq(self , req):
        try:
            resp = self._opener.open(req)
        except urllib2.HTTPError , e:
            errors = json.loads(e.read())['errors']
            raise G3RequestError(errors)
        return resp

    def _isItemValid(self , item , cls):
        if not isinstance(item , cls):
            raise TypeError('Items to be deleted must be descended from '
                '%s: %s' % (cls , type(item)))
        if not 'url' in item.__dict__:
            raise G3UnknownError('The object, %s, has no "url"' % item)

def login(host , username , passwd , g3Base='/gallery3' , port=80 , 
        ssl=False):
    """
    This will log you in and return a Gallery3 object on success, None
    otherwise

    host(str)       : The hostname of the gallery site
    username(str)   : The username to login with
    passwd(str)     : The password to login with
    g3Base(str)     : The remote url path to your gallery 3 install
                      (default: /gallery3)
    port(int)       : The port number to connect to (default: 80)
    ssl(bool)       : If true, use SSL for the connection (default: 80)
    """
    data = {
        'user': username ,
        'password': passwd ,
    }
    protocol = ('http' , 'https')[ssl]
    url = '%s://%s:%d/%s/index.php/rest' % (protocol , host , port , 
        quote(g3Base))
    req = PostRequest(url , None , urlencode(data))
    opener = urllib2.build_opener()
    if ssl:
        opener.add_handler(urllib2.HTTPSHandler())
    try:
        resp = opener.open(req)
    except urllib2.HTTPError , e:
        return None
    apiKey = resp.read().strip('\'"')
    return Gallery3(host , apiKey , g3Base , port , ssl)
