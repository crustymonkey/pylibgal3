
__all__ = ['BaseRequest' , 'GetRequest' , 'PostRequest' , 'PutRequest' , 
    'DeleteRequest']

from urllib2 import Request

class BaseRequest(Request):
    pass

class GetRequest(BaseRequest):
    pass

class PostRequest(BaseRequest):
    pass

class PutRequest(BaseRequest):
    pass

class DeleteRequest(BaseRequest):
    pass
