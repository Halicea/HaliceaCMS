
import Models.BaseModels as base
from MyRequestHandler import MyRequestHandler
from google.appengine.api import memcache
from lib import messages
from lib.decorators import AdminOnly, LogInRequired, ErrorSafe
from lib import configuration as conf
handlerType="base"
#A test class  only in debug mode#######################
class testHandler( MyRequestHandler ):
	def get( self ):
		self.respond()
################
class LoginHandler( MyRequestHandler ):
	@ErrorSafe()
	def get( self, *args ):
		if not self.User:
			if self.g('redirect_url'):
				self.respond({'redirect_url':self.g('redirect_url')})
			else:
				self.respond()
		else:
			self.redirect( '/' )
			
	def post( self ):
		uname = self.request.get( 'Email' )
		passwd = self.request.get( 'Password' )
		if (uname and passwd):
			if(self.login_user(uname, passwd)):
				if self.request.get( 'redirect_url' ):
					self.redirect( self.request.get( 'redirect_url' ) )
				else:
					self.redirect( '/' )
			else:
				self.status = 'Email Or Password are not correct!!'
				self.respond()
		else:
			self.status = 'Email Or Password are not correct!'
			self.respond()

class LogoutHandler( MyRequestHandler ):
	@LogInRequired(message = '')
	def get( self, *args ):
		self.logout_user()
		self.redirect( LoginHandler.get_url() )

class AddUserHandler( MyRequestHandler ):
	def get( self ):
		self.respond()
		
	def post( self ):
		self.SetTemplate(handlerType, 'Thanks.html')
		try:
			user = base.Person( 
						   UserName = self.g('UserName'),
						   Email=self.g( 'Email' ),
						   Name=self.g( 'Name' ),
						   Surname=self.g( 'Surname' ),
						   Password=self.g( 'Password' ),
						   Public=self.g( 'Public' ) == 'on' and True or False,
						   Notify=self.g( 'Notify' ) == 'on' and  True or False
						   )

			if ( self.request.get( 'Notify' ) == None and self.request.get( 'Notify' ) == 'on' ):
				user.Notify = True
			else:
				user.Notify = False

			if ( self.request.get( 'Public' ) == None and self.request.get( 'Public' ) == 'on' ):
				user.Public = True
			else:
				user.Public = False
			user.put()
			self.respond( locals() )
		except Exception, ex:
			self.status = ex
			self.redirect(AddUserHandler.get_url())
			
class WishListHandler(MyRequestHandler):
	def get(self):
		if self.g('op')=='del' and self.g('key'):
			self.deleteWish(self.g('key'))
		self.respond({'wishlist' : base.WishList.GetAll()})
		#self.respond()
	@AdminOnly('/WishList')
	def deleteWish(self, wishKey):
		k = base.WishList.get(wishKey)
		if k:
			k.delete()
			self.status ='Wish deleted!'
		else:
			self.status='Wish does not exist'

	def post(self):
		if self.g('op')=='add':
			base.WishList.CreateNew(self.User, self.g('wish'), _isAutoInsert=True)
			if self.isAjax:
				self.resonse.out.write('success')
			else:
				self.redirect(WishListHandler.get_url()+'?op=lst')