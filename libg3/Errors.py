
__all__ = ['G3Error' , 'G3AuthError' , 'G3UnknownError']

class G3Error(Exception):
    pass

class G3AuthError(G3Error):
    pass

class G3UnknownError(G3Error):
    pass
