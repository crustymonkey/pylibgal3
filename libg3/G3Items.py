
__all__ = ['Album' , 'Image' , 'LocalImage' , 'RemoteImage' , 'LocalMovie' , 
    'RemoteMovie' , 'getItemFromResp']

from datetime import datetime
import json , weakref , types , os , mimetypes

class BaseRemote(object):
    _gal = None

    def __init__(self , respObj , weakGalObj , weakParent=None):
        self._setAttrItems(respObj.items())
        if 'entity' in respObj:
            self._setAttrItems(respObj['entity'].items())
        if weakParent is not None:
            self.parent = weakParent()
        self._gal = weakGalObj()
        self.fh = None

    def __getattr__(self , name):
        """
        A bit of magic to make the retrieval of member objects lazy
        """
        if name == 'members':
            self.members = self._getMemberObjects()
            return self.members
        if name == 'album_cover':
            self.album_cover = self._getAlbumCoverObject()
            return self.album_cover
        raise AttributeError(name)

    def _setAttrItems(self , d):
        for k , v in d:
            if k == 'entity':
                # Skip it
                continue
            if (type(v) in types.StringTypes and v.startswith('http') and 
                    'url' not in k) or k == 'members':
                setattr(self , '_%s' % k , v)
            else:
                setattr(self , k , v)

    def _getMemberObjects(self):
        """
        This returns the appropriate objects for each child of this object.
        The default "members" attribute only contains the URLs for the 
        children of this object.  This returns a list of the actual objects.
        """
        memObjs = []
        for m in self._members:
            resp = self._gal.getRespFromUrl(m)
            memObjs.append(getItemFromResp(resp , self._gal , self))
        return memObjs

    def _getAlbumCoverObject(self):
        """
        This returns the album cover image
        """
        resp = self._gal.getRespFromUrl(self._album_cover)
        return getItemFromResp(resp , self._gal , self)

    def getCrDT(self):
        """
        Returns a datetime object for the time this item was created
        """
        if hasattr(self , 'created'):
            return datetime.fromtimestamp(int(self.created))
        return None

    def getUpdDT(self):
        """
        Returns a datetime object for the time this item was last updated
        """
        if hasattr(self , 'updated'):
            return datetime.fromtimestamp(int(self.updated))
        return None

    def delete(self):
        """
        Deletes this

        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        return self._gal.deleteItem(self)

    def update(self , title=None , description=None):
        """
        Update either the title, the description or both
        
        title(str)                      : The new item title
        description(str)                : The new item description

        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        return self._gal.updateItem(self)

class Album(BaseRemote):
    def addImage(self , image , title='' , description='' , name=''):
        """
        Add a LocalImage object to the album

        image(LocalImage)       : The image to upload

        returns(RemoteImage)    : The RemoteImage object that was created
        """
        if not isinstance(image , LocalImage):
            raise TypeError('%r is not of type LocalImage' % image)
        return self._gal.addImage(self , image , title , description , name)

    def addMovie(self , movie , name='' , title='' , description=''):
        """
        Adds a LocalMovie object to the album
        
        movie(LocalMovie)       : The movie to upload

        returns(RemoteMovie)    : The RemoteMovie object that was created
        """
        return self._gal.addMovie(self , movie , title , description , name)

    def addAlbum(self , albumName , title):
        """
        Add a subalbum to this album

        albumName(str)  : The name of the new album
        title(str)      : The album title

        returns(Album)  : The Album object that was created
        """
        return self._gal.addAlbum(self , albumName , title)

    def setCover(self , image):
        """
        Sets the album cover to the RemoteImage

        image(RemoteImage)  : The image to set as the album cover
        
        returns(tuple(status , msg))    : Returns a tuple of a boolean status
                                          and a message if there is an error
        """
        return self._gal.setAlbumCover(self , image)

    def getAlbums(self):
        """
        Return a list of the sub-albums in this album

        returns(list[Album])  : A list of Album objects
        """
        return self._getByType('album')
    Albums = property(getAlbums)

    def getImages(self):
        """
        Return a list of the images in this album

        returns(list[RemoteImage])  : A list of RemoteImages
        """
        return self._getByType('photo')
    Images = property(getImages)

    def getMovies(self):
        """
        Return a list of the movies in this album

        returns(list[RemoteMovie])  : A list of RemoteMovie objects
        """
        return self._getByType('movie')
    Movies = property(getMovies)

    def _getByType(self , t):
        ret = []
        for m in self.members:
            if m.type == t:
                ret.append(m)
        return ret

class Image(object):
    contentType = ''

class LocalImage(Image):
    def __init__(self , path , replaceSpaces=True):
        if not os.path.isfile(path):
            raise IOError('%s is not a file' % path)
        self.path = path
        self.replaceSpaces = replaceSpaces
        self.Filename = os.path.basename(self.path)
        self.fh = None
        self.type = 'photo'

    def setContentType(self , ctype=None):
        if ctype is not None:
            self.contentType = ctype
        self.contentType = mimetypes.guess_type(self.getFileContents())[0] or \
            'application/octet-stream'
    def getContentType(self):
        if not self.contentType:
            self.setContentType()
        return self.contentType
    ContentType = property(getContentType , setContentType)

    def setFilename(self , name):
        self.filename = name
        if self.replaceSpaces:
            self.filename = self.filename.replace(' ' , '_')
    def getFilename(self):
        return self.filename
    Filename = property(getFilename , setFilename)

    def getFileContents(self):
        """
        Gets the entire contents of the file
        
        returns(str)    : File contents
        """
        if self.fh is None:
            self.fh = open(self.path , 'rb')
        self.fh.seek(0)
        return self.fh.read()

    def getUploadContent(self):
        """
        This will return a string containing the MIME headers and the actual
        binary content to be uploaded
        """
        ret = 'Content-Disposition: form-data; name="file"; '
        ret += 'filename="%s"\r\n' % self.filename
        ret += 'Content-Type: %s\r\n' % self.ContentType
        ret += 'Content-Transfer-Encoding: binary\r\n'
        ret += '\r\n'
        ret += self.getFileContents() + '\r\n'
        return ret

    def close(self):
        try:
            self.fh.close()
        except:
            pass

class RemoteImage(BaseRemote , Image):
    def read(self , length=None):
        if not self.fh:
            resp = self._gal.getRespFromUrl(self.file_url)
            self.fh = resp
        if length is None:
            return self.fh.read()
        return self.fh.read(int(length))

    def close(self):
        try:
            self.fh.close()
        except:
            pass

class LocalMovie(LocalImage):
    def __init__(self , path , replaceSpaces=True):
        LocalImage.__init__(self , path , replaceSpaces)
        self.type = 'movie'

class RemoteMovie(RemoteImage):
    pass

def getItemFromResp(response , galObj , parent=None):
    """
    Returns the appropriate item given the "addinfourl" response object from
    the urllib2 request

    response(addinfourl) : The response object from the urllib2 request
    galObj(Gallery3)     : The gallery object this is associated with
    parent(Album)        : The parent object for this item 
    """
    galObj = weakref.ref(galObj)
    if parent is not None:
        parent = weakref.ref(parent)
    respObj = json.loads(response.read())
    try:
        t = respObj['entity']['type']
    except:
        raise G3InvalidRespError('Response contains no "entity type": %r' % 
            response)
    if t == 'album':
        return Album(respObj , galObj , parent)
    elif t == 'photo':
        return RemoteImage(respObj , galObj , parent)
    elif t == 'movie':
        return RemoteMovie(respObj , galObj , parent)
    else:
        raise G3UnknownTypeError('Unknown entity type: %s' % t)
