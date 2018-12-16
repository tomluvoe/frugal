import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')


"""
Frugal - Copyright 2006-2011 Thomas Larsson

This file is part of Frugal.

Frugal is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Frugal is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Frugal.  If not, see <http://www.gnu.org/licenses/>.
"""

import socket
import urllib2
import time
import threading
import sys

from datacoll_c import datacoll_c
from gui_c import gui_c,appl_c

__major_version__ = '0'
__minor_version__ = '26'

__program__ = 'Frugal'
__version__ = "%s.%s" % (__major_version__,__minor_version__)
__about__ = """%s version %s
Copyright (c) 2006-2011 Thomas Larsson

This program is distributed under the terms of the GNU General Public License.

%s is a simple yet powerful personal finance and stock portfolio management application. It provides quick on-line stock quote and currency rate updates and easy to understand graphical and textual views of your financial situation. 

More information @ http://www.samoht.se/frugal/""" % (__program__,__version__,__program__)

class frugalupd_c:
	RESULT = False
	LATEST = True

	def __init__(self,major,minor,callback):
		self.major_version = major
		self.minor_version = minor
		self.callback = callback
		self.sleeptime = 30
		time.sleep(2)
		while frugalupd_c.RESULT == False:
			self.do()
			if frugalupd_c.LATEST == False:
				self.callback()
			if self.sleeptime < 600:
				self.sleeptime = self.sleeptime * 2
			time.sleep(self.sleeptime)

	def do(self):
		socket.setdefaulttimeout(5)
		try:
			fd = urllib2.urlopen('http://www.samoht.se/frugal/latest_release')
			lr = fd.read(15)
			fd.close()
			fv = lr.split('.')
			if len(fv) < 2:
				return
			ma = int(fv[0])
			mi  = int(fv[1])
			if ma > int(self.major_version):
				frugalupd_c.LATEST = False
			if ma == int(self.major_version) and mi > int(self.minor_version):
				frugalupd_c.LATEST = False
			frugalupd_c.RESULT = True
		except IOError:
			pass

class frugal10_c:
	def __init__(self):
		self.datacoll = datacoll_c()
		self.fileok = False
		self.major_version = __major_version__
		self.minor_version = __minor_version__
		self.updcallback = None
		frugalupd = threading.Thread(target=frugalupd_c,args=[__major_version__,__minor_version__,self.updatecallback])
		#frugalupd.daemon = True
		frugalupd.setDaemon(True)
		frugalupd.start()

	def registerupdcallback(self,callback):
		self.updcallback = callback

	def updatecallback(self):
		if self.updcallback == None:
			return
		self.updcallback()

	def new(self,dirname,currency='EUR',pd=False):
		if not pd == False:
			pd.Update(50,'Creating new data files..')
		if self.datacoll.newfiles(dirname,currency) == False:
			return False
		return True

	def open(self,dirname,pd=False):
		if not pd == False:
			pd.Update(20,'Opening data files..')
		if self.datacoll.openfiles(dirname,pd) == False:
			return False
		self.fileok = True
		if not pd == False:
			pd.Update(60,'Data files opened.')
		if self.datacoll.calcnow(pd) == False:
			return False
		return True

	def save(self,pd=False):
		return self.datacoll.savefiles(pd)

	def calc(self,pd=False):
		if self.fileok == True:
			if self.datacoll.dicttomat(pd) == True:
				if self.datacoll.calcnow(pd) == True:
					return True
			else:
				return False
		return False	

	def downloadquotes(self,pd=False):
		return self.datacoll.downloadquotes(pd)

	def checkforupdate(self):
		if frugalupd_c.RESULT == False:
			#TODO ERROR MESSAGE
			return -1
		if frugalupd_c.LATEST == True:
			return 0
		return 1

def main():
	frugal = frugal10_c()
	app = appl_c()
	app.setup(__program__,__version__,__about__,frugal)
	app.MainLoop()

if __name__ == '__main__':
	main()
