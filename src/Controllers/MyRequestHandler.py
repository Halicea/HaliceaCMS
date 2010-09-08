'''
Created on Aug 6, 2009
@author: kosta
'''

from google.appengine.ext import webapp
import Models.BlogModels as bm
from Models.BaseModels import Person
from lib.appengine_utilities import sessions
import lib.paths as paths
import lib.configuration as configuration
from os import path
from google.appengine.ext.webapp import template
from lib import helpers
from lib import configuration as conf
import cgi

# from Models import ProfileModels as pm



class MyRequestHandler(webapp.RequestHandler):
    # Properties
    TemplateDir = 'Views'
    TemplateType = 'static'
    Template = ''
    last_posted = bm.Post.GetLastPosts(days_old=3, fetch_limit=7)
    quote = None
    status = None
    isAjax = False
    session = sessions.Session()
    t = {}
    def get_user(self):
        if self.session.has_key('user'):
            return self.session['user']
        else:
            return None
    User = property(get_user, None)

    def login_user(self, uname, passwd):
        user = Person.gql('WHERE Email= :email AND Password= :passwd', email=uname, passwd=passwd).get()
        if user == None :
            # we log out the user.
            if self.session.has_key('user'):
                self.session.delete_item('user', throw_exception=True)
            return False
        elif  user.__class__.kind() == 'Person':
            self.session['user'] = user
            return True
        else:
            raise Exception('MyException: Not a Valid Person Object')
    def logout_user(self):
        if self.session.has_key('user'):
            self.session.delete_item('user', throw_exception=True)
        return True
    #request =None
    # end Properties

    # Constructors  
    def SetTemplate(self, templateType, templateName):
        self.TemplateType = templateType
        self.TemplateDir = paths.GetTemplateDir(templateType)
        if templateName.find(self.TemplateDir) < 0:
            self.Template = path.join(self.TemplateDir, templateName)
        else:
            self.Template = templateName
 
    def initialize(self, request, response):
        """Initializes this request handler with the given Request and Response."""
        self.isAjax = ((request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest') or (request.headers.get('X-Requested-With') == 'XMLHttpRequest'))
        self.request = request
        self.response = response
        webapp.RequestHandler.__init__(self)
        #self.request = super(MyRequestHandler, self).request
        if not self.isAjax: self.isAjax = self.g('isAjax') == 'true'
        if self.request.get('status'):
            self.status = self.request.get('status')
    # end template property

# Methods
    def g(self, item):
        return self.request.get(item)
         
    def render_dict(self, basedict):
        result = dict(basedict)
        if result.has_key('self'): 
            result.pop('self')
        if not result.has_key('last_posted'):
            result['last_posted'] = self.last_posted
        if not result.has_key('status'):
            result['status'] = self.status
        if not result.has_key('quote'):
            result['quote'] = self.quote
        if not result.has_key('mode'):
            result['mode'] = conf.mode
        if not result.has_key('current_user'):
            result['current_user'] = self.User
        if not result.has_key('cvn'):
            result['cvn'] = helpers.get_cvn()    
        #update the variables about the references
        result.update(paths.GetBasesDict())
        result.update(paths.GetMenusDict())
        result.update(paths.GetBlocksDict())
        ##end
        return result

    def respond(self, dict={}):
        #self.response.out.write(self.Template+'<br/>'+ dict)
        self.response.out.write(template.render(self.Template, self.render_dict(dict),
                                                  debug=configuration.template_debug))
    def redirect_login(self):
        """Use this method to point to the Login Page"""
        self.redirect('/Login')
    
    def respond_static(self, text):
        self.response.out.write(text)
        
    def redirect(self, uri, postargs={}, permanent=False):
        innerdict = dict(postargs)
        if not innerdict.has_key('status') and self.status:
            innerdict['status'] = self.status
        if uri == '/Login':
            innerdict['redirect_url'] = self.request.url
        if innerdict and len(innerdict) > 0:
            params = '&'.join([cgi.escape(k) + '=' + cgi.escape(innerdict[k]) for k in innerdict])
            if uri.find('?') == -1:
                webapp.RequestHandler.redirect(self, uri + '?' + params, permanent)
            elif uri.endswith('&'):
                webapp.RequestHandler.redirect(self, uri + params, permanent)
            else:
                webapp.RequestHandler.redirect(self, uri + '&' + params, permanent)
        else:
            webapp.RequestHandler.redirect(self, uri, permanent)

class RoleAuthorization(object):
    @classmethod
    def IsAdmin(cls, user):
        if user and user.IsAdmin:
            return True
        return False
    
    @classmethod
    def CanOpenPage(user, pageUrl):
        """
        Here you can define rules, which types of users 
        will access certain pages
        """
        return True
#end Methods

