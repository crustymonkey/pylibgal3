
__all__ = ['Album' , 'Image' , 'LocalImage' , 'RemoteImage' , 'LocalMovie' , 
    'RemoteMovie']

class Album(object):
    pass

class Image(object):
    pass

class LocalImage(object):
    pass

class RemoteImage(object):
    pass

class LocalMovie(LocalImage):
    pass

class RemoteMovie(RemoteImage):
    pass
