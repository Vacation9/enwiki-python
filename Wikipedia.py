import ClientCookie  # These modules were quite helpful when I was writing
import json          # WikiTools, so I would assume they will be helpful
import urllib        # again. I didn't include things like Tkinter in this
import urllib2       # because this is meant to be a Python API for MediaWiki.
cookies = ClientCookie.CookieJar()
opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookies))
opener.addheaders = [("User-Agent", "WikiTools/1.2"), ("X-Contact-Person", "Fox Wilson"), ("X-Contact-Email", "foxwilson123@gmail.com")]
ClientCookie.install_opener(opener)
class ApiAction:
	def __init__(self, data):
		if "action" not in data: data["action"] = "query"
		if "format" not in data: data["format"] = "json"
		self.data = self.encoded_dict(data)
		self.data_encoded = urllib.urlencode(self.data)
		self.request = urllib2.Request("http://en.wikipedia.org/w/api.php", self.data_encoded)
	def performAction(self):
		response = ClientCookie.urlopen(self.request).read()
		if self.data["format"] == "json": return json.loads(response)
		else: return response
	def encoded_dict(self, in_dict):
		"""
		UTF-8 encodes the data in a dictionary. You never need to call this, it's done
		internally.
		"""
		out_dict = {}
		for k, v in in_dict.iteritems():
			if isinstance(v, unicode): v = v.encode('utf8')
			elif isinstance(v, str): v.decode('utf8')
			out_dict[k] = v
		return out_dict
class User:
	"""
	This class represents a user. It can also login using the MediaWiki API.
	"""
	def __init__(self, username, password, debug = True):
		"""
		Initialize the object. Pass in a username and password for login
		purposes later.
		"""
		self.username = username
		self.password = password
		self.debug = debug
	def login(self):
		"""
		Perform the login itself. Note that in order to do this, we need two
		requests, one to get a "login token" and another to actually do the
		login.
		"""
		token = ApiAction({"action": "login", "format": "xml", "lgname": self.username, "lgpassword": self.password}).performAction().split('token="')[1].split('"')[0]
		self.done = "Success" in ApiAction({"action": "login", "format": "xml", "lgname": self.username, "lgpassword": self.password, "lgtoken": token}).performAction()
class Edit:
	"""
	Represents an edit to a page. 
	"""
	def __init__(self, page, text, summary = ""):
		"""
		Initialize the Edit, pass in the name of a page, the text to set
		that page to, and an edit summary.
		"""
		self.page = page
		self.text = text
		self.summary = summary
	def getToken(self):
		"""
		Get an Edit Token. The MediaWiki API requires this for security
		purposes.
		"""
		token = ClientCookie.urlopen("http://en.wikipedia.org/w/api.php?action=tokens&format=xml").read().split('edittoken="')[1].split('" />')[0]
		return token
	def makeEdit(self, append):
		"""
		Actually make the edit. This internally calls getToken.
		"""
		data = {
			"format" : "xml"           , 
			"action" : "edit"          ,  
			"token"  : self.getToken() , 
			"summary": self.summary    , 
			"text"   : self.text       , 
			"title"  : self.page
			}
		ApiAction(data).performAction()
class Article:
	def __init__(self, pageName):
		self.pageName = pageName
	def getToken(self):
		"""
		Get an Edit Token. The MediaWiki API requires this for security
		purposes.
		"""
		token = ClientCookie.urlopen("http://en.wikipedia.org/w/api.php?action=tokens&format=xml").read().split('edittoken="')[1].split('" />')[0]
		return token
	def getContent(self):
		"""
		Get an article from the MediaWiki API. This gets the last few revisions,
		then gets the content of the first revision.
		"""
		data = {
			"titles": urllib.quote(self.pageName),
			"prop"  : "revisions",
			"rvprop": "content"  
			}
		articleContent = ApiAction(data).performAction()[u'query'][u'pages']
		articleContent = articleContent[articleContent.keys()[0]][u'revisions'][0][u'*']
		articleContent = articleContent.replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
	def makeEdit(self, edit, summary):
		Edit(self.pageName, edit, summary).makeEdit()
class TalkPage(Article):
	def postMessage(self, subject, body):
		print "Posting message..."
		token = self.getToken()
		print token
		data = {
			"action"       : "edit",
			"title"        : self.pageName,
			"section"      : "new",
			"sectiontitle" : subject,
			"summary"      : "Adding section " + subject + " to the talk page",
			"text"         : body + "\n~~~~",
			"token"        : token
			}
		print ApiAction(data).performAction()
