'''
Created on Jul 26, 2009
@author: kosta
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from lib import configuration as conf
########
import Controllers.adminHandlers as ah
import Controllers.baseHandlers as bh
import Controllers.postHandlers as ph
import Controllers.profileHandlers as prh
import Controllers.cmsHandlers as cms

application = webapp.WSGIApplication(
            [
             ## Standard Handlers
             ('/login', bh.LoginHandler),
             ('/logout', bh.LogoutHandler),
             ('/adduser', bh.AddUserHandler),
             ('/thanks', bh.ThanksHandler),
             ('/wishlist', bh.WishListHandler),
             ###########
             
             ## CMS Handlers
             ('/cms', cms.CMSAdminHandler),
             ('/cms/links', cms.CMSLinksHandler),
             ('/cms/content', cms.CMSContentHandler),
             ('/cms/pages/(.*)', cms.CMSPageHandler),
             ###########
             
             ## Post Handlers
             ('/blog', ph.HomeHandler),
             ('/blog/post', ph.PostHandler),
             ('/blog/comment', ph.CommentHandler),
             ('/blog/images/(.*)', ph.PostImageHandler),
             ('/blog/quote', ph.QuoteHandler),
             ###########
             
             ## Profile Handlers
             ('/profile', prh.UserProfileHandler),
             ('/profile/images', prh.ProfileImagesHandler),
             ###########
             
             ## Administrator Handlers
             ('/admin/searchusers', ah.UserSearchHandler),
             ('/admin/searchresults', ah.SearchResultsHandler),
             ('/admin/addadmin', ah.AddAdminHandler),
             ('/admin/listadmins', ah.ListAdminsHandler),
             ('/admin/listusers', ah.ListUsersHandler),
             ###########
            ], debug = conf.mode)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

