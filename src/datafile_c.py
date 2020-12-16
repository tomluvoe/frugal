"""
Frugal - Copyright 2006-2010 Thomas Larsson

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

import os
import shutil
import codecs
from xml.dom.minidom import parse

class datafile_c:
	def __init__(self,parent,xmlfile,toptag,tag,attributes,sort=False):
		self.attributes = attributes
		self.dictionary = []
		self.dataok = False
		self.sort = sort
		self.filename = xmlfile
		self.tagxml = toptag
		self.tagitem = tag
		self.parent = parent
		self.unsaved = False
		if not os.path.exists(self.filename):
			return None
		dom = parse(self.filename)
		elements = dom.getElementsByTagName(tag)
		self.dataok = True
		for e in elements:
			d = {}
			for a in attributes:
				if e.hasAttribute(a):
					attr = e.getAttribute(a)
					if a == 'd':
						[yy,mm,dd] = attr.split('-')
						attr = yy+mm+dd
					d[a] = attr
				else:
					self.dataok = False
			self.dictionary.append(d)
		dom.unlink()
		self.sortdata()

	def sortdata(self):
		if self.dataok == True and self.sort == True:
        		#self.dictionary.sort(cmp=lambda x,y: cmp(x['d'],y['d']))
				self.dictionary = sorted(self.dictionary, key=lambda dict: dict['d'])

	def updatedict(self,index,column,data):
		self.dictionary[index][self.attributes[column]] = data
		self.parent.unsaved = 1
		self.unsaved = True

	def addtodict(self,dict):
		for a in self.attributes:
			if a not in dict:
				return False
		self.dictionary.append(dict)
		self.sortdata()
		self.parent.unsaved = 1
		self.unsaved = True

	def writetofile(self):
		if not self.dataok == True:
			return False
		shutil.copyfile(self.filename,self.filename+'.old')
		f = codecs.open(self.filename,mode='w',encoding='utf-16')
		#f.write("<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n")
		f.write("<?xml version=\"1.0\" encoding=\"utf-16\"?>\n")
		f.write("<%s>\n"%self.tagxml)
		for itm in self.dictionary:
			f.write("<%s"%self.tagitem)
			for attr in self.attributes:
				f.write(" %s=\""%attr)
				if attr == 'd':
					yr = itm[attr][0:4]
					mo = itm[attr][4:6]
					da = itm[attr][6:8]
					attrval = "%s-%s-%s"%(yr,mo,da)
				else:
					attrval = itm[attr]
				f.write(str(attrval))
				f.write("\"")
			f.write("/>\n")
		f.write("</%s>\n"%self.tagxml)
		f.close()
		self.unsaved = False
		return True

	def xmltofile(self):
		return

def main():
	datfile = datafile_c('transactions_export.xml','transactions','item',['d','fs'],True)

if __name__ == '__main__':
	main()
