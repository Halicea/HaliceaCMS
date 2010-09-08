'''
Created on Aug 9, 2009

@author: Kosta Mihajlov
'''
########
import Models.BlogModels as bm
from google.appengine.api import memcache 
import datetime as dt
from MyRequestHandler import MyRequestHandler
handlerType = "blog"

class HomeHandler(MyRequestHandler):
    def get(self):
        self.SetTemplate(handlerType, 'post_Home.html')
        posts = memcache.get('posts') 
        if posts is None:
            posts = bm.Post.all()
            posts = posts.order('-DateModified')
            posts = posts.fetch(20, self.g('offset') or 0)
            memcache.add('posts', posts)
        self.respond({'posts':posts})

class PostHandler(MyRequestHandler):
    def get(self):
        try:
            # Admin options handling
            if self.g('op') and self.User and self.User.IsAdmin:
                if self.g('op')=='add':
                        self.SetTemplate(handlerType, 'post_AddPost.html')
                        self.respond()
                elif self.g('op')=='upd' and self.g('key'):
                    self.SetTemplate(handlerType, 'post_AddPost.html')
                    if self.g('key'):
                        p= bm.Post.get(self.g('key'))
                        if p:
                            self.respond({'post':p})
                        else:
                            self.respond()
                    else:
                        self.status="Such post does not exist! Create new if you like."
                        self.respond()
                elif self.g('op') == 'del' and self.g('key'):
                    p = bm.Post.get(self.g('key'))
                    if p:
                        p.delete()
                        memcache.delete('posts')
                        self.status = "Post is deleted"
                        self.redirect(self.request.URI)
                    else:
                        self.status('Such post does not exist!')
                        self.redirect(self.request.URI)
                elif self.g('op')=='arh' and self.g('key'):
                    p = bm.Post.get(self.g('key'))
                    if p and not p.IsArchive:
                        p.IsArchive = True
                        p.put()
                    self.SetTemplate(handlerType, 'post_Post.html')    
                    self.respond()
                elif self.g('op')=='unarh' and self.g('key'):
                    p = bm.Post.get(self.g('key'))
                    if p and p.IsArchive:
                        p.IsArchive = False
                        p.put()
                    self.SetTemplate(handlerType, 'post_Post.html')    
                    self.respond()
            # Normal Display of the post. plus increment the read oh the posts
            elif self.g('key') and not self.g('op'):
                self.SetTemplate(handlerType, 'post_Post.html')
                p = bm.Post.get(self.g('key'))
                if not p.TimesRead: p.TimesRead=1 
                else: p.TimesRead=p.TimesRead+1
                p.put()
                self.respond({'post':p})
            # Search posts because no post key parameter was passed
            elif not self.g('key') and not self.g('op'):
                self.SetTemplate(handlerType, 'post_SearchPost.html')
                if self.g('op') == 'src':
                    if (self.g('fromDate') and self.g('toDate')) or self.g('title'):
                        f = dt.datetime.strptime(self.g('fromDate'), '%m/%d/%Y' )
                        t = dt.datetime.strptime(self.g('toDate'), '%m/%d/%Y' )
                        title = self.g('title')
                        self.respond({'posts':bm.Post.GetLastPosts(5, 20) })
                else:
                    self.respond()
            else:
                self.redirect('/NotAuthorized')
                
        except Exception, e:
            #helpers.extend_exception(e, self)
            raise
            
    def post(self):
        if self.User.IsAdmin:
            self.SetTemplate(handlerType, 'post_AddPost.html')
            if self.g('op') == 'add':    
                if self.g('title') and self.g('entry'):
                    post = bm.Post.CreateNew(self.g('title'), self.g('entry'), self.User, _autoInsert=True)
                    memcache.delete('posts')
                    self.status = 'Post "'+post.Title+'" Saved!'
                    self.redirect('/post?key=' + post.key().__str__())
                else:
                    #self.status = 'There was not Title on the Post, You Must Add Title and Enter the text'
                    self.respond()
            #update
            elif self.g('op') == 'upd' and self.g('key'):
                post = bm.Post.get(self.g('key'))
                if post:
                    if self.g('title') and self.g('entry'):
                        post.Title = self.g('title')
                        post.Entry = self.g('entry')
                        post.DateModified = dt.datetime.now()
                        post.save()
                        memcache.delete('posts')
                        self.status = 'Post "'+post.Title+'" Saved!'
                        self.redirect('/post?key=' + str(post.key()))
                    else:
                        self.status = 'There was not Title on the Post, You Must Add Title and Enter the text'
                        self.SetTemplate(handlerType, 'post_AddPost.html')
                        self.respond({'post':post})
                else:
                    self.status = "No valid Post was given"
                    self.redirect('/Home')
        else:
            self.redirect("/NotAuthorized")
class PostImageHandler(MyRequestHandler):
    def get(self , ImageId):
        pass
#        post = self.I
#        if post.Image:
#            self.response.headers['Content-Type'] = "image/png"
#            self.response.out.write( post.Image )
#        else:
#            self.response.out.write( "No image" )
        
class CommentHandler(MyRequestHandler):
    def get(self):
        self.SetTemplate(handlerType, 'post_Comment.html')
        if self.g('op') == 'add':
            if self.g('postKey') and self.g('comment'):
                post = bm.Post.get(self.g('postKey'))
                if post:
                    bm.Comment.CreateNew(post, self.g('comment'), self.User, True, _isAutoInsert=True)
                    self.status = 'Comment was added'
                    self.redirect('/post?key=' + str(post.key()))
                else:
                    self.status = 'Not valid post was provided!'
                    self.redirect('/Post')
            else:
                self.status = 'Invalid parameters, Cannot save such comment'
                self.redirect('/post?key=' + str(post.key()))
                
        elif self.g('op') == 'del' and self.g('key'):
            c = bm.Comment.get(self.g('key'))
            if c:
                t = c.ReferencePost.key()
                c.delete()
                self.status = "Comment Deleted"
                self.redirect('/post?key=' + str(t) + '&')
            else:
                self.status = 'Such Comment does not exist'
                self.redirect('/')
        elif self.g('postKey'):
            self.redirect('/Post?key=' + self.g('postKey'))
#        elif self.g('op')=='upd':
#            pass
class QuoteHandler(MyRequestHandler): 
    def get(self, test):
        self.Template = 'post_AddQuote.html'
        if self.User and self.User.IsAdmin:
            if self.request.get('Quote'):
                quote = bm.Quote(
                         QuoteText=self.request.get('Quote'),
                         Author=self.User,
                         CreatedOn=dt.datetime.today(),
                         PublishDate=dt.datetime.today()
                         )
                quote.put()
            else:
                self.respond()
        else:
            self.status = 'You must be administrator in order to create a quote'
            self.redirect('/Login')
            
        