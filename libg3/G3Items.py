
__all__ = ['Album' , 'Image' , 'LocalImage' , 'RemoteImage' , 'LocalMovie' , 
    'RemoteMovie' , 'getItemFromResp']

from datetime import datetime
import json , weakref

class BaseRemote(object):
    _gal = None

    def __init__(self , respObj , weakGalObj):
        for k , v in respObj.items():
            setattr(self , k , v)
        self._gal = weakGalObj()
        self._membersSet = False

    def __getattribute__(self , name):
        if name == 'members' and not \
                object.__getattribute__(self , '_membersSet'):
            setattr(self , 'members' ,  
                object.__getattribute__(self , '_getMemberObjects')())
            setattr(self , '_membersSet' , True)
        d = object.__getattribute__(self , '__dict__')
        if name in d:
            return d[name]
        elif 'entity' in d and name in d['entity']:
            return d['entity'][name]
        raise AttributeError(name)

    def _getMemberObjects(self):
        """
        This returns the appropriate objects for each child of this object.
        The default "members" attribute only contains the URLs for the 
        children of this object.  This returns a list of the actual objects.
        """
        memObjs = []
        members = object.__getattribute__(self , 'members')
        gal = object.__getattribute__(self , '_gal')
        for m in members:
            resp = gal.getRespFromUrl(m)
            memObjs.append(getItemFromResp(resp , gal))
        return memObjs

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
    pass

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

def getItemFromResp(response , galObj):
    """
    Returns the appropriate item given the "addinfourl" response object from
    the urllib2 request

    response(addinfourl) : The response object from the urllib2 request
    galObj(Gallery3)     : The gallery object this is associated with
    """
    respObj = json.loads(response.read())
    try:
        t = respObj['entity']['type']
    except:
        raise G3InvalidRespError('Response contains no "entity type": %r' % 
            response)
    if t == 'album':
        return Album(respObj , weakref.ref(galObj))
    elif t == 'photo':
        return RemoteImage(respObj , weakref.ref(galObj))
    elif t == 'movie':
        return RemoteMovie(respObj , weakref.ref(galObj))
    else:
        raise G3UnknownTypeError('Unknown entity type: %s' % t)
