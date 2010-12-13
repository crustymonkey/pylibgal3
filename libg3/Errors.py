
__all__ = ['G3Error' , 'G3RequestError' , 'G3InvalidRespError' , 
    'G3UnknownTypeError' , 'G3AuthError' , 'G3UnknownError']

class G3Error(Exception):
    pass

class G3RequestError(G3Error):
    def __init__(self , errDict):
        self.errors = errDict
        self.message = self._getMessage()

    def _getMessage(self):
        ret = ''
        for e in self.errors.items():
            ret += '%s: %r\n' % e
        return ret

    def __str__(self):
        return self.message

class G3InvalidRespError(G3Error):
    pass

class G3UnknownTypeError(G3InvalidRespError):
    pass

class G3AuthError(G3Error):
    pass

class G3UnknownError(G3Error):
    pass
