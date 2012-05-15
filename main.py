from args import getArguments
from files import watchFactory
import glob
import shlex
from subprocess import Popen
import sys
import textwrap
import time
import verbose

# default: check for updates every second
POLLING_INTERVAL = 1.0


class Watcher:
	def __init__(self, args):
		global POLLING_INTERVAL
		POLLING_INTERVAL = args.interval

		verbose.setLevel(args.verbose)
		verbose.setCmd(args.cmd[0])

		self.cmd = shlex.split(args.cmd[0])
		self.watching = self.processFiles(args.file, args.absolute)

		self.cmd = shlex.split(args.cmd[0])

		verbose.startupReport(self.watching)



	def processFiles(self, files, absolute=False):
		# expand the globs
		newf = []
		for f in files:
			verbose.globExpandReport(f)
			newf.extend(glob.glob(f))

		files = newf

		# absolute paths
		if absolute:
			verbose.pathExpandReport(files)
			files = map(os.path.abspath,files)


		# convert to the appropriate objects
		files = map(watchFactory, files)
		return files



	def run(self):
		global POLLING_INTERVAL
		while True:
			time.sleep(POLLING_INTERVAL)
			for f in self.watching:
				if f.hasChanged():
					verbose.changeReport(f)
					Popen(self.cmd)


if __name__ == "__main__":
	w = Watcher(getArguments(POLLING_INTERVAL))
	try:
		w.run()
	except KeyboardInterrupt:
		print "\n"
		sys.exit(0)