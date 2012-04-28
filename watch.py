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
		self.watching = {}
		self.mod_times = {}

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

			if self.verbose >= 2:
				print textwrap.fill("[pre] Expanding " + str(f) + " -> " + ", ".join(glob.glob(f)), initial_indent='', subsequent_indent='    ')

			newf.extend(glob.glob(f))

		files = newf
		
		if arguments.absolute:
			files = map(os.path.abspath,files)

			if self.verbose >= 2:
				print "[pre] Expanded paths:"
				print "    " + "\n    ".join(files)

		for f in files:
			if not (os.path.isfile(f) or os.path.isdir(f)):
				raise Exception("Error:", f, "doesn't exist")

		self.cmd = shlex.split(arguments.cmd)



		



	def run(self):
		while True:
			for f in self.watching.keys():
				# initial case: we don't have a date for these things
				if not self.mod_times.has_key(f):
					self.mod_times[f] = os.stat(f).st_mtime
				else:
					m = os.stat(f).st_mtime
					if m > self.mod_times[f]:
						self.mod_times[f] = m

						# verbose output stuff
						if self.verbose >= 1:
							now = time.gmtime()
							strnow = "[" + time.strftime("%Y-%m-%d %H:%M:%S", now) + "]"

							output = strnow + " File " + f + " has changed."
							if self.verbose >= 2:
								output += "  Running '" + self.watching[f] + "'"
							print textwrap.fill(output, initial_indent='', subsequent_indent='    ')


						Popen(self.cmd)





if __name__ == "__main__":
	try:
		w = Watcher()
	except KeyboardInterrupt:
		print "\n"
		sys.exit(0)