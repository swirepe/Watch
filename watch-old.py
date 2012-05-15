# Peter Swire, 2012
# swirepe.com
# this is basically tail -f, but for arbitrary commands
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import glob
from multiprocessing import Process
import os
from subprocess import Popen
import shlex
import sys
import textwrap
import time
import signal

# check for changes every second
POLLING_INTERVAL = 1


class Watcher:
	def __init__(self):
		self.watching = []
		self.mod_tracker = {}

		args = self.getArguments()
		self.formatAndAddArgs(args)
		self.run()



	def getArguments(self):
		# note: the --cmd argument needs to be quoted,
		# so that we don't confuse arguments to this program with arguments to the command to run
		description = "Run a command when a file changes."
		epilog = textwrap.dedent('''\
			Watch: a utility for acting on file changes.
			Copyright (c) 2012, Peter Swire - swirepe.com

			Examples:
			    watch --file readme.md --cmd "pandoc readme.md -o readme.html"

			    watch -f somelog.txt -c "cat somelog.txt"

			    watch --file *.c *.h --cmd "make"
			''')
		
		parser = ArgumentParser(prog="watch", formatter_class=RawDescriptionHelpFormatter, description=description, epilog=epilog)
		parser.add_argument("-f", "--file", action="store",  required=True, nargs='+', help="The file(s) to watch.")
		parser.add_argument("-c", "--cmd", action="store", required=True, nargs='+', help="The command to run when the file(s) changes.  This should be a quoted string.")
		parser.add_argument("-i", "--interval", default=POLLING_INTERVAL, action="store", help="The interval to check the file(s) at, in seconds.", type=float)
		parser.add_argument("-a", "--absolute", action="store_true", help="Guess the absolute paths of the files being watched.")
		parser.add_argument("-v", "--verbose", action="count", help="Output file names and commands as they are run.")
		return parser.parse_args()



	def formatAndAddArgs(self, arguments):
		# make sure the file exists
		# turn the file into an absolute path
		global POLLING_INTERVAL
		POLLING_INTERVAL = arguments.interval

		self.verbose = arguments.verbose


		files = arguments.file
		newf = []
		for f in files:
			self.verboseGlobExpandReport(f)
			newf.extend(glob.glob(f))

		files = newf
		
		if arguments.absolute:
			files = map(os.path.abspath,files)

			if self.verbose >= 2:
				print "[watch] Expanded paths:"
				print "    " + "\n    ".join(files)

		self.getInitialTimes(files)
		self.cmd = shlex.split(arguments.cmd[0])



	def run(self):
		global POLLING_INTERVAL
		while True:
			time.sleep(POLLING_INTERVAL)
			for f in self.watching:
				if self.hasChanged(f):
					verboseRunReport(f, m)
					Popen(self.cmd)



	def getInitialTimes(self, files):
		for f in files:
			if not os.path.exists(f):
				raise Exception("Error:", f, "doesn't exist")

			if os.path.isfile(f):
				self.mod_tracker[f] = os.stat(f).st_mtime
			elif os.path.isdir(f):
				self.addDirToModTracker(f)

		self.verboseStartupReport()


	def addDirToModTracker(self, f):
		if os.path.isdir(f):
			inf = self.getInDirectory(f)
			self.mod_tracker[f] = inf
			self.watching.extend(inf)
			self.getInitialTimes(inf)


	def getInDirectory(self, d):
		"""recursively go through directories, 
		listing all of the non-directory files in it"""
		ind = []
		for root, dirnames, fnames in os.walk(d):
			for f in fnames:
				ind.append( os.path.join(d, f))
			for d2 in dirnames:
				ind2 = self.getInDirectory(os.path.join(d,d2))
				ind.extend(ind2)

		ind.sort()

		return ind



	def hasChanged(self, f):
		"""Checks to see if a file or directory has changed,
		and updates it's status if it has

		If a directory has changed, its contents have changed.
		If a file has changed, it's modification time has changed.
		"""
		# if it doesn't exist, that may be a change. 
		# We need to remove it from the list of files to watch either way
		if not os.path.exists(f):
			self.watching.remove(f)

			if self.mod_tracker.has_key(f):
				self.mod_tracker.pop(f)
				return True

			return False


		# if it's a directory, the standard st_time won't cut it
		if os.path.isdir(f):
			inf = self.getInDirectory(f)

			# if the two contents aren't the same, the 
			# something has changed
			if not self.mod_tracker[f] == inf:
				self.mod_tracker[f] = inf
				return True

			# if one of the contents has changed, this has changed
			for fcontent in inf:
				if self.hasChanged(fcontent):
					return True


		else:
			# check the hard time for a file

			m = os.stat(f).st_mtime
			# case 1: the file didn't exist before and does now
			if not self.mod_tracker.has_key[f]:
				self.mod_tracker[f] = m
				self.watching.add(f)
				return True

			# case 2: the file existed and changed
			if m > self.mod_tracker[f]:
				self.mod_tracker[f] = m
				return True

		return False



	def verboseGlobExpandReport(self, f):
		if self.verbose >= 2:
			print textwrap.fill("[watch] Expanding " + str(f) + " -> " + ", ".join(glob.glob(f)), initial_indent='', subsequent_indent='    ')


	def verboseStartupReport(self):
		if self.verbose >= 3:
			for f in self.watching:
				if os.path.isdir(f):
					print "[watch] Directory " + str(f) + "/ initialized with contents:"
					for fcontent in self.mod_tracker[f]:
						print "        " + str(f) + " => " + str(fcontent) 
				else:
					print "[watch] File " + str(f) + " initialized with time " + str(self.mod_tracker[f])


	def verboseRunReport(self, f, mod_time):
		# verbose output stuff
		if self.verbose >= 1:
			now = time.gmtime()
			strnow = "[" + time.strftime("%Y-%m-%d %H:%M:%S", now) + "]"

			output = strnow + " File " + f + " has changed."

			if self.verbose >= 3:
				output += " (from " + str(self.mod_tracker[f]) + " to " + str(mod_time) + ") "				

			if self.verbose >= 2:
				output += "  Running '" + self.cmd + "'"
			print textwrap.fill(output, initial_indent='', subsequent_indent='    ')

			



if __name__ == "__main__":
	try:
		w = Watcher()
	except KeyboardInterrupt:
		print "\n"
		sys.exit(0)