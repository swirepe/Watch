from copy import deepcopy
import glob
import os
import textwrap
import time



verbose = 0
cmd = None
changes = dict()


def setLevel(level):
	global verbose
	verbose = level


def setCmd(command):
	global cmd
	cmd = command


def runAtLevel(level):
	global verbose
	def outer(f):
		def decoration(*args, **kwargs):
			if verbose >= level:
				return f(*args, **kwargs)
			else:
				return ""

		def doNothing(*args, **kwargs):
			return ""
		return decoration
	return outer

@runAtLevel(3)
def startupReport(files):
	global changes
	for f in files:
		if f.isdir:
			changes[f.path] = deepcopy(set(f.watching))

			print "[watch] Directory " + str(f) + "/ initialized with contents:"
			for fcontent in f.watching:
				print "    " + str(f) + " => " + str(fcontent) 
		else:
			changes[f.path] = f.mod_time
			print "[watch] File " + str(f) + " initialized with time " + str(f.mod_time)


@runAtLevel(2)
def globExpandReport(f):
	print textwrap.fill("[watch] Glob expanding " + str(f) + " -> " + ", ".join(glob.glob(f)), initial_indent='', subsequent_indent='    ')


@runAtLevel(2)
def pathExpandReport(files):
	print "[watch] Expanded paths:"
	for f in files:
		print "    " + f + " -> " + os.path.abspath(f)



def changeReport(f):
	output = _changeSimple(f) + _changeWithDetail(f) + _changeWithCommand(f)
	print output


@runAtLevel(1)
def _changeSimple(f):
	now = time.gmtime()
	strnow = "[" + time.strftime("%Y-%m-%d %H:%M:%S", now) + "]"

	ftype = "File"
	if f.isdir:
		ftype = "Directory"

	output = strnow + " " + ftype + " " + str(f) + " has changed.\n"
	return output



@runAtLevel(3)
def _changeWithDetail(f):
	global changes
	if f.isdir:
		# find the change and report it
		now = set(f.watching)
		then = changes[f.path]

		if now == then:
			output = ""
			for f in then:
				if f.hasChanged():
					output += "    (file " + str(f) + " has changed)\n"
					

		# list the files that have been added or removed
		else:
			difference = (now - then) | (then - now)
			output = ""
			for d in difference:
				output += "    (file " + str(d) + " has changed)\n"

		changes[f.path] = deepcopy(now)
	else:
		output = "    (from " + str(changes[f.path]) + " to " + str(f.mod_time) + ")\n"
		changes[f.path] = f.mod_time
	return output



@runAtLevel(2)
def _changeWithCommand(f):
	global cmd
	return "[watch] Running '" + cmd + "'"



