import os, glob
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import textwrap
from multiprocessing import Process, Queue
import time
from subprocess import Popen
import shlex
import tempfile
import socket
import pickle
import sys

# basically:
# watch --file a.md --cmd "pandoc -o a.html a.md"

# check for changes every second
POLLING_INTERVAL = 1
PORT = 5219



def getArguments():
	description = "Run a command when a file changes."
	epilog = textwrap.dedent('''\
		example:
		    watch --file readme.md --cmd "pandoc readme.md -o readme.html"
		''')
	
	parser = ArgumentParser(prog="watch", formatter_class=RawDescriptionHelpFormatter, description=description, epilog=epilog)
	parser.add_argument("-f", "--file", action="store",  required=True, nargs='+', help="The file to watch.")
	parser.add_argument("-c", "--cmd", action="store", required=True, help="The command to run when the file changes.  This should be a quoted string.")
	parser.add_argument("-s", "--stop", action="store_true", help="Stop watching files.")
	parser.add_argument("-l", "--list", action="store_true", help="List the files being watched and the commands that run when they change.")
	return parser.parse_args()



def formatArgs(arguments):
	# make sure the file exists
	# turn the file into an absolute path
	# should we save the environment too?
	if arguments.list:
		return "list"

	if arguments.stop:
		return "stop"

	files = arguments.file
	newf = []
	for f in files:
		newf.extend(glob.glob(f))
	files = map(os.path.abspath,newf)

	for f in files:
		if not os.path.isfile(f):
			raise Exception("Error:", f, "doesn't exist")

	cmd = arguments.cmd
	bundle = [{f: cmd} for f in files]
	return bundle



def watcherFilePath():
	temporaryDir = tempfile.gettempdir()
	return os.path.join(temporaryDir, "watcherpid")


def isAlreadyRunning():
	# see if the watcherpid file is in the temporary directory
	return os.path.isfile(watcherFilePath())



def startBackgroundProcess():
	watcherObj = Watcher()
	p = Process(target=watcherObj)
	p.start()



def addToBackgroundProcess(args):
	# set up socket business
	global PORT
	address = ("localhost", PORT)
	client = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
	client.connect((address))

	if args in ["halt", "list"]:
		client.send(pickle.dumps(args))
	else:
		for pair in args:
			client.send(pickle.dumps(pair))






def run():
	args = getArguments()
	fmt = formatArgs(args)

	#if not isAlreadyRunning():
	startBackgroundProcess()

	#addToBackgroundProcess(fmt)


class Watcher:
	def __init__(self):
		# file -> cmd
		self.watching = {"test": "ping google.com"}

		# file -> modification time
		self.mod_times = {}

		#self.setupServer()
		self.holdMarkerFile()


	def holdMarkerFile(self):
		
		# hold onto the file handle forever, basically
		self._hold = open(watcherFilePath(), "w")
		self._hold.write(str(os.getpid()))
	


	def stop(self):
		# close and remove that file, showing that we are done
		self._hold.close()
		os.unlink(watcherFilePath())

		sys.exit(0)

		



	def setupServer(self):
		print "got here!"
		"""This is going to be a locally-running server"""
		global PORT

		server_address = ('localhost', PORT)

		def getter():
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.bind((server_address))

			while True:
				server.listen(5)
				conn, addr = server.accept()
				data = conn.recv(4096)
				self.process(data)


		p = Process(target=getter)
		p.start()
		p.join()


	def process(self, data):
		"""all data is coming in pickled"""
		data = pickle.loads(data)
		if data == "stop":
			self.stop()
		elif data == "list":
			self.list()
		else:
			self.watching[data["file"]] = data["cmd"]


	def list(self):
		print "Watching these files with these commands:"
		for k,v in self.watching.iteritems():
			print k, v




	def __call__(self):
		global POLLING_INTERVAL

		while True:
			time.sleep(POLLING_INTERVAL)

			for f in self.watching.keys():
				# initial case: we don't have a date for these things
				if not self.mod_times.has_key(f):
					self.mod_times[f] = os.stat(f).st_mtime
				else:
					m = os.stat(f).st_mtime
					if m > self.mod_times[f]:
						self.mod_times[f] = m
						print "The file", f, "has changed!"
						#Popen(shlex.split(self.watching[f]))




if __name__ == "__main__":
	run()