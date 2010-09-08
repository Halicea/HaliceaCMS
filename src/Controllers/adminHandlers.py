'''
Created on Jul 21, 2009
@author: Kosta
'''

from google.appengine.ext import db
import Models.BlogModels as bm
from Models.BaseModels import Person, Admin


from MyRequestHandler import MyRequestHandler
from lib import messages
handlerType="admin"
class UserSearchHandler(MyRequestHandler):
    def get(self):
        self.SetTemplate(handlerType, 'admin_SearchUsers.html')
        if(self.User and self.User.IsAdmin):
            g = self.request.get
            if(g('search')):
                query = Person.all()
                #query.filter('Name=', g('search'))
                self.respond({'result':query.fetch(limit=100)})  
                #self.response.out.write(str(query.fetch(limit=20)))
            else:
                self.respond()
        else:
            self.redirect('/Login')

class SearchResultsHandler(MyRequestHandler):
    def get(self):
        self.SetTemplate(handlerType,'SearchResults.html')
        if(self.User and self.User.IsAdmin):
            g = self.request.get
            
            if(g('search')):
                query = Person.all()
                query.filter('Name=', g('search'))
                persons = query.fetch(limit=100)
                self.respond({'result':persons})  
            else:
                self.respond()
        else:
            self.redirect('/Login')

class AddAdminHandler(MyRequestHandler):
    def get(self):
        self.SetTemplate(handlerType,'admin_AddAdmin.html')
        g = self.request.get        
        if(self.User and self.User.IsAdmin):
            if(g('UserName')):
                u = Admin(userId=g('UserName'))
                db.put(u)
                self.respond({'laStatus':'Successfuly saved the Admin ' + g('UserName')})
            else:    
                self.respond()  
        else:
            self.redirect('/Login')

class ListAdminsHandler(MyRequestHandler):
    def get(self):
        self.SetTemplate(handlerType,'admin_ListUsers.html')
        if(self.User and self.User.IsAdmin):
            querry = Person.gql("WHERE IsAdmin =:v", v=True)
            result=querry.fetch(1000)
            self.respond({'result':result})
        else:
            self.redirect('/Login')
            self.status(messages.not_allowed_to_access)

class ListUsersHandler( MyRequestHandler ):
    def get( self ):
        self.SetTemplate(handlerType, 'admin_ListUsers.html')
        if self.User and self.User.IsAdmin:
            offset = self.request.get( 'Offset' ) or 0
            result = Person.all().fetch( limit=30, offset=offset )
            self.respond( locals() )
        else:
            self.status = 'You Must be Loged in as administrator in order to list the users'
            self.redirect( '/Login' )

