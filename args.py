from argparse import ArgumentParser, RawDescriptionHelpFormatter
import os
import sys
import textwrap
import time


def getArguments(defaultPollingInterval):
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

		    watch -f ./experiments --cmd "echo experiment done!"
		''')
	
	parser = ArgumentParser(prog="watch", formatter_class=RawDescriptionHelpFormatter, description=description, epilog=epilog)
	parser.add_argument("-f", "--file", action="store",  required=True, nargs='+', help="The file(s) to watch.")
	parser.add_argument("-c", "--cmd", action="store", required=True, nargs='+', help="The command to run when the file(s) changes.  This should be a quoted string.")
	parser.add_argument("-i", "--interval", default=defaultPollingInterval, action="store", help="The interval to check the file(s) at, in seconds.", type=float)
	parser.add_argument("-a", "--absolute", action="store_true", help="Guess the absolute paths of the files being watched.")
	parser.add_argument("-v", "--verbose", action="count", help="Output file names and commands as they are run.")
	return parser.parse_args()



