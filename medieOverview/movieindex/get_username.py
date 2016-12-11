from threading import current_thread

_requests = {}

def get_username():
    t = current_thread()
    if t not in _requests:
         return None
    return _requests[t]

class RequestMiddlewareOld(object):
    def process_request(self, request):
        _requests[current_thread()] = request
        
    def __init__(self, *args, **kwargs):
        return self
    
class RequestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        _requests[current_thread()] = request
        response = self.get_response(request)
    
        # Code to be executed for each request/response after
        # the view is called.

        return response