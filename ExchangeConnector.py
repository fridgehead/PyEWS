from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, ServiceAccount, \
    EWSDateTime, EWSTimeZone, Configuration, NTLM, Message, \
    Mailbox, Attendee, Q, ExtendedProperty, FileAttachment, ItemAttachment, \
    HTMLBody, Build, Version, transport, Folder
from threading import Lock

class ExchangeConnector:
	def __init__ (self):
		self.url = ""
		self.connected = False
		self.account = None
		self.lock = Lock()

	def connect(self, url, email):
		ews_url = url# "http://localhost:7001/EWS/Exchange.asmx"
		ews_auth_type = transport.NOAUTH
		primary_smtp_address = email #"tom.wyatt@serverchoice.com"
		credentials = Credentials(primary_smtp_address, 'topsecret')
		config = Configuration(service_endpoint=ews_url, credentials=credentials, auth_type=ews_auth_type)
		self.account = Account(
		    primary_smtp_address=primary_smtp_address, config=config, autodiscover=False, access_type=DELEGATE
		)

	def getTree(self, folderPath=""):
		if self.account:
			folder = self.account.root
			if folderPath != "":
				folder = self.getFolder(folderPath)	
			if folder is not None:
				self.lock.acquire()
				ret = folder.tree() 
				self.lock.release()
				return ret 
			else:
				return "current folder invalid"
		else:
			return "not connected"

	def getFolderContents(self, path):
		if self.account is None:
			return 
		else :
			folder = self.getFolder(path)
			self.lock.acquire()
			qs = folder.all()
			ret = list(qs)	
			self.lock.release()
			return qs

	def exportPath(self, path):
		folder = self.getFolder(path)
		response = ""
		if folder is not None:
			self.lock.acquire()
			
			response = self.account.export(folder.all())
			self.lock.release()
		return response

	# get all folders under a given path
	def getFolders(self, path):
		if self.account is None:
			return False	
		#if path[0] == '/':
		#		path = path[1:]	
		self.lock.acquire()
		folders = self.account.root.glob(path)
		flist = list(folders)
		self.lock.release()
		return flist
	
	def getFolder(self, path):
		if self.account is None:
			return False	
		#if path[0] == '/':
		#		path = path[1:]	
		self.lock.acquire()
		folders = self.account.root.glob(path)
		self.lock.release()
		flist = list(folders)
		if len(flist) > 0:
			return flist[0]
		else:
			return None	
	

	def folderExists(self, path):
		folder = self.getFolder(path)
		if folder != None:
			return True
		return False
			
	def refresh(self):
		if self.account is not None:
			self.lock.acquire()
			self.account.root.refresh()
			self.lock.release()

	def getFolderList(self):
		pass


