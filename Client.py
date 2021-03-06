from cmd import Cmd
from ExchangeConnector import ExchangeConnector
from threading import Thread
from time import sleep
from exchangelib.items import Message,CalendarItem
from glob import glob
import traceback
import argparse
import shlex
import os

class BackgroundThread(Thread):
	def __init__(self, connect):
		self.connection = connect
		self.running = True
		print "BG Thread Init"

	def kill(self):
		self.running = False
	
	def sendHeartbeat(self):
		while self.running == True:
			sleep(10)
			self.connection.refresh()
#			print " ! heartbeat"
				
			
class SendParser(argparse.ArgumentParser):
    def error(self, message):
        print 'error: %s\n' % message

class MailClientPrompt(Cmd):
	
	def __init__(self):
		self.connector = ExchangeConnector()
		self.dirchain = ["Root"]
		self.settingsMap = {}
		self.settingsMap["url"] = "http://localhost:7001"
		self.settingsMap["heartbeat"] = "true"
		self.settingsMap["emailaddress"] = "target@domain.com"
		self.settingsMap["exportpath"] = "./export"

		# start a bg thread to do heartbeats etc
		self.bgThread = BackgroundThread(self.connector)
		thread = Thread(target=self.bgThread.sendHeartbeat)
		thread.start()
				
		Cmd.__init__(self)

	def do_send(self, args):
		parser = SendParser(prog="send")
		parser.add_argument("-t", "--to", help="Recipient")
		parser.add_argument("-s", "--subject", help="Message Subject")
		parser.add_argument("-a", "--attachmentfile", help="Message attachment")
		parser.add_argument("-n", "--attachmentname", help="Message attachment name")
		group = parser.add_mutually_exclusive_group()
		group.add_argument("-b", "--body", help="Message body")
		group.add_argument("-f", "--bodyfile", help="Message body file")
		argList = ""
		try:
			argList = parser.parse_args(shlex.split(args))
			body = ""
			if argList.bodyfile is not None:
				print "loading body from " + argList.bodyfile
				f = open (argList.bodyfile, "r")
				body = f.read()
				f.close()
			else:
				body = argList.body

			if argList.attachmentfile is not None:
				f = open (argList.attachmentfile, "rb")
				content = f.read()
				f.close()
				name = ""
				if argList.attachmentname is None:
					name = os.path.basename(argList.attachmentfile)
				else:
					name = argList.attachmentname
				self.connector.sendMessage(argList.to, argList.subject, body, attachmentBytes=content, attachmentName=argList.attachmentname)	
			else:
				self.connector.sendMessage(argList.to, argList.subject, body)
		except SystemExit:
			parser.print_help()
			return
			
		

	def do_connect(self, args):
		url = self.settingsMap["url"] + "/EWS/Exchange.asmx"
		email = self.settingsMap["emailaddress"]
		print "connecting to %s..." % (url)
		try:
			self.connector.connect(url, email)
			print "..connected!"
			self.connector.refresh()	
		except: 
			
			traceback.print_exc()
			print "connect error"

	def do_tree(self, args):
		path = "/".join(self.dirchain[1:])   
		print "tree for ", path
		print(self.connector.getTree(folderPath=path))

	def do_set (self, args):
		args = args.strip()
		if len(args) <= 0:
			print "Current Settings: "
			for k in self.settingsMap.keys():
				print "[%s] = %s" % (k, self.settingsMap[k])
			return
		parts = args.split("=")
		if len(parts) > 0:
			parts = [a.strip() for a in parts]
			print " setting %s to %s" % (parts[0], parts[1])
			if parts[0] in self.settingsMap.keys():
				self.settingsMap[parts[0]] = parts[1]

	def do_ls(self, args):
		print "Contents of folder..."
		print "         "
		# also refresh the cache
		path = "/".join(self.dirchain[1:])   
		items = self.connector.getFolderContents(path)
		for item in items:
			if isinstance(item, Message):
				sender = item.sender.email_address
				print "%s - %s" %( item.subject, sender )
			elif isinstance(item, CalendarItem):
				print item.subject
			else:
				print "%s item" %(type(item).__name__)

	def do_export(self, args):
		
		path = "/".join(self.dirchain[1:])   
		print "setting up export for path %s" % path
		items = self.connector.getFolderContents(path)
		outpath = self.settingsMap["exportpath"]
		if outpath[-1:] != "/":
			outpath += "/"
		for index, item in enumerate(items):
			print "exporting %s%i.eml" %(outpath,index)
			f = open(outpath + str(index) + ".eml", "wb")
			f.write(item.mime_content)
			f.close()
		

	def do_cd(self, args):
		loc = args.strip()
		if loc == "/":
			self.dirchain = ["Root"]
		elif loc == ".." :
			if len(self.dirchain) > 1:
				self.dirchain.pop()
				
		else:
			# lets make sure the folder exists first
			path = "/".join(self.dirchain[1:]) + "/" + loc
			if self.connector.folderExists(path):
				self.dirchain.append(loc)
			else:
				print "path doesnt exist : %s" % (path)
			
			
		self.prompt = "/".join(self.dirchain) + "/ > "
	
	def do_exit(self, args):
		self.bgThread.kill()
		raise SystemExit	

if __name__ == '__main__':
	prompt = MailClientPrompt()
	prompt.prompt = '> '
	prompt.cmdloop('Starting prompt...')
