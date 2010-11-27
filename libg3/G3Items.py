
__all__ = ['Album' , 'Image' , 'LocalImage' , 'RemoteImage' , 'LocalMovie' , 
    'RemoteMovie' , 'getItemFromResp']

import json , weakref

class BaseRemote(object):
    def __init__(self , respObj , galObj):
        for k , v in respObj.items():
            self.__dict__[k] = v
        self._gal = galObj

    def __getattr__(self , name):
        if name in self.entity:
            return self.entity[name]
        raise AttributeError(name)

    def getMemberObjects(self):


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
