# Watch
A small utility for acting on file changes


	usage: watch [-h] -f FILE [FILE ...] -c CMD [-i INTERVAL] [-a] [-v]

	Run a command when a file changes.

	optional arguments:
	  -h, --help            show this help message and exit
	  -f FILE [FILE ...], --file FILE [FILE ...]
	                        The file(s) or directories to watch.
	  -c CMD, --cmd CMD     The command to run when the file(s) changes. 
	                        This should be a quoted string.
	  -i INTERVAL, --interval INTERVAL
	                        The interval to check the file(s) at, in seconds.
	  -a, --absolute        Guess the absolute paths of the files being watched.
	  -v, --verbose         Output file names and commands as they are run.

	Examples:
	    watch --file readme.md --cmd "pandoc readme.md -o readme.html"

	    watch -f somelog.txt -c "cat somelog.txt"

	    watch --file *.c *.h --cmd "make"

	    watch -f ./experiments --cmd "echo experiment done!"


Exe built with [py2exe] downloaded from [here.](http://www.lfd.uci.edu/~gohlke/pythonlibs/#py2exe)

Watch is released under the [MIT License].

Copyright (C) 2012 Peter Swire


[MIT License]: http://www.opensource.org/licenses/mit-license.html
[py2exe]: http://www.py2exe.org/
