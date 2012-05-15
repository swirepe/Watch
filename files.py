# Peter Swire, 2012
# swirepe.com
# this is basically tail -f, but for arbitrary commands
import os
from itertools import chain


def watchFactory(path):
	if os.path.isdir(path):
		return Directory(path)
	elif os.path.isfile(path):
		return File(path)

	raise ValueError(path + " not found.")



class File:
	def __init__(self, path):
		self.isdir = False
		self.path = path
		self.mod_time = os.stat(path).st_mtime


	def hasChanged(self):
		m = os.stat(self.path).st_mtime
		if m > self.mod_time:
			self.mod_time = m
			return True

		return False


	def __str__(self):
		return self.path


	def __eq__(self, other):
		"""Compare by path"""
		return other.path == self.path

	def __hash__(self):
		return hash(self.path)


class Directory(File):
	def __init__(self, path):
		self.isdir = True
		self.path = path
		self.watching = self.getInDirectory(self.path)
		

	def getInDirectory(self, path):
		dircontents = []
		for root, dirnames, fnames in os.walk(path):
			contents = [watchFactory(os.path.join(root, f)) for f in chain(dirnames, fnames)]
			dircontents.extend(contents)

		return dircontents


	def hasChanged(self):
		# if a directory has changed, its contents have changed
		# (either added or removed files, or the files have changed)

		# added or removed files
		nowContents = self.getInDirectory(self.path)
		if set(nowContents) != set(self.watching):
			self.watching = nowContents
			return True


		# or a file has changed
		for w in self.watching:
			if w.hasChanged():
				return True

		return False
