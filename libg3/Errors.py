
__all__ = ['G3Error' , 'G3InvalidRespError' , 'G3UnknownTypeError' , 
    'G3AuthError' , 'G3UnknownError']

class G3Error(Exception):
    pass

class G3InvalidRespError(G3Error):
    pass

class G3UnknownTypeError(G3InvalidRespError):
    pass

class G3AuthError(G3Error):
    pass

class G3UnknownError(G3Error):
    pass
