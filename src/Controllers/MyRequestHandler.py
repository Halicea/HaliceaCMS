'''
Created on Aug 6, 2009
@author: kosta
'''

from google.appengine.ext import webapp
from Models.BaseModels import Person
#from lib.appengine_utilities import sessions
from lib.gaesessions import get_current_session
import lib.paths as paths
import lib.configuration as configuration
from os import path
from google.appengine.ext.webapp import template

#from lib.decorators import property as prop
from django.contrib.auth import get_user
# from Models import ProfileModels as pm
__mode__ = 'Debug'

class Operations(object):
	'''Defines the basic operations that can be user for a handler action
	This actions can be extended with the [add] method'''
	add = 'add'
	delete = 'del'
	insert = 'ins'
	update = 'upd'
	search = 'src'
	list = 'lst'
	@staticmethod
	def contains(operation):
		return [x for x in dir(Operations) if x == operation]
	@classmethod
	def add(cls, name, value):
		cls.__setattr__(name, value)
		

class MyRequestHandler( webapp.RequestHandler ):
	# Properties
	TemplateDir = 'Views'
	TemplateType = ''
	quote = None
	status = None
	isAjax=False
	__templateIsSet__= False
	__template__ =""
	def getTemplate(self):
		if not self.__templateIsSet__:
			tname = self.TemplateType
			if not tname:
				tname = self.__class__.__module__
				if tname.count("."):
					tname=tname[tname.rfind(".")+1:]
				tname=tname[:tname.find("Handlers")]
			hname= self.__class__.__name__
			hname=hname[:hname.find("Handler")]+".html"
	
			result = path.join(paths.GetTemplateDir(tname), hname)
			return result
		else:
			return self.__template__
	def SetTemplate(self, templateType, templateName):
		self.__templateIsSet__=True
		self.TemplateType=templateType
		self.TemplateDir = paths.GetTemplateDir(templateType)
		if templateName.find( self.TemplateDir ) < 0:
			self.__template__ = path.join( self.TemplateDir, templateName )
		else:
			self.__template__ = templateName
	Template =property(getTemplate)
	def __getSession__(self):
		return get_current_session()
	session = property(__getSession__)

	@classmethod
	def GetUser(cls):
		s = get_current_session()
		if s.is_active():
			return s.get('user', default=None)
		else:
			return None

	def get_user(self):
		return MyRequestHandler.GetUser()
	User=property(get_user, None)

	def login_user(self, uname, passwd):
		self.logout_user()
		user = Person.GetUser(uname, passwd)
		if user:
			self.session['user']= user; return True			
		else:
			return False
	def logout_user(self):
		if self.session.is_active():
			self.session.terminate()
		return True
	#request =None
	# end Properties

	# Constructors   
	def initialize( self, request, response ):
		"""Initializes this request handler with the given Request and Response."""
		self.isAjax = ((request.headers.get('HTTP_X_REQUESTED_WITH')=='XMLHttpRequest') or (request.headers.get('X-Requested-With')=='XMLHttpRequest'))
		self.request = request
		self.response = response
		webapp.RequestHandler.__init__( self )
		#self.request = super(MyRequestHandler, self).request
		if not self.isAjax: self.isAjax = self.g('isAjax')=='true'
		# set the status variable
		if self.session.has_key( 'status' ):
			self.status = self.session.pop('status')
# Methods
	def g(self, item):
		return self.request.get(item)

	def render_dict( self, basedict ):
		result = dict( basedict )
		if result.has_key( 'self' ):
			result.pop( 'self' )
		if not result.has_key( 'status' ):
			result['status'] = self.status
		if not result.has_key( 'quote' ):
			result['quote'] = self.quote
		if not result.has_key( 'mode' ):
			result['mode'] = __mode__
		if not result.has_key('current_user'):
			result['current_user'] = self.User
		if not result.has_key('op'):
			result['op'] = Operations
		#update the variables about the references
		result.update(paths.GetBasesDict())
		result.update(paths.GetMenusDict())
		result.update(paths.GetBlocksDict())		##end
		return result
	def respond( self, dict={} ):
		#self.response.out.write(self.Template+'<br/>'+ dict)
		self.response.out.write( template.render( self.Template, self.render_dict( dict ), 
												  debug = configuration.template_debug ) )
	def redirect_login( self ):
		self.redirect( '/Login' )
	def respond_static(self, text):
		self.response.out.write(text)	
	def redirect( self, uri, postargs={}, permanent=False ):
		innerdict = dict( postargs )
		if innerdict.has_key( 'status' ):
			self.status = innerdict['status']
			del innerdict['status']
		if self.status:
			self.session['status']=self.status
		if uri=='/Login' and not self.request.url.endswith('/Logout'):
			innerdict['redirect_url']=self.request.url
		if innerdict and len( innerdict ) > 0:
			params= '&'.join( [k + '=' + str(innerdict[k]) for k in innerdict] )
			if uri.find('?')==-1:
				webapp.RequestHandler.redirect( self, uri + '?' + params, permanent )
			elif uri.endswith('&'):
				webapp.RequestHandler.redirect( self, uri + params, permanent )
			else:
				webapp.RequestHandler.redirect( self, uri+ '&' + params, permanent )
		else:
			webapp.RequestHandler.redirect( self, uri, permanent )

class RoleAuthorization(object):
	@staticmethod
	def IsAdmin(user):
		if user and user.IsAdmin:
			return True
		return False
	
	@staticmethod
	def CanOpenPage(user, pageUrl):
		return True
#end Methods
