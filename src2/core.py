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
import re
import sys

import datafile
import utils
import online

from datetime import date,datetime

from numpy import *
from numpy import array as nparray

class core:
	def __init__(self):
	# initialization function
		self.unsaved = False
		self.opened = False
		self.tfile = 'transactions.xml'
		self.ttags = ['transactions','item']
		self.tattr = ['d','fs','fq','fp','fc','ts','tq','tp','tc','de']
		self.afile = 'accounts.xml'
		self.atags = ['accounts','account']
		self.aattr = ['num','c','de']
		self.cfile = 'currencies.xml'
		self.ctags = ['currencies','price']
		self.cattr = ['d','c','p'] 
		self.qfile = 'quotes.xml'
		self.qtags = ['quotes','quote']
		self.qattr = ['d','a','p']
		self.anams = []
		self.utils = utils.utils()
		self.online = online.quotes()
		self.assetnames = []

	def newproject(self,dir,currency='EUR'):
	# create new files based on currency currency
		if not os.path.exists(dir):
			return False
		if not currency in core.ALLOWEDCURRENCIES:
			return False
		tfile = dir+'/'+self.tfile
		afile = dir+'/'+self.afile
		cfile = dir+'/'+self.cfile
		qfile = dir+'/'+self.qfile
		if os.path.exists(tfile) or os.path.exists(afile) or os.path.exists(cfile) or os.path.exists(qfile):
			return False
		todaysdate = date.today().strftime('%Y-%m-%d')
		filedata = re.sub('CURRENCY',currency,core.TRANSACTIONS_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(tfile,'w')
		f.write(filedata)
		f.close()
		filedata = re.sub('CURRENCY',currency,core.ACCOUNTS_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(afile,'w')
		f.write(filedata)
		f.close()
		filedata = re.sub('CURRENCY',currency,core.CURRENCIES_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(cfile,'w')
		f.write(filedata)
		f.close()
		filedata = re.sub('CURRENCY',currency,core.QUOTES_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(qfile,'w')
		f.write(filedata)
		f.close()
		rv = self.openproject(dir)
		return rv

	def saveproject(self):
	# save all opened files
		if self.opened == False:
			return True
		if not self.tdict.writetofile() == True:
			return False
		if not self.adict.writetofile() == True:
			return False
		if not self.cdict.writetofile() == True:
			return False
		if not self.qdict.writetofile() == True:
			return False
		self.unsaved = False
		return True

	def issaved(self):
		if self.unsaved == False:
			return True
		return False

	def isopen(self):
		if self.opened == False:
			return False
		return True

	def openproject(self,dir):
	# open project files in dir
		if not os.path.exists(dir):
			return False
		if self.opened == True:
			return False
		# load dictionaries, sort dates
		self.tdict = datafile.file(self,dir+'/'+self.tfile,self.ttags[0],self.ttags[1],self.tattr,True)
		self.adict = datafile.file(self,dir+'/'+self.afile,self.atags[0],self.atags[1],self.aattr)
		self.cdict = datafile.file(self,dir+'/'+self.cfile,self.ctags[0],self.ctags[1],self.cattr,True)
		self.qdict = datafile.file(self,dir+'/'+self.qfile,self.qtags[0],self.qtags[1],self.qattr,True)
		# check files
		if self.tdict.dataok == False or self.adict.dataok == False or self.cdict.dataok == False or self.qdict.dataok == False:
			return False
		self.opened = True
		self.calcnow()
		return True

	def downloadquotes(self):
	# download quotes from the internet
		if self.opened == False:
			return True
		assetslist = []
		assets = self.getassets(GRP_ASSETS_C)
		for a in assets:
			assetslist.append(self.getassetname(a[0],ticker=True))
		base = self.getbasecurrency()
		currencylist = self.getcurrencies()
		quotes = self.online.getquotes(assetslist)
		rates = self.online.getcurrencyrates(base,currencylist)
		assetquotes = []
		for a in assets:
			aname = self.getassetname(a[0],ticker=True)
			for q in quotes:
				if q[0] == aname:
					inlist = False
					assetquotes.append([a[0],q])
					for an in self.assetnames:
						if an[0] == a[0]:
							an[1] = q[4]
							inlist = True
							break
					if inlist == False:
						self.assetnames.append([a[0],q[4]])
		for a in assetquotes:
			q = a[1]
			ditm = {}
			ditm['d'] = q[3]
			ditm['p'] = q[1]
			ditm['a'] = a[0]
			self.qdict.addtodict(ditm)
		for r in rates:
			ditm = {}
			ditm['d'] = r[3]
			ditm['c'] = r[0]
			ditm['p'] = r[1]
			self.cdict.addtodict(ditm)

	def addtransaction(self,d,fs,fq,fp,fc,ts,tq,tp,tc,de):
		if self.opened == False:
			return False
		ditm = {}
		ditm['d'] = d
		ditm['fs'] = fs
		ditm['fq'] = fq
		ditm['fp'] = fp
		ditm['fc'] = fc
		ditm['ts'] = ts
		ditm['tq'] = tq
		ditm['tp'] = tp
		ditm['tc'] = tc
		ditm['de'] = de
		return self.tdict.addtodict(ditm)

	def addasset(self,d,p,c,de,group):
		num = self.nextassetid(group)
		if num == False:
			return False
		ditm = {}
		ditm['num'] = str(num)
		ditm['de'] = de
		ditm['c'] = c
		rv = self.adict.addtodict(ditm)
		if rv == False:
			return False
		rv = self.addquote(d,p,num)
		if rv == False:
			return False
		self.calcnow()
		return num

	def addquote(self,d,p,num):
		ditm = {}
		ditm['d'] = d
		ditm['p'] = p
		ditm['a'] = str(num)
		return self.qdict.addtodict(ditm)

	def nextassetid(self,grp):
		if self.opened == False:
			return False
		spread = self.getgroupspread(grp)
		naid = spread[0]
		for a in self.adict.dictionary:
			if self.utils.isint(a['num']):
				num = int(a['num'])
				if num >= spread[0] and num <= spread[1]:
					naid = num + 1
		return naid

	def splitasset(self,d,x,y,p,num,cpy=True):
		c = self.getassetcurrency(num)
		if c == -1:
			return False
		cn = self.getcurrencies()[c]

		nam = self.getassetname(num)
		q = self.getassetbalance(num)
		g = self.getassetgroup(num)
		
		factor = float(x)/float(y)
		
		qn = float(q)*factor
		qeven = qn-round(qn)
		
		if not (self.utils.isint(d) and int(d) > 19700101 and int(d) < 21000101):
			return False
		if not (self.utils.isint(x) and self.utils.isint(y)):
			return Flase
		if not (self.utils.isfloat(p)):
			return False
		if not (qeven == 0.0 and qn > 0.0):
			return False

		pn = self.getassetapps(num) / factor

		new = self.addasset(d,p,cn,nam,g)
		if new == False:
			return False
		self.addtransaction(d,str(num),q,p,'0',str(new),str(qn),str(pn),'0','Automatic stock split')

		#print d,p,cn,g,new
		#print d,num,q,p,'0',new,qn,pn,'0'

		if cpy == True:
			fid = num
			tid = new
			fac = float(y)/float(x)
			di = 95.0/float(len(self.qdict.dictionary))
			for i,q in enumerate(self.qdict.dictionary):
				if q['a'] == fid:
					ditm = {}
					ditm['d'] = q['d']
					ditm['p'] = str(float(q['p'])*float(fac))
					ditm['a'] = str(tid)
					self.qdict.addtodict(ditm)
		
		return True
	
### --- 
 
	def dicttomat(self):
	# transform to matrices without description; transactions, currencies, accounts
		self.tdmatrix = self.utils.dictomat(self.tdict.dictionary,self.tattr[0:9])
		self.cdmatrix = self.utils.dictomat(self.cdict.dictionary,self.cattr,True)
		self.cdlist = self.utils.clist
		self.admatrix = self.utils.dictomat(self.adict.dictionary,self.aattr[0:2],True)
		self.qdmatrix = self.utils.dictomat(self.qdict.dictionary,self.qattr)
		# prepare data for matrix calculations
		# transactions set to one transaction per row vs accounts
		self.tcmatrix = self.utils.tdattocalc(self.tdmatrix,self.tattr[0:9],self.admatrix)
		# accumulative matrix 1110000 one row per month vs accounts
		self.datematrix = self.calcdatematrix()
		self.camatrix = self.calcamatrix()
		self.qamatrix = self.calcqmatrix()
		# matrix 0..1..0, one row for each currency vs accounts
		self.ccamatrix = self.calccamatrix()
		# matrix for result with currencies for months vs accounts
		self.ccmatrix = self.calccmatrix()
		return True

	def calcnow(self):
	# calculate holdings (accumulated and diff)
		if self.opened == False:
			return True
		self.dicttomat()
		# accumulated quantity row date vs accounts
		self.amatrix = dot(self.camatrix,self.tcmatrix[:,1:])
		# accumulated sum (quantity*price) row date vs accounts
		self.aqmatrix = self.amatrix*self.qamatrix
		# accumulated sum (quantity*price) in base currency row date vs accounts
		self.aqcmatrix = self.aqmatrix*self.ccmatrix
		# calculate diff matrix from result (in quantity)
		cdmatrix = self.calcdmatrix(self.amatrix)
		self.dmatrix = dot(cdmatrix,self.amatrix)
		# calculate diff sum (q*p)
		self.dqmatrix = self.dmatrix*self.qamatrix
		# calculate diff sum (q*p) in base currency
		self.dqcmatrix = self.dqmatrix*self.ccmatrix
		return True

	def calccamatrix(self):
	# create mapping matrix between currecies and accounts
		mat = zeros((self.admatrix[:,1].size))
		for i,c in enumerate(self.cdlist):
			row = array(where(self.admatrix[:,1] == i,1,0))
			mat = vstack((mat,row))
		return mat[1:,:]

	def calcqmatrix(self):
	# create quote matrix one row being month vs accounts
		cols = self.admatrix[:,0].size
		mat = zeros((1,cols))
		for d in self.datematrix[:,0]:
			row = zeros((1,cols))
			for i,a in enumerate(self.admatrix[:,0]):
				r = where((self.qdmatrix[:,1] == a) & (self.qdmatrix[:,0] <= d*100+31))
				if r[0].size != 0:
					row[0,i] = self.qdmatrix[r[0][-1],2]
			mat = vstack((mat,row))
		return mat[1:,:]

	def calccmatrix(self):
	# create a currency matrix row being month vs currencies and prices
		# depends on calcamatrix
		cols = self.admatrix[:,0].size	
		mat = zeros((1,cols))
		for d in self.datematrix[:,0]:
			row = zeros((1,cols))
			for i,c in enumerate(self.cdlist):
				r = where((self.cdmatrix[:,1] == i) & (self.cdmatrix[:,0] <= d*100+31))
				if not r[0].size == 0:
					row = row + self.cdmatrix[r[0][-1],2] * self.ccamatrix[i] 
			mat = vstack((mat,row))
		return mat[1:,:]

	def calcdatematrix(self):
	# create month matrix 
		sd = self.tcmatrix[0][0]
		sd = int(sd/100)
		sy = int(sd/100)
		sm = sd - sy*100
		md = int(max(self.tcmatrix[-1][0],self.qdmatrix[-1][0])/100)
		my = int(md/100)
		mm = md - my*100
		mat = zeros((1,1))
		while(sy*100+sm <= my*100+mm):
			row = zeros((1,1))
			row[0,0] = sy*100+sm
			mat = vstack((mat,row))
			sm = sm + 1
			if sm > 12:
				sm = 1
				sy = sy + 1
		return mat[1:,:]
	

	def calcamatrix(self):
	# create the ones/zeros matrix to calc accumulated result/month
		asize = self.tcmatrix[:,0].size
		cmat = zeros((1,asize))
		for d in self.datematrix[:,0]:
			row = array(where(self.tcmatrix[:,0] <= d*100+31,1,0))
			cmat = vstack((cmat,row)) 
		return cmat[1:,:]

	def calcdmatrix(self,rmatrix):
	# create the pseudo identity matrix to calculate the diff result
		s = rmatrix[:,0].size
		a = identity((s))
		b = identity((s+1))[:-1,1:]
		cdmatrix = a-b
		return cdmatrix

	def calcgvector(self,nmin,nmax):
	# calculate group vector to summarize
		cgvector = where((self.admatrix[:,0] >= nmin) & (self.admatrix[:,0] <= nmax),1,0)
		return cgvector

	def calcdvector(self,dmin=0,dmax=sys.maxint):
	# calculate date vector to summarize a diff matrix
		if dmax == 0: #workaround as 0 means undefined
			dmax = sys.maxint
		cdvector = where((self.datematrix[:,0] >= dmin) & (self.datematrix[:,0] <= dmax),1,0)
		return cdvector

	def calchgsum(self,gvec,diff=0,year=0):
	# calculate historical group sum of group vector, diff or no diff
		if not diff == 0:
			qcmatrix = self.dqcmatrix
		else:
			qcmatrix = self.aqcmatrix
		return dot(qcmatrix,gvec)

	def calcgsum(self,gvec,dmin=0,dmax=0,diff=0):
	# calculate group sum of group vector, from date dmin to date dmax, diff or no diff
		if diff == 0:
			mat = self.calcamdiff(self.aqcmatrix,dmin,dmax)
		else:
			mat = self.calcdmdiff(self.dqcmatrix,dmin,dmax)
		return dot(gvec,mat)

	def calcamdiff(self,mat,dmin=0,dmax=0):
	# calculate matrix row difference of whole matrix, or between different dates
		row = mat[-1,:]
		row0 = self.getmdrow(mat,dmax)
		row1 = self.getmdrow(mat,dmin,1)
		if not row0 == None:
			row = row0
		if not row1 == None:
			row = row - row1
		return row

	def calcdmdiff(self,mat,start=0,end=0):
	# summarize a diff matrix
		cdvec = self.calcdvector(start,end)
		return dot(cdvec,mat)

	def getmdrow(self,mat,dat=0,minus=0):
	# get row in matrix where date is dat, deduct 0 or 1 rows
		row = None
		if not dat == 0:
			r = where(self.datematrix[:,0] >= dat)
			if not r[0].size == 0:
				if r[0][0]-minus >= 0:
					row = mat[r[0][0]-minus,:]
				else:
					row = mat[r[0][0],:]
		return row

## ---

	def gethglvalues(self,labels,diff=0):
	# get historical sums for a list of groups (labels) with diff / no diff
		values = []
		for text in labels:
			cgvec = self.getgroupvector(text)
			values.append(self.calchgsum(cgvec,diff))
		return values


## ---

	def getassetname(self,num,ticker=False):
	# return a string with name connected to num
		if self.opened == False:
			return False
		if not self.utils.isint(num):
			return ''
		if ticker == False:
			for a in self.assetnames:
				if int(num) == int(a[0]):
					return a[1]
		num = float(num)
		id = where(self.admatrix[:,0] == num)
		if id[0].size == 0:
			return ''
		nam = self.adict.dictionary[id[0][0]]['de']
		return nam

	def getassetcurrency(self,num):
	# return share currency of share num
		if self.opened == False:
			return -1
		if not self.utils.isint(num):
			return -1
		num = int(num)
		ids = where(self.admatrix[:,0] == num)
		if len(ids) == 0:
			return -1
		if ids[0].size == 0:
			return -1
		return int(self.admatrix[:,1][ids][0])

	def getassetquotes(self,num):
	# return all quotes of share num
		if self.opened == False:
			return False
		if not self.utils.isint(num):
			return []
		num = int(num)
		ids = where(self.qdmatrix[:,1] == num)
		if len(ids) == 0:
			return []
		quotes = []
		for i in ids[0]:
			quotes.append([str(int(self.qdmatrix[i][0])),self.qdmatrix[i][2]])
		return quotes

	def getassettransactions(self,num):
	# return all asset transactions [[buy],[sell]]
		if self.opened == False:
			return False
		if not self.utils.isint(num):
			return []
		num = int(num)
		transactions = [[],[]]
		ids = where(self.tdmatrix[:,5] == num)
		if not len(ids) == 0:
			for i in ids[0]:
				td = self.tdmatrix[i]
				transactions[0].append([str(int(td[0])),td[6],td[7],td[8]])
		ids = where(self.tdmatrix[:,1] == num)
		if not len(ids) == 0:
			for i in ids[0]:
				td = self.tdmatrix[i]
				transactions[1].append([str(int(td[0])),-td[2],td[3],td[4]])
		return transactions

	def getassetapps(self,num,year=0,month=12,date=31):
	# get the average price per share
	# return average price per share / account (incl commission)
	# self.tattr = ['d','fs','fq','fp','fc','ts','tq','tp','tc','de']
		if self.opened == False:
			return False
		if not self.utils.isint(num):
			return 0.0
		ids = where(self.admatrix[:,0] == int(num))
		if len(ids) == 0:
			return 0.0
		if ids[0].size == 0:
			return 0.0
		#print array(where(self.tcmatrix[:,id[0][0]+1] != 0,1,0))
		date0 = 0
		if not year == 0:
			date0 = year*10000+month*100+date
		if not date0 == 0:
			trn = where(self.tcmatrix[:,0] <= date0,1,0)
			trn0 = compress(trn,self.tcmatrix,axis=0)
			trn = where(self.tdmatrix[:,0] <= date0,1,0)
			trn1 = compress(trn,self.tdmatrix,axis=0)
		else:
			trn0 = self.tcmatrix
			trn1 = self.tdmatrix
		tr = where(trn0[:,ids[0][0]+1] != 0)
		if tr[0].size == 0:
			return 0.0
		apps = 0
		quan = 0
		for t in tr[0]:
			#print 'share',id[0][0],'change',self.tcmatrix[t,id[0][0]+1]
			qua = trn0[t,ids[0][0]+1]
			row = trn1[t,:]
			if qua > 0:
				pri = row[7]
				com = row[8]
				apps = (apps * quan + pri * qua + com) / (quan + qua)
			elif qua < 0:
				pri = row[3]
				com = row[4]
			else:
				continue
			quan = quan + qua
		#print 'Avg Price Per Share',self.accname(num),apps,'(',quan,')'
		#print 'share',id[0][0],'change',self.tcmatrix[t,id[0][0]+1]
		return apps


	def getbasecurrency(self):
	# get the project's base currency (i.e. value == 1)
		if self.opened == False:
			return False
		base = where(self.cdmatrix[:,2] == 1.0)
		if not base[0].size > 0:
			return ''
		cnam = self.cdlist[base[0][0]]
		return cnam

	def getcurrencies(self):
		clist = self.cdlist
		return clist

## ---

	def getgroupfactor(self,group):
	# get factor of one group by name
		factor = 0
		for og in core.GROUPS:
			if og[0] == group:
				factor = og[2]
				break
			for ig in og[3]:
				if ig[0] == group:
					factor = og[2]
			if not factor == 0:
				break
		return factor

	def getgroupspread(self,group):
	# get group spread by name
		spread = [0,0]
		for og in core.GROUPS:
			if og[0] == group:
				spread = og[1]
				break
			for ig in og[3]:
				if ig[0] == group:
					spread = ig[1]
			if not spread == [0,0]:
				break
		return spread

	def getgroupvector(self,group):
	# get vector for one group by name
		spread = self.getgroupspread(group)
		factor = self.getgroupfactor(group)
		gvec = self.calcgvector(spread[0],spread[1])
		gvec = gvec * factor
		return gvec

	def getaccountvector(self,aid):
	# get the vector for a single account
		if not self.utils.isint(aid):
			return False
		factor = 1.0 # calculate?
		gvec = self.calcgvector(int(aid),int(aid))
		gvec = gvec * factor
		return gvec

	def getgrouplist(self,group):
	# get a list of all sub-groups, or if group is a sub-group, return itself as a list
	# if no match, return empty list
		for og in core.GROUPS:
			if og[0] == group:
				igs = []
				for ig in og[3]:
					igs.append(ig[0])
				return igs
			for ig in og[3]:
				if ig[0] == group:
					return [group]
		return []
## ---

	def getgroupname(self,group):
		return group

	def getgroup(self,group):
	# get group
		cgvec = self.getgroupvector(group)
		ds = self.utils.calcdates(0,0)
		sum = self.calcgsum(cgvec,ds[0],ds[1],diff)
		return sum

	def getassetbalance(self,aid): 
	# get account holdings for a single account
		if not self.utils.isint(aid):
			return -1
		amatrix = self.calcamdiff(self.amatrix)
		gvec = self.getaccountvector(aid)
		return dot(amatrix,gvec)

	def getassetgroup(self,aid):
	# get which group an asset is part of
		group = False
		if self.opened == False:
			return False
		if not self.utils.isint(aid) == True:
			return False
		for g0 in core.GROUPS:
			if g0[1][0] < int(aid) and g0[1][1] > int(aid):
				for g1 in g0[3]:
					if g1[1][0] < int(aid) and g1[1][1] > int(aid):
						return g1[0]
		return False

	def getassets(self,group,diff=False,all=False,year=0,month=0,year1=0,month1=0,acid=0):
	# get assets
		if self.opened == False:
			return False
		cgvec = self.getgroupvector(group)
		ds = self.utils.calcdates(year,month,year1,month1)
		amatrix = self.calcamdiff(self.amatrix,ds[0],ds[1])
		if diff == False:
			aqcmatrix = self.calcamdiff(self.aqcmatrix,ds[0],ds[1])
		else:
			aqcmatrix = self.calcdmdiff(self.dqcmatrix,ds[0],ds[1])
		qamatrix = self.calcamdiff(self.qamatrix)
		assets = []
		for i,v in enumerate(amatrix):
			if cgvec[i] == 0:
				continue
			if all == False and amatrix[i] == 0:
				continue
			if all == False and aqcmatrix[i] == 0:
				continue
			acid = self.admatrix[i][0]
			cid = self.getassetcurrency(self.admatrix[i][0])
			cnam = self.cdlist[cid]
			assets.append([str(int(acid)),self.utils.rstr(amatrix[i]*cgvec[i],2),self.utils.rstr(qamatrix[i],2),cnam,self.utils.rstr(aqcmatrix[i]*cgvec[i])])
		return assets

	def getassetgroups(self,group,diff=False,all=False,year=0,month=0,year1=0,month1=0,acid=0):
	# get asset groups
		if self.opened == False:
			return False
		grplist = self.getgrouplist(group)
		ds = self.utils.calcdates(year,month,year1,month1)
		amatrix = self.calcamdiff(self.amatrix,ds[0],ds[1])
		if diff == False:
			aqcmatrix = self.calcamdiff(self.aqcmatrix,ds[0],ds[1])
		else:
			aqcmatrix = self.calcdmdiff(self.dqcmatrix,ds[0],ds[1])
		qamatrix = self.calcamdiff(self.qamatrix)
		base = self.getbasecurrency()
		assets = []
		for g in grplist:
			cgvec = self.getgroupvector(g)
			gsum = 0.0
			for i,v in enumerate(amatrix):
				if cgvec[i] == 0:
					continue
				if all == False and amatrix[i] == 0:
					continue
				if all == False and aqcmatrix[i] == 0:
					continue
				gsum = float(aqcmatrix[i]*cgvec[i]) + gsum
			assets.append([str(g),'','',base,self.utils.rstr(gsum)])
		return assets
		
	def getassetshistory(self,columns,diff=False):
	# get historical assets list for a list of groups (columns)
		if self.opened == False:
			return False
		if diff == False:
			vtmp = self.gethglvalues(columns,0)
		else:
			vtmp = self.gethglvalues(columns,1)
		vcal = len(columns) * [0.0]
		vals = []
		for i,val in enumerate(vtmp[0]):
			vrow = []
			datm = str(int(self.datematrix[i][0]))
			vrow.append(datm)
			for j in range(len(columns)):
				vcal[j] = vcal[j] + float(vtmp[j][i])
				vrow.append(self.utils.rstr(vcal[j]))
				vcal[j] = 0.0
			vals.append(vrow)
		values = vals
		return values

	def getdatelist(self):
		return self.datematrix[:,0]

	def getbudget(self):
		dat = []
		labls = []
		vals = []
		for i,l in enumerate(core.BUDGET[0][1]):
			if l == 0:
				continue
			vals.append(l)
			labls.append(core.GROUPS[1][3][i][0])
		dat.append(labls)
		dat.append(vals)
		sav = 1.0
		for d in dat[1]:
			sav = sav - d
		dat[0].append('Savings')
		dat[1].append(sav)
		return dat

## ---

	ALLOWEDCURRENCIES = ['EUR','USD','JPY','BGN','CZK','DKK','EEK','GBP','HUF','LTL','LVL','PLN','RON','SEK','CHF','NOK','HRK','RUB','TRY','AUD','BRL','CAD','CNY','HKD','IDR','INR','KRW','MXN','MYR','NZD','PHP','SGD','THB','ZAR']

	global INFO
	
	INFO = ['Frugal Finance','1.0b2','Copyright (c) 2006-2010 Thomas Larsson','Thomas Larsson','http://www.samoht.se/frugal']

	global GRP_REVENUES; GRP_REVENUES = 'Revenues'
	global GRP_EXPENSES; GRP_EXPENSES = 'Expenses'
	global GRP_ASSETS_C; GRP_ASSETS_C = 'Current assets'
	global GRP_ASSETS_NC; GRP_ASSETS_NC = 'Non-current assets'
	global GRP_LIABILITIES_C; GRP_LIABILITIES_C = 'Current liabilities'
	global GRP_LIABILITIES_NC; GRP_LIABILITIES_NC = 'Non-current liabilities'

	BUDGET = [
		[GRP_EXPENSES,
			[0.3,0.1,0.05,0.1,0.1,0.05,0.0,0.0,0.0,0.1]
		]
	]

	GROUPS = [
		[GRP_REVENUES,[10000,19999],-1,
			[
			['Salary',      [10000,10999]],
			['Interest',    [11000,11999]],
			['Dividend',    [12000,12999]],
			['Income from Business', [13000,13999]],
			['Social Security', [14000,14999]],
			['Incoming Transfers', [15000,15999]],
			['Other income',[19000,19999]]
			],
		],
		[GRP_EXPENSES,[20000,29999],1,
			[
			['Living Costs',  [20000,20999]],				# 30%
			['Food',          [21000,21999]],				# 10% 
			['Clothes',       [22000,22999]],				# 5%
			['Automobile/Transportation',[23000,23999]],	# 10%
			['Holidays',      [24000,24999]],				# 10%
			['Entertainment', [25000,25999]],				# 5%
			['Memberships',   [26000,26999]],				# 0%
			['Medical Costs', [27000,27999]],				# 0%
			['Outgoing Transfers',[28000,28999]],			# 0
			['Other expenses',[29000,29999]]				# 5%
			]												# savings 20%
		],
		[GRP_ASSETS_C,[30000,35999],1,
			[
			['Accounts',      [30000,30999]],
			['Stocks',        [31000,31999]],
			['Mutual funds',  [32000,32999]],
			['Bonds',         [33000,33999]],
			['Derivates',     [34000,34999]],
			['Other current assets',[35000,35999]]
			]
		],
		[GRP_ASSETS_NC,[36000,39999],1,
			[
			['Houses',[37000,37999]],
			['Cars',[38000,38999]],
			['Other non-current assets',[39000,39999]]
			]
		],
		[GRP_LIABILITIES_C,[40000,42999],-1,
			[
			['Current bank loans',[40000,40999]],
			['Other current liabilities',[42000,42999]],
			]
		],
		[GRP_LIABILITIES_NC,[43000,49999],-1,
			[
			['Non-current bank loans',[43000,43999]],
			['Other non-current liabilities',[49000,49999]]
			]
		],
		['Index',[50000,51000],0,
			[
			['Indices',[50000,51000]]
			]
		]
		] # END GROUPS

	ACCOUNTS_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<accounts>\n<account num=\"10000\" c=\"CURRENCY\" de=\"Salary\"/><account num=\"11000\" c=\"CURRENCY\" de=\"Interest\"/>\n<account num=\"12000\" c=\"CURRENCY\" de=\"Dividend\"/>\n<account num=\"13000\" c=\"CURRENCY\" de=\"Income from Business\"/>\n<account num=\"14000\" c=\"CURRENCY\" de=\"Social Security\"/>\n<account num=\"15000\" c=\"CURRENCY\" de=\"Incoming Transfers\"/>\n<account num=\"19000\" c=\"CURRENCY\" de=\"Other income\"/>\n<account num=\"20000\" c=\"CURRENCY\" de=\"Living Costs\"/>\n<account num=\"21000\" c=\"CURRENCY\" de=\"Food\"/>\n<account num=\"22000\" c=\"CURRENCY\" de=\"Clothes\"/>\n<account num=\"23000\" c=\"CURRENCY\" de=\"Automobile/Transportation\"/>\n<account num=\"24000\" c=\"CURRENCY\" de=\"Holidays\"/>\n<account num=\"25000\" c=\"CURRENCY\" de=\"Entertainment\"/>\n<account num=\"26000\" c=\"CURRENCY\" de=\"Memberships\"/>\n<account num=\"27000\" c=\"CURRENCY\" de=\"Medical Costs\"/>\n<account num=\"28000\" c=\"CURRENCY\" de=\"Outgoing Transfers\"/>\n<account num=\"29000\" c=\"CURRENCY\" de=\"Other costs\"/>\n</accounts>"
	CURRENCIES_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<currencies>\n<price d=\"1970-01-01\" c=\"CURRENCY\" p=\"1\"/>\n</currencies>"
	QUOTES_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<quotes>\n<quote d=\"1970-01-01\" a=\"10000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"11000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"12000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"19000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"20000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"21000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"22000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"23000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"24000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"25000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"29000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"30000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"30001\" p=\"1\"/>\n</quotes>"
	TRANSACTIONS_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<transactions>\n<item d=\"DATE\" fs=\"0\" fq=\"0\" fp=\"1\" fc=\"0\" ts=\"0\" tq=\"0\" tp=\"1\" tc=\"0\" de=\"initial transaction\"/>\n</transactions>"
