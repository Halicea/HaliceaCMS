
import Models.BaseModels as base
from MyRequestHandler import MyRequestHandler

from google.appengine.api import memcache
from lib import messages
handlerType="base"
#A test class  only in debug mode#######################

class tests( MyRequestHandler ):
    def get( self ):
        self.SetTemplate(handlerType, 'test.html')
        self.respond()
class LoginHandler( MyRequestHandler ):
    def get( self ):
        self.SetTemplate(handlerType, 'base_Login.html')
        if not self.User:
            self.respond()
        else:
            self.redirect( '/' )
            
    def post( self ):
        self.SetTemplate(handlerType, 'base_Login.html')
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
    def get( self ):
        self.logout_user()
        self.redirect( '/Login' )

class AddUserHandler( MyRequestHandler ):
    def get( self ):
        self.SetTemplate(handlerType, 'base_AddUser.html')
        self.respond( locals() )

class ThanksHandler( MyRequestHandler ):
    def post( self ):
        self.SetTemplate(handlerType, 'base_Thanks.html')
        try:
            user = base.Person( Email=self.request.get( 'Email' ),
                           Name=self.request.get( 'Name' ),
                           Surname=self.request.get( 'Surname' ),
                           Password=self.request.get( 'Password' ),
                           Public=self.request.get( 'Public' ) == 'on' and True or False,
                           Notify=self.request.get( 'Notify' ) == 'on' and  True or False
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
            self.Template = 'base_AddUser.html'
            self.status = ex
            self.respond()

class WishListHandler(MyRequestHandler):
    def get(self):
        self.SetTemplate(handlerType, 'WishList.html')
        if self.g('op')=='del' and self.g('key'):
            if self.User and self.User.IsAdmin:
                k = base.WishList.get(self.g('key'))
                if k:
                    k.delete()
                    self.status ='Wish deleted!'
                else:
                    self.status='Wish does not exist'
            else:
                self.status = messages.must_be_loged
        else:
            self.status = messages.not_allowed_to_access
        self.respond({'wishlist' : base.WishList.GetAll()})
            #self.respond()
    def post(self):
        if self.g('op')=='add':
            result = base.WishList.CreateNew(self.User, self.g('wish'), _isAutoInsert=True)
            #wishes = memcache.get('wishes')
#            if wishes:
#                wishes.append(result)            
            if self.isAjax:
                self.resonse.out.write('sucess')
            else:
#                self.SetTemplate(handlerType, 'WishList.html')
                self.redirect('/WishList?op=lst')
                
                