'''
Created on 04.1.2010

@author: KMihajlov
'''
#from lib import messages
from lib import exceptions, messages
#from Controllers.MyRequestHandler import MyRequestHandler as mrh
import sys
import warnings
def property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probe_func(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k, locals.get(k)) for k in keys))
#            sys.settrace(None)
        return probe_func
#    sys.settrace(probe_func)
    function()
    return property(**func_locals)

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func

class LogInRequired():
    def __init__(self, redirect_url='/Login', message= messages.must_be_loged):
        self.redirect_url = redirect_url
        self.message = message
        self.handler = None

    def __call__(self, f):
        def new_f(request, *args):
            if request.User:
                f(request, args)
            else:
                request.status= self.message
                request.redirect(self.redirect_url)
        return new_f

class AdminOnly():
    def __init__(self, redirect_url='/Login', message= messages.must_be_admin):
        self.redirect_url = redirect_url
        self.message = message
        self.handler = None

    def __call__(self, f):
        def new_f(request, *args):
            if request.User and request.User.IsAdmin:
                f(request, args)
            else:
                request.status= self.message
                request.redirect(self.redirect_url)
        return new_f

class ErrorSafe():
    def __init__(self,
                 redirectUrl = '/',
                 message= messages.error_happened,
                 Exception = Exception,
                 showStackTrace = True ):
        self.redirectUrl = redirectUrl
        self.message = message
        self.Exception = Exception
        self.showStackTrace = showStackTrace
    def __call__(self, f):
        def new_f(request, *args):
            try:
                f(request, args)
            except self.Exception, ex:
                if request.status == None:
                    request.status = self.message or ''
                else:
                    request.status += self.message or ''
                    
                if self.showStackTrace:
                    request.status+= "  Details:<br/>"+ex.__str__()
                request.redirect(self.redirectUrl)
        return new_f