
__all__ = ['Album' , 'Image' , 'LocalImage' , 'RemoteImage' , 'LocalMovie' , 
    'RemoteMovie' , 'getItemFromResp']

from datetime import datetime
import json , weakref , types

class BaseRemote(object):
    _gal = None

    def __init__(self , respObj , weakGalObj , weakParent=None):
        self._setAttrItems(respObj.items())
        if 'entity' in respObj:
            self._setAttrItems(respObj['entity'].items())
        if weakParent is not None:
            self.parent = weakParent()
        self._gal = weakGalObj()

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

class Album(BaseRemote):
    def addImage(self , image , name='' , title='' , description=''):
        """
        Add a LocalImage object to the album

        image(LocalImage)   : The image to upload
        """
        if not isinstance(image , LocalImage):
            raise TypeError('%r is not of type LocalImage' % image)
        return self._gal.addImage(self , image , name , title , description)

    def addMovie(self , movie , name='' , title='' , description=''):
        """
        Adds a LocalMovie object to the album
        
        movie(LocalMovie)   : The movie to upload
        """
        return self.addImage(movie , name , title , description)

    def addAlbum(self , albumName , title):
        """
        Add a subalbum to this album

        albumName(str)  : The name of the new album
        title(str)      : The album title
        """
        return self._gal.addAlbum(self , albumName , title)

class Image(object):
    pass

class LocalImage(Image):
    pass

class RemoteImage(BaseRemote , Image):
    pass

class LocalMovie(LocalImage):
    pass

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
