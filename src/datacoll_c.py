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

import os
import sys
import re
import socket
import urllib2
import json
from datetime import date,datetime,timedelta
import requests
from user_agent import generate_user_agent

from numpy import *
from numpy import array as nparray

from datautils_c import datautils_c
from datafile_c import datafile_c
from plugin_c import plugin_c

class datacoll_c:
	def __init__(self):
	# initialization function
		self.unsaved = 0
		self.datautils = datautils_c()
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

	def newfiles(self,dir,currency='EUR'):
	# create new files based on currency currency
		if not os.path.exists(dir):
			return False
		tfile = dir+'/'+self.tfile
		afile = dir+'/'+self.afile
		cfile = dir+'/'+self.cfile
		qfile = dir+'/'+self.qfile
		if os.path.exists(tfile) or os.path.exists(afile) or os.path.exists(cfile) or os.path.exists(qfile):
			return False
		todaysdate = date.today().strftime('%Y-%m-%d')
		filedata = re.sub('CURRENCY',currency,datacoll_c.TRANSACTIONS_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(tfile,'w')
		f.write(filedata)
		f.close()
		filedata = re.sub('CURRENCY',currency,datacoll_c.ACCOUNTS_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(afile,'w')
		f.write(filedata)
		f.close()
		filedata = re.sub('CURRENCY',currency,datacoll_c.CURRENCIES_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(cfile,'w')
		f.write(filedata)
		f.close()
		filedata = re.sub('CURRENCY',currency,datacoll_c.QUOTES_XML)
		filedata = re.sub('DATE',todaysdate,filedata)
		f = open(qfile,'w')
		f.write(filedata)
		f.close()
		return True

	def savefiles(self,pd=False):
	# save all opened files
		if not pd == False:
			pd.Update(20,'Saving transaction data..')
		if not self.tdict.writetofile() == True:
			return False
		if not pd == False:
			pd.Update(40,'Saving account data..')
		if not self.adict.writetofile() == True:
			return False
		if not pd == False:
			pd.Update(60,'Saving currency data..')
		if not self.cdict.writetofile() == True:
			return False
		if not pd == False:
			pd.Update(80,'Saving price data..')
		if not self.qdict.writetofile() == True:
			return False
		self.unsaved = 0
		if not pd == False:
			pd.Update(95,'Data files saved.')
		return True

	def openfiles(self,dir,pd=False):
	# open project files in dir
		if not os.path.exists(dir):
			return False
		# load dictionaries, sort dates
		if not pd == False:
			pd.Update(20,'Reading transaction data..')
                self.tdict = datafile_c(self,dir+'/'+self.tfile,self.ttags[0],self.ttags[1],self.tattr,True)
		if not pd == False:
			pd.Update(40,'Reading account data..')
                self.adict = datafile_c(self,dir+'/'+self.afile,self.atags[0],self.atags[1],self.aattr)
		if not pd == False:
			pd.Update(60,'Reading currency data..')
		self.cdict = datafile_c(self,dir+'/'+self.cfile,self.ctags[0],self.ctags[1],self.cattr,True)
		if not pd == False:
			pd.Update(80,'Reading price data..')
		self.qdict = datafile_c(self,dir+'/'+self.qfile,self.qtags[0],self.qtags[1],self.qattr,True)
		# check files
		if self.tdict.dataok == False or self.adict.dataok == False or self.cdict.dataok == False or self.qdict.dataok == False:
			return False
		if not pd == False:
			pd.Update(95,'Opened all files OK.')
		return self.dicttomat(pd)

	def dicttomat(self,pd=False):
	# transform to matrices without description; transactions, currencies, accounts
		if not pd == False:
			pd.Update(10,'Transforming matrices..')
		self.tdmatrix = self.datautils.dictomat(self.tdict.dictionary,self.tattr[0:9])
		self.cdmatrix = self.datautils.dictomat(self.cdict.dictionary,self.cattr,True)
		self.cdlist = self.datautils.clist
		self.admatrix = self.datautils.dictomat(self.adict.dictionary,self.aattr[0:2],True)
		self.qdmatrix = self.datautils.dictomat(self.qdict.dictionary,self.qattr)
		# prepare data for matrix calculations
		# transactions set to one transaction per row vs accounts
		if not pd == False:
			pd.Update(20,'Preparing transactions.. Please wait.')
		#self.tcmatrix = self.datautils.tdattocalc(self.tdmatrix,self.tattr[0:9],self.admatrix,False)
                self.tcmatrix = self.datautils.tdattocalc(self.tdmatrix,self.tattr[0:9],self.admatrix)
		# accumulative matrix 1110000 one row per month vs accounts
		if not pd == False:
			pd.Update(60,'Preparing matrices..')
		self.datematrix = self.calcdatematrix()
		if not pd == False:
			pd.Update(75)
		self.camatrix = self.calcamatrix()
		if not pd == False:
			pd.Update(80)
		self.qamatrix = self.calcqmatrix()
		if not pd == False:
			pd.Update(75)
		# matrix 0..1..0, one row for each currency vs accounts
		if not pd == False:
			pd.Update(85,'Preparing account matrix..')
		self.ccamatrix = self.calccamatrix()
		# matrix for result with currencies for months vs accounts
		if not pd == False:
			pd.Update(90,'Calculating result matrix..')
		self.ccmatrix = self.calccmatrix()
		if not pd == False:
			pd.Update(95,'Done.')
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

	def getaccountvector(self,aid):
	# get the vector for a single account
		if not self.datautils.isint(aid):
			return False
		factor = 1.0 # calculate?
		gvec = self.calcgvector(int(aid),int(aid))
		gvec = gvec * factor
		return gvec

	def getgroupvector(self,group):
	# get vector for one group by name
		spread = self.getgroupspread(group)
		factor = self.getgroupfactor(group)
		gvec = self.calcgvector(spread[0],spread[1])
		gvec = gvec * factor
		return gvec

	def getgroupsum(self,group,yfrom=0,yto=0,diff=0):
	# get total sum for one group from and to year (diff or no diff) by name
		cgvec = self.getgroupvector(group)
		ds = self.datautils.calcdates(yfrom,yto)
		sum = self.calcgsum(cgvec,ds[0],ds[1],diff)
		return sum

	def getallgrouplabels(self):
	# get list of all sub-group labels
		labels = []
		for og in datacoll_c.GROUPS:
			for ig in og[3]:
				labels.append(ig[0])
		return labels

	def getgrouplabels(self,group):
	# get list of all sub-group labels in one major group (or return group) by name
		labels = []
		for og in datacoll_c.GROUPS:
			if og[0] == group:
				for ig in og[3]:
					labels.append(ig[0])
		if labels == []:
			labels.append(group)
		return labels

	def getgroupfactor(self,group):
	# get factor of one group by name
		factor = 0
		for og in datacoll_c.GROUPS:
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
		for og in datacoll_c.GROUPS:
			if og[0] == group:
				spread = og[1]
				break
			for ig in og[3]:
				if ig[0] == group:
					spread = ig[1]
			if not spread == [0,0]:
				break
		return spread

	def getaccbalance(self,aid): #TODO getgroupvector, getassetvector
	# get account holdings for a single account
		if not self.datautils.isint(aid):
			return -1
		amatrix = self.calcamdiff(self.amatrix)
		gvec = self.getaccountvector(aid)
		return dot(amatrix,gvec)

	def getdassets(self,group,yfrom=0,yto=0,diff=0,mini=0,all=0,basecurrency=1,totsum=1,yoy=0,apps=0):
	# get detailed asset list from year to year (diff/no diff) of one group by name (mini=1 name only, =2 name and aid) yoy = quote diff 3,6,12 mo apps = avg price per sh,
		cgvec = self.getgroupvector(group)
		ds = self.datautils.calcdates(yfrom,yto)
		if basecurrency == 1:
			base = ' '+self.getbasecurrency()
		else:
			base = ''
		amatrix = self.calcamdiff(self.amatrix,ds[0],ds[1])
		if diff == 0:
			aqcmatrix = self.calcamdiff(self.aqcmatrix,ds[0],ds[1])
		else:
			aqcmatrix = self.calcdmdiff(self.dqcmatrix,ds[0],ds[1])
		qamatrix = self.calcamdiff(self.qamatrix)
		assets = []
		sum = 0
		for i,v in enumerate(amatrix):
			if cgvec[i] == 0:
				continue
			if round(amatrix[i])*cgvec[i] == 0 and all == 0:
				continue
			if aqcmatrix[i] == 0:
				continue
			acid = self.admatrix[i][0]
			nam = self.accname(acid)
			if mini == 0:
				cid = self.acccurrency(self.admatrix[i][0])
				cnam = self.cdlist[cid]
				sum = sum + aqcmatrix[i]*cgvec[i]
				asset = []
				asset.extend([nam,self.datautils.rstr(amatrix[i]*cgvec[i],2),self.datautils.rstr(qamatrix[i],2)+' '+cnam,self.datautils.rstr(aqcmatrix[i]*cgvec[i])+base])
				if yoy == 1:
					today = datetime.today()
					mo12 = today - timedelta(days=365)
					mo12 = mo12.strftime('%Y%m%d')
					mo6 = today - timedelta(days=182)
					mo6 = mo6.strftime('%Y%m%d')
					mo3 = today - timedelta(days=91)
					mo3 = mo3.strftime('%Y%m%d')
					aid = str(int(acid))
					q0 = float(self.getlatestquote(aid)[1])
					q12 = float(self.getdatequote(mo12,aid)[1])
					q6 = float(self.getdatequote(mo6,aid)[1])
					q3 = float(self.getdatequote(mo3,aid)[1])
					if not float(q3) == float(0):
						asset.extend([self.datautils.rstr(100*(q0-q3)/q3,2)+'%'])
					else:
						asset.extend(['-'])
					if not float(q6) == float(0):
						asset.extend([self.datautils.rstr(100*(q3-q6)/q6,2)+'%'])
					else:
						asset.extend(['-'])
					if not float(q12) == float(0):
						asset.extend([self.datautils.rstr(100*(q6-q12)/q12,2)+'%'])
					else:
						asset.extend(['-'])
				if apps == 1:
					avg = self.getapps(acid,year=yto)
					pro = 100*(qamatrix[i]-avg)/avg
					asset.extend([self.datautils.rstr(avg,2)+' '+cnam,self.datautils.rstr(pro,2)+'%'])
				assets.append(asset)
			elif mini == 1:
				assets.append([nam])
			else:
				assets.append([nam,str(int(acid))])
		if mini == 0 and totsum == 1:
			assets.append(['Total '+group.title(),'','',self.datautils.rstr(sum,0)+base])
		return assets

	def getdglvalues(self,labels,yfrom=0,yto=0,diff=0):
	# get group sum list for a list of groups (labels) from year to year (diff / no diff)
		values = []
		for l in labels:
			values.append(self.datautils.rstr(self.getgroupsum(l,yfrom,yto,diff),2))
		return values

	def gethglvalues(self,labels,diff=0):
	# get historical sums for a list of groups (labels) with diff / no diff
		values = []
		for text in labels:
			cgvec = self.getgroupvector(text)
			values.append(self.calchgsum(cgvec,diff))
		return values

	def gethassets(self,columns,diff=0,year=0):
	# get historical assets list for a list of groups (columns)
		vtmp = self.gethglvalues(columns,diff)
		vcal = len(columns) * [0.0]
		vals = []
		for i,val in enumerate(vtmp[0]):
			vrow = []
			datm = str(int(self.datematrix[i][0]))
			if year == 0 or (i == 0 and diff == 0) or (year == 1 and int(datm[4:6]) == 12) or i == len(vtmp[0])-1:
				vrow.append(datm)
				for j in range(len(columns)):
					vcal[j] = vcal[j] + float(vtmp[j][i])
					vrow.append(self.datautils.rstr(vcal[j]))
					vcal[j] = 0.0
				vals.append(vrow)
			elif diff == 1:
				for j in range(len(columns)):
					vcal[j] = vcal[j] + float(vtmp[j][i])
		columns.insert(0,'Date')
		values = vals
		return values

	def accnum(self,nam):
	# return id of share name (careful, if two accounts have same name..)
		for acc in self.adict.dictionary:
			if acc['de'] == nam:
				return acc['num']
		return '0'

	def accname(self,num):
	# return name of share num
		if not self.datautils.isfloat(num):
			return ''
		num = float(num)
		id = where(self.admatrix[:,0] == num)
		if id[0].size == 0:
			return ''
		nam = self.adict.dictionary[id[0][0]]['de']
		for a in self.anams:
			if a[0] == nam:
				return a[1]
		return nam

	def accticker(self,num):
	# return ticker of share num
		if not self.datautils.isfloat(num):
			return ''
		num = float(num)
		id = where(self.admatrix[:,0] == num)
		if id[0].size == 0:
			return ''
		nam = self.adict.dictionary[id[0][0]]['de']
		return nam

	def accgroup(self,num):
	# return group of share num
		group = ''
		for og in datacoll_c.GROUPS:
			for ig in og[3]:
				if int(ig[1][0]) <= int(num) and int(num) <= int(ig[1][1]):
					group = ig[0]
			if not group == '':
				break
		return group

	def accisgroup(self,num,group):
	# return true or false if share num is in group group
		for og in datacoll_c.GROUPS:
			if og[0] == group:
				if int(og[1][0]) <= int(num) and int(num) <= int(og[1][1]):
					return True
				else:
					return False
			for ig in og[3]:
				if int(ig[1][0]) <= int(num) and int(num) <= int(ig[1][1]):
					if group == ig[0]:
						return True
					else:
						return False
		return False

	def naccid(self,grp):
	# return next share num of group grp
		datautil = self.datautils
		spread = self.getgroupspread(grp)
		naid = spread[0]
		for a in self.adict.dictionary:
			if datautil.isint(a['num']):
				num = int(a['num'])
				if num >= spread[0] and num <= spread[1]:
					naid = num + 1
		return naid

	def acccurrency(self,num):
	# return share currency of share num
		du = self.datautils
		if not du.isint(num):
			return -1
		num = int(num)
		ids = where(self.admatrix[:,0] == num)
		if len(ids) == 0:
			return -1
		if ids[0].size == 0:
			return -1
		return int(self.admatrix[:,1][ids][0])

	def currencyname(self,num):
	# return currency name
		du = self.datautils
		if not du.isint(num):
			return -1
		if int(num) < 0 and int(num) > len(self.cdlist):
			return ''
		return self.cdlist[int(num)]

	def accissamecurrency(self,num1,num2):
	# return true or false whether share num1 and share num2 are of same currency
		c1 = self.acccurrency(num1)
		c2 = self.acccurrency(num2)
		if not c1 == c2:
			return False
		return True

	def getdtransactionhist(self,group,yfrom=0,yto=0,trtype='sell'):
	# return a detailed list of transactions between yfrom and yto trtype=0 (sell) =1 (buy)
	# TODO Not fixed column for fs and ts
		cgvec = self.getgroupvector(group)
		ds = self.datautils.calcdates(yfrom,yto) # yfrom01 yto12
		ds[0] = ds[0]*100+1
		ds[1] = ds[1]*100+31
		#ids = where((self.tcmatrix[:,0] >= ds[0]) & (self.tcmatrix[:,0] <= ds[1]),1,0)
		ids = where((self.tdmatrix[:,0] >= ds[0]) & (self.tdmatrix[:,0] <= ds[1]),1,0)
		trn = compress(ids,self.tdmatrix,axis=0)
		act = compress(cgvec,self.admatrix,axis=0)
		#cgvec = insert(cgvec,0,1)
		#trn = compress(cgvec,trn,axis=1)
		# trn date + accounts xaxis, transactions yaxis
		# act accounts and currencies xaxis, nums yaxis
		#ids = where(trn[:,1:] == 0,1,0)
		#ids = dot(ids,ones([ids.shape[1],1])).transpose()[0]
		#trn = compress(ids,trn,axis=0)
		#
		#self.tattr = ['d','fs','fq','fp','fc','ts','tq','tp','tc','de']
		transactions = []
		if trtype == 'sell':
			col = 1
		else:
			col = 5
		for a in act[:,0]:
			ids = where(trn[:,col] == int(a),1,0)
			if len(ids) == 0:
				continue
			if ids[0].size == 0:
				continue
			tmp = compress(ids,trn,axis=0)
			nam = self.accname(a)
			cur = self.acccurrency(a)
			cur0 = self.cdlist[cur]
			for t in tmp:
				#print t
				pro0 = ''
				pro1 = ''
				dat = t[0]
				qua = t[col+1]
				pri = t[col+2]
				priqua = pri*qua
				apps = self.getapps(a,date=dat)
				if trtype == 'sell':
					com = t[8]
					cur = self.acccurrency(t[5])
					cur1 = self.cdlist[cur]
					appsqua = apps*qua
					print str(int(dat)),nam,self.datautils.rstr(qua,1),cur0,round(appsqua),round(com),round(appsqua+com)
					if not appsqua == 0 and cur0 == cur1:
						pro0 = self.datautils.rstr(priqua-appsqua-com,2)+' '+cur0
						pro1 = self.datautils.rstr(100*(priqua-appsqua-com)/appsqua,2)+' %'
					else:
						pro0 = self.datautils.rstr(priqua-appsqua,2)+' '+cur0+'*'
						pro1 = self.datautils.rstr(100*(priqua-appsqua)/appsqua,2)+' %*'
				elif trtype == 'buy':
					com = t[4]
					cur = self.acccurrency(t[1])
					cur1 = self.cdlist[cur]
					pro0 = self.datautils.rstr(apps,2)+' '+cur0
				else:
					com = 0.0
					cur1 = ''
				if cur0 == cur1:
					trsum = self.datautils.rstr(priqua+com,0)+' '+cur0
				else:
					trsum = self.datautils.rstr(priqua,0)+' '+cur0+'*'
				transactions.append([str(int(dat)),nam,self.datautils.rstr(qua,1),self.datautils.rstr(pri,2)+' '+cur0,self.datautils.rstr(com,2)+' '+cur1,trsum,pro0,pro1])
		#print trn
		#trn = compress(,trn,axis=0)
		return transactions

	def getapps(self,num,year=0,date=0):
	# return average price per share / account (incl commission)
	# self.tattr = ['d','fs','fq','fp','fc','ts','tq','tp','tc','de']
	# TODO add year!!!
		ids = where(self.admatrix[:,0] == int(num))
		if len(ids) == 0:
			return 0.0
		if ids[0].size == 0:
			return 0.0
		#print array(where(self.tcmatrix[:,id[0][0]+1] != 0,1,0))
		if not year == 0:
			date = year*10000+1231
		if not date == 0:
			trn = where(self.tcmatrix[:,0] <= date,1,0)
			trn0 = compress(trn,self.tcmatrix,axis=0)
			trn = where(self.tdmatrix[:,0] <= date,1,0)
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

	def calcnow(self,pd=False):
	# calculate holdings (accumulated and diff)
		# accumulated quantity row date vs accounts
		if not pd == False:
			pd.Update(10,'Calculating accumulative matrix..')
		self.amatrix = dot(self.camatrix,self.tcmatrix[:,1:])
		# accumulated sum (quantity*price) row date vs accounts
		if not pd == False:
			pd.Update(20,'Calculating quote matrix..')
		self.aqmatrix = self.amatrix*self.qamatrix
		# accumulated sum (quantity*price) in base currency row date vs accounts
		if not pd == False:
			pd.Update(40,'Calculating base currency matrix..')
		self.aqcmatrix = self.aqmatrix*self.ccmatrix
		# calculate diff matrix from result (in quantity)
		if not pd == False:
			pd.Update(60,'Calculating diff matrix..')
		cdmatrix = self.calcdmatrix(self.amatrix)
		if not pd == False:
			pd.Update(70,'Calculating diff matrix..')
		self.dmatrix = dot(cdmatrix,self.amatrix)
		# calculate diff sum (q*p)
		if not pd == False:
			pd.Update(80,'Calculating diff sum matrix..')
		self.dqmatrix = self.dmatrix*self.qamatrix
		# calculate diff sum (q*p) in base currency
		if not pd == False:
			pd.Update(90,'Calculating base currency matrix..')
		self.dqcmatrix = self.dqmatrix*self.ccmatrix
		if not pd == False:
			pd.Update(95,'Calculating base currency matrix..')

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
		if type(row0) != str:
			row = row0
		if type(row1) != str:
			row = row - row1
		return row

	def getmdrow(self,mat,dat=0,minus=0):
	# get row in matrix where date is dat, deduct 0 or 1 rows
		row = ''
		if not dat == 0:
			r = where(self.datematrix[:,0] >= dat)
			if not r[0].size == 0:
				if r[0][0]-minus >= 0:
					row = mat[r[0][0]-minus,:]
				else:
					row = mat[r[0][0],:]
		return row

	def getbasecurrency(self):
	# get the project's base currency (i.e. value == 1)
		base = where(self.cdmatrix[:,2] == 1.0)
		if not base[0].size > 0:
			return ''
		return self.cdlist[base[0][0]]

	def getcurrencies(self):
	# get a list of the project's currencies
		de = []
		for c in self.cdict.dictionary:
			de.append(c['c'])
		currencies = list(set(de))
		return currencies

	def copyquotes(self,fromid,toid,factor,pd=False):
		if not (self.datautils.isint(fromid) and self.datautils.isint(toid) and self.datautils.isfloat(factor)):
			return False
		di = 95.0/float(len(self.qdict.dictionary))
		for i,q in enumerate(self.qdict.dictionary):
			if q['a'] == fromid:
				ditm = {}
				ditm['d'] = q['d']
				ditm['p'] = str(float(q['p'])*float(factor))
				ditm['a'] = str(toid)
				#print ditm
				self.qdict.addtodict(ditm)
			if not pd == False:
				pd.Update(int(float(i)*di),'Copying and adjusting quotes..')
		return True

	def getlatestquote(self,aid=0):
	# get a list of date and latest quote of account id aid
		latest = ['0','0']
		if aid == 0:
			return latest
		for q in self.qdict.dictionary:
			if q['a'] == aid:
				latest = [q['d'],q['p']]
		return latest

	def getdatequote(self,date=0,aid=0):
	# get a list of date and latest quote of account id aid
	# of quote before or on date
		quote = ['0','0']
		if aid == 0 or date == 0:
			return quote
		for q in self.qdict.dictionary:
			if q['a'] == aid:
				if int(q['d']) <= int(date) and int(q['d']) > int(quote[0]):
					quote = [q['d'],q['p']]
		return quote

	def getlatestrate(self,cur=''):
	# get a list of date and latest rate of currency cur
		latest = ['0','0']
		if cur == '':
			return latest
		for r in self.cdict.dictionary:
			if r['c'] == cur:
				latest = [r['d'],r['p']]
		return latest

	def calcdmdiff(self,mat,start=0,end=0):
	# summarize a diff matrix
		cdvec = self.calcdvector(start,end)
		return dot(cdvec,mat)

	def getonlinequote(self,symbol):
	# get latest quote
		if self.datautils.ismorn(symbol):
			return self.getmorningstarquote(symbol)
		elif self.datautils.isbloom(symbol):
			return self.getbloombergquote(symbol)
		return self.getyahooquote(symbol)

	def getbloombergquote(self,symbol):
		blmlist = self.getbloombergquotes(pd=False,shares=[symbol])
		if not len(blmlist) == 0:
			return blmlist[0][1]
		return '0.0'


	def getbloombergquotes(self,pd=False,shares=[]):
	# get latest share quotes of list shares from bloomberg
		groups = self.getgrouplabels(self.GROUPS[2][0])
		shareurl = ''
		shareids = []
		sharenams = []
		bloomshares = []
		quotes = {}
		if not pd == False:
			pd.Update(10,'Preparing shares..')
		if shares == []:
			autoupd = True
			for g in groups:
				assets = self.getdassets(g,mini=2)
				for a in assets:
					shares.append(a[0])
					shareids.append(a[1])
		else:
			autoupd = False
		shtmp = []
		if autoupd == True:
			for i,s in enumerate(shares):
				if not pd == False:
					pd.Update(10)
				if not self.datautils.isbloom(s):
					continue
				shtmp.append([s,shareids[i]])
		else:
			shtmp = [shares]
		socket.setdefaulttimeout(10)
		delta = 0
		if len(shtmp) > 0:
			delta = 75/len(shtmp)
		for i,symbol in enumerate(shtmp):
			ticker = symbol[0].split()[0]
			ticker_key = str(ticker)
			ticker_key = ticker_key.translate(None, ':')
			if ticker_key in quotes.keys():
				#symbol = quotes[ticker_key]['symbol']
				nav = quotes[ticker_key]['nav']
				nam = quotes[ticker_key]['nam']
				dat = quotes[ticker_key]['dat']
				print symbol,nav,nam,dat
				sharenams.append([symbol[0],nam])
				mosdate = datetime.strptime(dat,'%m/%d/%Y')
				if autoupd == True:
					ditm = {}
					ditm['d'] = mosdate.strftime('%Y%m%d')
					ditm['p'] = nav
					ditm['a'] = symbol[1]
					if not ditm['a'] == 0:
						self.qdict.addtodict(ditm)
				bloomshares.append([symbol[0],nav,'9:00PM',mosdate.strftime('%m/%d/%Y'),nam])
			else:
				url = "https://www.bloomberg.com/markets/api/quote-page/%s" % ticker
				print url
				bloom = ""
				try:
					if not pd == False:
						pd.Update(delta*i+20,'Downloading share prices..')
					r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
					bloom = r.content
					read_json = json.loads(bloom)
					nav = str(read_json['basicQuote']['price'])
					nam = str(read_json['basicQuote']['name'])
					dat = str(read_json['basicQuote']['priceDate'])
					print symbol,nav,nam,dat
					quotes[ticker_key] = {'symbol':symbol, 'nam':nam, 'nav': nav, 'dat':dat}
					# add quote to project
					sharenams.append([symbol[0],nam])
					mosdate = datetime.strptime(dat,'%m/%d/%Y')
					if autoupd == True:
						ditm = {}
						ditm['d'] = mosdate.strftime('%Y%m%d')
						ditm['p'] = nav
						ditm['a'] = symbol[1]
						if not ditm['a'] == 0:
							self.qdict.addtodict(ditm)
					bloomshares.append([symbol[0],nav,'9:00PM',mosdate.strftime('%m/%d/%Y'),nam])
				except (IOError, ValueError) as e:
					#print bloom
					pass
		if autoupd == True:
			if self.anams == []:
				self.anams = sharenams
			else:
				for sn in sharenams:
					self.anams.append(sn)
		if not pd == False:
			pd.Update(95,'Done')
		return bloomshares

	def getyahooquote(self,symbol):
	# get latest share quote from yahoo finance
		yholist = self.getyahooquotes(shares=[symbol])
		if not len(yholist) == 0:
			return yholist[0][1]
		return '0.0'

	def getyahoohistory(self,share,date,pd=False):
	# get historical values from yahoo finance or share share, on date date
		yhoshares = []
		if share == '':
			return yhoshares
		a = str(int(date[4:6])-1)
		b = date[6:8]
		c = date[0:4]
		yahoourl = 'http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s' % (share,a,b,c)
		socket.setdefaulttimeout(10)
		if not pd == False:
			pd.Update(20,'Connecting to the internet..')
		try:
			fd = urllib2.urlopen(yahoourl)
			yho = fd.read()
			fd.close()
			if not pd == False:
				pd.Update(60,'Processing result..')
			yholist = yho.split('\n')
			if len(yholist) > 1:
				y = yholist[len(yholist)-2]
				y1 = y.split(',')
				yhoshares.append([share,y1[6],y1[0],"5.00pm",share])
		except IOError:
			pass
		return yhoshares

	def getyahooquotes(self,pd=False,shares=[]):
	# get latest mutual fund quotes from morningstar dot se
		groups = self.getgrouplabels(self.GROUPS[2][0])
		shareurl = ''
		shareids = []
		sharenams = []
		mornshares = []
		if not pd == False:
			pd.Update(10,'Preparing shares..')
		if shares == []:
			autoupd = True
			for g in groups:
				assets = self.getdassets(g,mini=2)
				for a in assets:
					shares.append(a[0])
					shareids.append(a[1])
		else:
			autoupd = False
		shtmp = []
		if autoupd == True:
			for i,s in enumerate(shares):
				if not pd == False:
					pd.Update(10)
				s = s.split()[0]
				#GROUPS[2][3][1][1][0-1]
				#print(s,shareids[i],self.GROUPS[2][3][1][1][0],self.GROUPS[2][3][1][1][1],len(s))
				if (int(shareids[i]) < self.GROUPS[2][3][1][1][0] or int(shareids[i]) > self.GROUPS[2][3][1][1][1] or (len(s) > 5 and '.' not in s)) or self.datautils.isisin(s) or self.datautils.ismorn(s) or self.datautils.isbloom(s):
					continue
#			ticker = symbol[0].split()[0]
				shtmp.append([s.split()[0],shareids[i]])
		else:
			shtmp = [shares]
		socket.setdefaulttimeout(10)
		delta = 0
		if len(shtmp) > 0:
			delta = 75/len(shtmp)
		for i,symbol in enumerate(shtmp):
			url = "https://finance.yahoo.com/quote/%s" % symbol[0]
			print url
			try:
				if not pd == False:
					pd.Update(delta*i+20,'Downloading share prices..')
					page_response = requests.get(url, headers={'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}, timeout=10)
					if page_response.status_code == 200:
						content_lines = page_response.content.splitlines()
						for l in content_lines:
							if l.startswith(b"root.App.main"):
								m = re.search('({.*})', str(l))
								#n = re.search('currentPrice\":{\"raw\":(.*?),',m.group(1))
								n = re.search(symbol[0]+'\":{(.*?)regularMarketPrice\":{\"raw\":(.*?),',m.group(1))
								nav = [n.group(2)]
								nam = []
								n = re.search('\"time\":\"(.*?)T', m.group(1))
								dat = [n.group(1)]
								print symbol,nav,nam,dat
								if nav == [] or dat == []:
									continue
								if nam == []:
									nam = symbol[0]
								pcom = re.compile(',')
								nav[0] = pcom.sub('',nav[0])
								if not self.datautils.isfloat(nav[0]):
									continue
								# add quote to project
								sharenams.append([symbol[0],nam[0]])
								mosdate = datetime.strptime(dat[0],'%Y-%m-%d')
								if autoupd == True:
									ditm = {}
									ditm['d'] = mosdate.strftime('%Y%m%d')
									ditm['p'] = nav[0]
									ditm['a'] = symbol[1]
									if not ditm['a'] == 0:
										self.qdict.addtodict(ditm)
								mornshares.append([symbol[0],nav[0],'9:00PM',mosdate.strftime('%m/%d/%Y'),nam[0]])
			except IOError:
				pass
		if autoupd == True:
			if self.anams == []:
				self.anams = sharenams
			else:
				for sn in sharenams:
					self.anams.append(sn)
		if not pd == False:
			pd.Update(95,'Done')
		return mornshares

	def getyahooquotes_old(self,pd=False,shares=[]):
	# get latest share quotes of list shares from yahoo finance
		groups = self.getgrouplabels(self.GROUPS[2][0])
		shareurl = ''
		yhoshares = []
		sharenams = []
		shareids = []
		if not pd == False:
			pd.Update(5,'Preparing shares..')
		if shares == []:
			autoupd = True
			for g in groups:
				assets = self.getdassets(g,mini=2)
				for a in assets:
					shares.append(a[0])
					shareids.append(a[1])
		else:
			autoupd = False
		shtmp = []
		for i,s in enumerate(shares):
			if not pd == False:
				pd.Update(10)
			if re.search(' ',s) or self.datautils.isisin(s) or self.datautils.ismorn(s) or self.datautils.isbloom(s):
				continue
			if autoupd == True:
				shtmp.append(shareids[i])
			if shareurl == '':
				shareurl = s
			else:
				shareurl = shareurl + '+' + s
		if shareurl == '':
			return yhoshares
		shareids = shtmp
		#yahoourl = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=sl1d1t1n' % shareurl
		yahoourl = 'https://finance.yahoo.com/quote/%s' % shareurl
		print yahoourl
		socket.setdefaulttimeout(10)
		if not pd == False:
			pd.Update(10,'Connecting to the internet..')
		try:
			fd = urllib2.urlopen(yahoourl)
			yho = fd.read()
			fd.close()
			if not pd == False:
				pd.Update(60,'Processing result..')
			#yholist = yho.split('\r\n')
			yholist = yho.split('\n')
			delta = 0
			if len(yholist) > 0:
				delta = 35/len(yholist)
			for i,y in enumerate(yholist):
				if not pd == False:
					pd.Update(delta*i+60)
				if y == '':
					continue
				y = re.sub('"','',y)
				sh = y.split(',')
				if sh[1] == '0.00':
					continue
				yhoshares.append(sh)
				sharenams.append([sh[0],sh[4]])
				# add quote to project
				if autoupd == True:
					ditm = {}
					yhodate = datetime.strptime(sh[2],'%m/%d/%Y')
					ditm['d'] = yhodate.strftime('%Y%m%d')
					ditm['p'] = sh[1]
					ditm['a'] = shareids[i]
					if not ditm['a'] == 0 and self.accname(shareids[i]) == sh[0]:
						print [sh[0],ditm['a']], ditm['p'], sh[4], sh[2]
						self.qdict.addtodict(ditm)
			if autoupd == True:
				if self.anams == []:
					self.anams = sharenams
				else:
					for sn in sharenams:
						self.anams.append(sn)
		except IOError:
			pass
		if not pd == False:
			pd.Update(95,'Done')
		return yhoshares

	def getgooglequotes(self,pd,shares=[]):
	# get latest share quotes of list shares from Google finance (identical to Yahoo!)
	#	googleurl = 'http://www.google.com/finance/historical?q=BRK.B&output=csv'
		pass

	def getmorningstarquote(self,symbol):
	# get latest share quote from yahoo finance
		mornlist = self.getmorningstarquotes(shares=[symbol])
		if not len(mornlist) == 0:
			return mornlist[0][1]
		return '0.0'

	def getmorningstarquotes(self,pd=False,shares=[]):
	# get latest mutual fund quotes from morningstar dot se
		groups = self.getgrouplabels(self.GROUPS[2][0])
		shareurl = ''
		shareids = []
		sharenams = []
		mornshares = []
		if not pd == False:
			pd.Update(10,'Preparing shares..')
		if shares == []:
			autoupd = True
			for g in groups:
				assets = self.getdassets(g,mini=2)
				for a in assets:
					shares.append(a[0])
					shareids.append(a[1])
		else:
			autoupd = False
		shtmp = []
		if autoupd == True:
			for i,s in enumerate(shares):
				if not pd == False:
					pd.Update(10)
				s = s.split()[0]
				if not self.datautils.ismorn(s):
					continue
				shtmp.append([s,shareids[i]])
		else:
			shtmp = [shares]
		socket.setdefaulttimeout(10)
		delta = 0
		if len(shtmp) > 0:
			delta = 75/len(shtmp)
		for i,symbol in enumerate(shtmp):
			#url = "http://quote.morningstar.com/stock/s.aspx?t=%s" % symbol[0]
			#url = "http://quote.morningstar.com/fund/f.aspx?t=%s" % symbol[0]
			url = "https://morningstar.se/Funds/Quicktake/Overview.aspx?perfid=%s" % symbol[0]
			#url = "http://quote.morningstar.com/fund/chart.aspx?t=%s" % symbol[0]
			print url
			try:
				nav = []
				dat = []
				nam = []
				if not pd == False:
					pd.Update(delta*i+20,'Downloading share prices..')
				#fd = urllib2.urlopen(url)
				#morn = fd.read()
				#fd.close()
				#pnav = re.compile('NAV:"(\d*?\,?\d+?.\d+?)"')
				#pnam = re.compile('CompanyName:"(.+?)"')
				#pdat = re.compile('LastDate:"(\d{4}-\d{2}-\d{2})')
				#nav = pnav.findall(morn)
				#nam = pnam.findall(morn)
				#dat = pdat.findall(morn)
				page_response = requests.get(url, headers={'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}, timeout=10)
				if page_response.status_code == 200:
					content_lines = page_response.content.splitlines()
					for l in content_lines:
						m = re.search('Senaste NAV</td><td>(.*?) [A-Z]{3}</td><td>(.*?)</td>', str(l))
						if m:
							nav = m.group(1).replace('.','')
							nav = nav.replace(',','.')
							nav = [nav.replace(' ','')]
							dat = [m.group(2)]
					print symbol,nav,nam,dat
				if nav == [] or dat == []:
					continue
				if nam == []:
					nam = [symbol[0]]
				pcom = re.compile(',')
				nav[0] = pcom.sub('',nav[0])
				if not self.datautils.isfloat(nav[0]):
					continue
				# add quote to project
				sharenams.append([symbol[0],nam[0]])
				mosdate = datetime.strptime(dat[0],'%Y-%m-%d')
				if autoupd == True:
					ditm = {}
					ditm['d'] = mosdate.strftime('%Y%m%d')
					ditm['p'] = nav[0]
					ditm['a'] = symbol[1]
					if not ditm['a'] == 0:
						self.qdict.addtodict(ditm)
				mornshares.append([symbol[0],nav[0],'9:00PM',mosdate.strftime('%m/%d/%Y'),nam[0]])
			except IOError:
				pass
		if autoupd == True:
			if self.anams == []:
				self.anams = sharenams
			else:
				for sn in sharenams:
					self.anams.append(sn)
		if not pd == False:
			pd.Update(95,'Done')
		return mornshares

	def getsebquotes(self,pd,shares=[]):
	# get latest mutual fund quotes from SEB
		groups = self.getgrouplabels(self.GROUPS[2][0])
		sharenams = []
		shareids = []
		if not pd == False:
			pd.Update(10,'Preparing currencies..')
		if shares == []:
			autoupd = True
			for g in groups:
				assets = self.getdassets(g,mini=2)
				for a in assets:
					shares.append(a[0])
					shareids.append(a[1])
		else:
			autoupd = False
		shtmp = []
		if not pd == False:
			pd.Update(15)
		for i,s in enumerate(shares):
			if autoupd == True:
				shtmp.append([s,shareids[i]])
		if shtmp == []:
			return shtmp
		seburl = 'http://www.seb.se/pow/fmk/2100/Senaste_fondkurserna.TXT'
		socket.setdefaulttimeout(10)
		if not pd == False:
			pd.Update(20,'Connecting to the internet..')
		try:
			fd = urllib2.urlopen(seburl)
			seb = fd.read()
			fd.close()
			if not pd == False:
				pd.Update(70,'Processing result..')
			seblist = seb.split('\n')
			delta = 0
			if len(seblist) > 0:
				delta = 25/len(seblist)
			for i,y in enumerate(seblist):
				if not pd == False:
					pd.Update(delta*i+70)
				if y == '':
					continue
				sh = y.split(';')
				for j,s in enumerate(shtmp):
					if s[0] == unicode(sh[1],'latin-1'):
						# add quote to project
						if autoupd == True:
							ditm = {}
							sebdate = datetime.strptime(sh[0],'%Y-%m-%d')
							ditm['d'] = sebdate.strftime('%Y%m%d')
							ditm['p'] = sh[2]
							ditm['a'] = shtmp[j][1]
							if not ditm['a'] == 0:
								self.qdict.addtodict(ditm)
		except IOError:
			pass
		if not pd == False:
			pd.Update(95,'Done')
		return []

	def calcecbtobase(self,rates):
	# re-calculate ecb result depeding on base currency
		newrates = []
		baserate = 0
		base = self.getbasecurrency()
		if base == '':
			return newrates
		for r in rates:
			if r[1] == base:
				baserate = float(r[2])
		if baserate == 0:
			return newrates
		for r in rates:
			rv = self.datautils.rstr(baserate / float(r[2]),4)
			newrates.append([r[0],r[1],rv])
		return newrates

	def getecbrate(self,currency):
		rate = self.getecbrates(False,currency)
		return rate

	def getecbrates(self,pd=False,ccode=False):
	# get latest exchange rates from the ECB and re-calculate result to base currency
		ecbrates = []
		subecbrates = []
		ratedate = ''
		ecburl = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
		socket.setdefaulttimeout(10)
		if not pd == False:
			pd.Update(10,'Connecting to the internet..')
		try:
			fd = urllib2.urlopen(ecburl)
			ecb = fd.read()
			fd.close()
			if not pd == False:
				pd.Update(60,'Processing result..')
			ecblist = ecb.split('\n')
			delta = 0
			if len(ecblist) > 0:
				delta = 30/len(ecblist)
			for i,e in enumerate(ecblist):
				if not pd == False:
					pd.Update(delta*i+65)
				if e == '':
					continue
				if re.search('time',e):
					ratedate = re.search('time=\'.*?\'',e).group()
					ratedate = re.sub('\'','',ratedate)
					ratedate = re.sub('-','',ratedate)
					ratedate = ratedate.split('=')[1]
				if not re.search('currency',e):
					continue
				e = re.sub('\t','',e)
				currency = re.search('currency=\'.*?\'',e).group()
				currency = re.sub('\'','',currency)
				currency = currency.split('=')[1]
				rate = re.search('rate=\'.*?\'',e).group()
				rate = re.sub('\'','',rate)
				rate = rate.split('=')[1]
				ecbrates.append([ratedate,currency,rate])
			ecbrates.append([ratedate,'EUR','1.0'])
			ecbrates = self.calcecbtobase(ecbrates)
			if ccode == False:
				currencies = self.getcurrencies()
				subecbrates = []
				base = self.getbasecurrency()
				for c in currencies:
					for r in ecbrates:
						if c == r[1] and not c == base:
							ditm = {}
							ditm['d'] = r[0]
							ditm['c'] = r[1]
							ditm['p'] = r[2]
							self.cdict.addtodict(ditm)
							subecbrates.append(r)
			else:
				base = self.getbasecurrency()
				if not ccode == base:
					for r in ecbrates:
						if ccode == r[1]:
							return r[2]
				else:
					return '1.0'
				return '0.0'
		except IOError:
			pass
		if not pd == False:
			pd.Update(95,'Done')
		return subecbrates

	def downloadquotes(self,pd=False):
	# download all quotes from all sources
		self.anams = []
		yhoquotes = self.getyahooquotes(pd)
		morningquotes = self.getmorningstarquotes(pd)
		bloombergquotes = self.getbloombergquotes(pd)
		ecbrates = self.getecbrates(pd)
		#sebquotes = self.getsebquotes(pd)
		return True

	ALLOWEDCURRENCIES = ['EUR','USD','JPY','BGN','CZK','DKK','EEK','GBP','HUF','LTL','LVL','PLN','RON','SEK','CHF','NOK','HRK','RUB','TRY','AUD','BRL','CAD','CNY','HKD','IDR','INR','KRW','MXN','MYR','NZD','PHP','SGD','THB','ZAR']

	GROUPS = [
		['Revenues',[10000,19999],-1,
			[
			['Salary',      [10000,10999]],
			['Interest',    [11000,11999]],
			['Dividend',    [12000,12999]],
			['Income from Business', [13000,13999]],
			['Social Security', [14000,14999]],
			['Other income',[19000,19999]]
			],
		],
		['Expenses',[20000,29999],1,
			[
			['Living Costs',  [20000,20999]],
			['Food',          [21000,21999]],
			['Clothes',       [22000,22999]],
			['Automobile/Transportation',[23000,23999]],
			['Holidays',      [24000,24999]],
			['Entertainment', [25000,25999]],
			['Memberships',   [26000,26999]],
			['Medical Costs', [27000,27999]],
			['Other expenses',[29000,29999]]
			]
		],
		['Current assets',[30000,35999],1,
			[
			['Accounts',      [30000,30999]],
			['Stocks',        [31000,31999]],
			['Mutual funds',  [32000,32999]],
			['Bonds',         [33000,33999]],
			['Derivates',     [34000,34999]],
			['Other current assets',[35000,35999]]
			]
		],
		['Non-current assets',[36000,39999],1,
			[
			['Houses',[37000,37999]],
			['Cars',[38000,38999]],
			['Other non-current assets',[39000,39999]]
			]
		],
		['Current liabilities',[40000,42999],-1,
			[
			['Current bank loans',[40000,40999]],
			['Other current liabilities',[42000,42999]],
			]
		],
		['Non-current liabilities',[43000,49999],-1,
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

	ACCOUNTS_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<accounts>\n<account num=\"10000\" c=\"CURRENCY\" de=\"Salary\"/><account num=\"11000\" c=\"CURRENCY\" de=\"Interest\"/>\n<account num=\"12000\" c=\"CURRENCY\" de=\"Dividend\"/>\n<account num=\"19000\" c=\"CURRENCY\" de=\"Other income\"/>\n<account num=\"20000\" c=\"CURRENCY\" de=\"Living costs\"/>\n<account num=\"21000\" c=\"CURRENCY\" de=\"Food and groceries\"/>\n<account num=\"22000\" c=\"CURRENCY\" de=\"Clothes\"/>\n<account num=\"23000\" c=\"CURRENCY\" de=\"Transportation\"/>\n<account num=\"24000\" c=\"CURRENCY\" de=\"Vacation\"/>\n<account num=\"25000\" c=\"CURRENCY\" de=\"Entertainment\"/>\n<account num=\"29000\" c=\"CURRENCY\" de=\"Other costs\"/>\n<account num=\"30000\" c=\"CURRENCY\" de=\"My Salary Account\"/>\n<account num=\"30001\" c=\"CURRENCY\" de=\"My Savings Account\"/>\n</accounts>"
	CURRENCIES_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<currencies>\n<price d=\"1970-01-01\" c=\"CURRENCY\" p=\"1\"/>\n</currencies>"
	QUOTES_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<quotes>\n<quote d=\"1970-01-01\" a=\"10000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"11000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"12000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"19000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"20000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"21000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"22000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"23000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"24000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"25000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"29000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"30000\" p=\"1\"/>\n<quote d=\"1970-01-01\" a=\"30001\" p=\"1\"/>\n</quotes>"
	TRANSACTIONS_XML = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n<transactions>\n<item d=\"DATE\" fs=\"0\" fq=\"0\" fp=\"1\" fc=\"0\" ts=\"0\" tq=\"0\" tp=\"1\" tc=\"0\" de=\"initial transaction\"/>\n</transactions>"

def main():
	frugal = datacoll_c()
	frugal.openfiles('/home/tom/frugal10/source/')
	frugal.calcnow()

if __name__ == '__main__':
	main()
