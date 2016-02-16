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

from numpy import *
from datetime import date
import threading
import Queue
import re

duqueue = Queue.Queue(0)

class datautils_c:
	def __init__(self):
		self.ok = True
		self.clist = []

	def dictomat(self,dictionary,attributes,currency=False):
		num = len(attributes)
		mat = zeros((1,num))
		for d in dictionary:
			row = zeros((1,num))
			for i,a in enumerate(attributes):
				if currency == True and a == 'c':
					if self.clist.count(d['c']) == 0:
						self.clist.append(d['c'])
					ci = self.clist.index(d['c'])
					row[0,i] = float(ci)
				else:
					row[0,i] = float(d[a])
			mat = vstack((mat,row))
		return mat[1:,:]

	def tdattocalcloop(self,datmat,attr,adatmat,srow=0,erow=-1,store=-1):
		global duqueue
		calcmat = zeros((1,adatmat.shape[0]+1))
		if erow == -1:
			erow = datmat.shape[0]
		for i in range(srow,erow):
			row = zeros((1,adatmat.shape[0]+1))
			datrow = datmat[i,:]
			fs = datmat[i,attr.index('fs')]
			fq = datmat[i,attr.index('fq')] + datmat[i,attr.index('fc')]
			ts = datmat[i,attr.index('ts')]
			tq = datmat[i,attr.index('tq')] - datmat[i,attr.index('tc')]
			fcol = where(adatmat==fs)
			tcol = where(adatmat==ts)
			row[0,0] = datrow[0] #date
			row[0,fcol[0][0]+1] = -fq
			row[0,tcol[0][0]+1] = tq
			calcmat = vstack((calcmat,row))
		if not store == -1:
			duqueue.put([store,calcmat[1:,:]])
			return
		return calcmat[1:,:]

	def tdattocalc(self,datmat,attr,adatmat,usethreads=True):
		global duqueue
		if datmat.shape[0] < 100 or usethreads == False:
			#d1 = datetime.now()
			calcmat = self.tdattocalcloop(datmat,attr,adatmat)
			#d2 = datetime.now()
			#print "No threads =",d2-d1
		else:
			#two threads
			#d1 = datetime.now()
			siz = datmat.shape[0]/3 # int division
			tds = []
			tds.append(threading.Thread(target=self.tdattocalcloop,args=[datmat,attr,adatmat,0,siz,0]))
			tds.append(threading.Thread(target=self.tdattocalcloop,args=[datmat,attr,adatmat,siz,2*siz,1]))
			tds.append(threading.Thread(target=self.tdattocalcloop,args=[datmat,attr,adatmat,2*siz,-1,2]))
			for t in tds:
				t.start()
			# ask thread if finished - aquire data - then close (instead of join)?
			# create class of tdattocalcloop - store result internal in that class?
			# queue.queue, attach number - then add in right order when creating matrix
			for t in tds:
				t.join()
			#d2 = datetime.now()
			#print "Threads =",d2-d1,duqueue.qsize()
			que = []
			que.append(duqueue.get())
			que.append(duqueue.get())
			que.append(duqueue.get())
			mstack = [0,0,0]
			mstack[que[0][0]] = que[0][1]
			mstack[que[1][0]] = que[1][1]
			mstack[que[2][0]] = que[2][1]
			calcmat = vstack((mstack[0],mstack[1]))
			calcmat = vstack((calcmat,mstack[2]))
			#calcmat = self.tdattocalcloop(datmat,attr,adatmat)
		return calcmat

	def isint(self,str):
		try:
			num = int(str)
		except ValueError:
			return False
		return True

	def isfloat(self,str):
		try:
			num = float(str)
		except ValueError:
			return False
		return True

	def isisin(self,s):
		p = re.compile('\A[A-Z0-9]{12}\Z')
		if p.match(s) == None:
			return False
		return True

	def ismorn(self,s):
		p = re.compile('\A[A-Z0-9]{10}\Z')
		if p.match(s) == None:
			return False
		return True

	def rstr(self,num,decimal=0):
		return str(round(num,decimal))

	def calcdates(self,yf,yt):
		if not yf == 0:
			df = yf*100+1
		else:
			df = 0
		if not yt == 0:
			dt = yt*100+12
		else:
			dt = 0
		return [df,dt]

	def ymtodatetime(self,datelist,fixdate=27):
		result = []
		for d in datelist:
			yy = int(d[0:4])
			mm = int(d[4:6])
			result.append(date(yy,mm,fixdate))
		return result

	def ymtoyear(self,datelist,fixdate=27):
		result = []
		for i,d in enumerate(datelist):
			yy = int(d[0:4])
			mm = int(d[4:6])
			if i == 0 and not mm == 12:
				yy = yy - 2
			else:
				yy = yy - 1
			mm = 11
			result.append(date(yy,mm,fixdate))
		return result

