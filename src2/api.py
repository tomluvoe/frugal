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

import core
import utils
import datetime

class api:
	def __init__(self):
		self.cores = []
		self.utils = utils.utils()
		self.dates = []

		license = """Frugal is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Frugal is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Frugal.  If not, see <http://www.gnu.org/licenses/>."""
		desc = """Frugal is a simple yet powerful personal finance and stock 
portfolio management application. It provides quick on-line 
stock quote and currency rate updates and easy to understand 
graphical and textual views of your financial situation. 
The software is platform independent, which means that you 
can run it on your Windows PC, your Apple Macintosh or on your 
Linux computer."""
	
		self.info = {}
		self.info['name'] = core.INFO[0]
		self.info['version'] = core.INFO[1]
		self.info['description'] = desc
		self.info['copyright'] = core.INFO[2]
		self.info['website'] = core.INFO[4]
		self.info['license'] = license
		self.info['developer'] = core.INFO[3]
		
		self.error = 'General error'
		
		self.ALLOWEDCURRENCIES = core.core.ALLOWEDCURRENCIES[:]

# ------
# about functions
	def getaboutinfo(self):
		return self.info

	def geterrormsg(self):
		return self.error

# ------
# functions interfacing core related to project management

	def new(self,dir,currency):
		if len(self.cores) >= 1:
			return False
		newcore = core.core()
		rv = newcore.newproject(dir,currency)
		if rv == True:
			self.cores = [newcore]
		else:
			self.error = 'Currency not allowed or project already exists. Create project failed!'
		return rv

	def open(self,dir):
		if len(self.cores) >= 2:
			return False
		newcore = core.core()
		rv = newcore.openproject(dir)
		if rv == True:
			if not len(self.cores) == 0 and not self.getcurrency() == newcore.getbasecurrency():
				self.error = 'The projects do not have the same base currency.'
				rv = False
			else:
				newdates = newcore.getdatelist()
				self.dates = self._mergedates(newdates)
				self.cores.append(newcore)
		return rv
	
	def save(self):
		rv = True
		if self.cores == []:
			return False
		for c in self.cores:
			if c.saveproject() == False:
				self.error = 'Save project failed.'
				rv = False
		return rv
	
	def issaved(self):
		rv = True
		for c in self.cores:
			if c.issaved() == False:
				rv = False
		return rv
		
	def calculate(self):
		rv = True
		for c in self.cores:
			if c.calcnow() == False:
				self.error = 'Calculation operation failed.'
				rv = False
		return rv
	
	def downloadquotes(self):
		rv = True
		for c in self.cores:
			if c.downloadquotes() == False:
				self.error = 'Download quotes did not finish successfully.'
				rv = False
		return rv

# -----
# functions related to the program

	def getprogramname(self):
		name = self.info['name']
		version = self.info['version']
		numcores = len(self.cores)
		return "%s %s - %d project(s)"%(name,version,numcores)
	
	def getprogramversion(self):
		return self.info['version']

# -----
# add transactions
	def addtransaction(self,datetim,description,faccount,famount,fprice,fcomm,taccount,tamount,tprice,tcomm):
		if not self.utils.isint(faccount) and self.utils.isint(taccount):
			self.error = 'Accounts are defined incorrectly.'
			return False
		if not self.utils.isfloat(famount) and self.utils.isfloat(fprice) and self.utils.isfloat(fcomm) and self.utils.isfloat(tamount) and self.utils.isfloat(tprice) and self.utils.isfloat(tcomm):
			self.error = 'Amounts are defined incorrectly.'
			return False
		d = datetim.strftime("%Y%m%d")
		fs = faccount
		fq = famount
		fp = fprice
		fc = fcomm
		ts = taccount
		tq = tamount
		tp = tprice
		tc = tcomm
		de = description
		return self.cores[0].addtransaction(d,fs,fq,fp,fc,ts,tq,tp,tc,de)

	def addsimpletransaction(self,datetim,description,faccount,taccount,amount):
		if not self.utils.isint(faccount) and self.utils.isint(taccount):
			self.error = 'Accounts are defined incorrectly.'
			return False
		if not self._samecurrency(faccount,taccount):
			self.error = 'Accounts do not have the same currency.'
			return False
		return self.addtransaction(datetim,description,faccount,amount,1.0,0.0,taccount,amount,1.0,0.0)

	def splitasset(self,datetim,x,y,account,price):
		if not (self.utils.isint(x) and self.utils.isint(y)):
			self.error = 'Values x and y must be integers.'
			return Flase
		if not (self.utils.isfloat(price)):
			self.error = 'Price must be a decimal number.'
			return False
		d = datetim.strftime("%Y%m%d")
		rv = self.cores[0].splitasset(d,x,y,price,account)
		if rv == False:
			self.error = 'Split share failed. Please check that you will end up with an even number of shares after split.'
		return rv


# -----
# add assets or accounts

	def getaccountcurrency(self,account):
		cid = self.cores[0].getassetcurrency(account)
		clist = self.cores[0].getcurrencies()
		return clist[cid]

	def addasset(self,description,price,currency,group,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		if not self.utils.isfloat(price):
			self.error = 'Price is defined incorrectly.'
			return False
		if not currency in self.cores[0].ALLOWEDCURRENCIES:
			self.error = 'Currency not allowed.'
			return False
		d = datetim.strftime("%Y%m%d")
		de = description
		p = price
		c = currency
		return self.cores[0].addasset(d,p,c,de,group)

	def addaccount(self,description,price,currency,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		return self.addasset(description,price,currency,self.cores[0].GROUPS[2][3][0][0],datetim)

	def addshare(self,description,price,currency,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		return self.addasset(description,price,currency,self.cores[0].GROUPS[2][3][1][0],datetim)

	def addmutualfund(self,description,price,currency,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		return self.addasset(description,price,currency,self.cores[0].GROUPS[2][3][2][0],datetim)

	def addbond(self,description,price,currency,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		return self.addasset(description,price,currency,self.cores[0].GROUPS[2][3][3][0],datetim)

	def addderivate(self,description,price,currency,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		return self.addasset(description,price,currency,self.cores[0].GROUPS[2][3][4][0],datetim)

	def addotherasset(self,description,price,currency,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		return self.addasset(description,price,currency,self.cores[0].GROUPS[2][3][5][0],datetim)

# -----
# internal functions interfacing core
	def _getflowsum(self,group,year,month=0):
		#data = self.cores[0].getassets(group,True,False,year,month,year,month)
		data = self._getassets(group,True,False,year,month,year,month)
		sum = 0.0
		for d in data:
			sum = sum + float(d[4])
		return sum

	def _getgroupsum(self,group,year,month=0):
		#data = self._getassets(group,False,False,year,month)
		data = self._getassets(group,False,False,year,month)
		sum = 0.0
		for d in data:
			sum = sum + float(d[4])
		return sum

	def _getassets(self,group,diff=False,all=False,year=0,month=0,year1=0,month1=0,selcore=-1):
		alist = []
		if selcore == -1:
			for c in self.cores:
				a = c.getassets(group,diff,all,year,month,year1,month1)
				for a0 in a:
					alist.append(a0)
		else:
			alist = self.cores[selcore].getassets(group,diff,all,year,month,year1,month1)
		return alist

	def _getassetgroups(self,group,diff=False,all=False,year=0,month=0,year1=0,month1=0):
		alist = []
		for i,c in enumerate(self.cores):
			if i == 0:
				alist = c.getassetgroups(group,diff,all,year,month,year1,month1)
				continue
			a = c.getassetgroups(group,diff,all,year,month,year1,month1)
			for j,a0 in enumerate(a):
				alist[j][4] = self.utils.rstr(float(alist[j][4]) + float(a[j][4]))
		return alist

	def _getassetshistory(self,groups,diff=False):
		for i,c in enumerate(self.cores):
			if i == 0:
				ahlist = c.getassetshistory(groups,diff)
				ahlist = self._placeondates(ahlist,diff)
				continue
			a = c.getassetshistory(groups,diff)
			a = self._placeondates(a,diff)
			for j,a0 in enumerate(a):
				ahlist[j][1] = self.utils.rstr(float(ahlist[j][1]) + float(a[j][1]))
		return ahlist

	def _samecurrency(self,account1,account2):
		if not self.cores[0].getassetcurrency(account1) == self.cores[0].getassetcurrency(account2):
			return False
		return True

	def _mergedates(self,datelist):
		if self.dates == []:
			return datelist
		newdates = []
		if self.dates[0] > datelist[0]:
			one = datelist
			two = self.dates
		else:
			one = self.dates
			two = datelist
		newdates = one.tolist()	
		while newdates[-1] < two[-1]:
			mm = int(str(int(one[-1]))[-2:])
			if mm == 12:
				dat = newdates[-1] + 88
			dat = newdates[-1] + 1
			newdates.append(dat)
		return newdates

	def _incymdate(self,date):
			d0 = int(date)
			mm = int(str(d0)[-2:])
			if mm == 12:
				d0 = d0 + 88
			d0 = d0 + 1
			return d0

	def _placeondates(self,hlist,diff=False):
		d0 = int(hlist[0][0])
		d1 = int(self.dates[0])
		while d1 < d0:
			hlist.insert(0,[d1,'0.0'])
			d1 = self._incymdate(d1)
		if diff == True:
			s0 = '0.0'
		else:
			s0 = hlist[-1][1]
		d0 = int(hlist[-1][0])
		d1 = int(self.dates[-1])
		while d0 < d1:
			d0 = self._incymdate(d0)
			hlist.append([str(d0),s0])
		return hlist

# -----
# functions interfacing core

	def getcurrency(self):
		currency = self.cores[0].getbasecurrency()
		return currency

	def getassetname(self,num,ticker=False):
		name = self.cores[0].getassetname(num,ticker)
		return name

	def getbudget(self):
		return self.cores[0].getbudget()

### - stock portfolio
	def getshares(self,year=0,month=0,selcore=-1,all=False):
		return self._getassets('Stocks',False,all,year,month,selcore=selcore)

	def getmutualfunds(self,year=0,month=0,selcore=-1,all=False):
		return self._getassets('Mutual funds',False,all,year,month,selcore=selcore)

	def getderivates(self,year=0,month=0,selcore=-1,all=False):
		return self._getassets('Derivates',False,all,year,month,selcore=selcore)

	def getbonds(self,year=0,month=0,selcore=-1,all=False):
		return self._getassets('Bonds',False,all,year,month,selcore=selcore)

	def getothercurrent(self,year=0,month=0,selcore=-1,all=False):
		return self._getassets('Other current assets',False,all,year,month,selcore=selcore)

	def getaccounts(self,year=0,month=0,selcore=-1,all=False):
		accounts = []
		acc = self._getassets('Accounts',False,all,year,month,selcore=selcore)
		for a in acc:
			if all == False and abs(float(a[1])) < 1:
				continue
			accounts.append(a)
		return accounts
	
	def getliquidssum(self,year=0,month=0):
		return self._getgroupsum('Accounts',year,month)
		
	def getassetquotes(self,aid):
		return self.cores[0].getassetquotes(aid)
		
	def getassettransactions(self,aid):
		return self.cores[0].getassettransactions(aid)
	
	def getassetaverageprice(self,aid,year=0,month=0,date=0):
		return self.cores[0].getassetapps(aid,year,month,date)
	
## - end stock portfolio

	def getassets(self,year=0,month=0):
		assets = []
		a0 = self.getothercurrent(year,month)
		for a in a0:
			assets.append(a)
		a0 = self.getderivates(year,month)
		for a in a0:
			assets.append(a)
		a0 = self.getbonds(year,month)
		for a in a0:
			assets.append(a)
		a0 = self.getmutualfunds(year,month)
		for a in a0:
			assets.append(a)
		a0 = self.getshares(year,month)
		for a in a0:
			assets.append(a)
		a0 = self.getaccounts(year,month)
		for a in a0:
			assets.append(a)
		return assets

	def getassetsminusaccounts(self,year=0,month=0,selcore=-1,all=False):
		assets = []
		a0 = self.getothercurrent(year,month,selcore=selcore,all=all)
		for a in a0:
			assets.append(a)
		a0 = self.getderivates(year,month,selcore=selcore,all=all)
		for a in a0:
			assets.append(a)
		a0 = self.getbonds(year,month,selcore=selcore,all=all)
		for a in a0:
			assets.append(a)
		a0 = self.getmutualfunds(year,month,selcore=selcore,all=all)
		for a in a0:
			assets.append(a)
		a0 = self.getshares(year,month,selcore=selcore,all=all)
		for a in a0:
			assets.append(a)
		return assets

	def getassetshistory(self,noncurrent=False):
		if noncurrent == False:
			#hist = self.cores[0].getassetshistory([core.GRP_ASSETS_C])
			hist = self._getassetshistory([core.GRP_ASSETS_C])
		else:
			#hist = self.cores[0].getassetshistory([core.GRP_ASSETS_NC])
			hist = self._getassetshistory([core.GRP_ASSETS_NC])
		return hist

	def getliabilitieshistory(self,noncurrent=False):
		if noncurrent == False:
			#hist = self.cores[0].getassetshistory([core.GRP_LIABILITIES_C])
			hist = self._getassetshistory([core.GRP_LIABILITIES_C])
		else:
			#hist = self.cores[0].getassetshistory([core.GRP_LIABILITIES_NC])
			hist = self._getassetshistory([core.GRP_LIABILITIES_NC])
		return hist

	def getrevenueshistory(self):
		#return self.cores[0].getassetshistory([core.GRP_REVENUES],True)
		return self._getassetshistory([core.GRP_REVENUES],True)

	def getexpenseshistory(self):
		#return self.cores[0].getassetshistory([core.GRP_EXPENSES],True)
		return self._getassetshistory([core.GRP_EXPENSES],True)

	def getrevenuegroups(self,year,month=0):
		revenues = self._getassetgroups(core.GRP_REVENUES,True,True,year,month,year,month)
		return revenues
	
	def getexpensegroups(self,year,month=0):
		expenses = self._getassetgroups(core.GRP_EXPENSES,True,True,year,month,year,month)
		return expenses

	def getrevenues(self,year,month=0,selcore=-1):
		revenues = self._getassets(core.GRP_REVENUES,True,True,year,month,year,month,selcore=selcore)
		return revenues
	
	def getexpenses(self,year,month=0,selcore=-1):
		expenses = self._getassets(core.GRP_EXPENSES,True,True,year,month,year,month,selcore=selcore)
		return expenses

# ----
# functions interfacing only api

	def getrevenuessum(self,year,month=0):
		sum = self._getflowsum(core.GRP_REVENUES,year,month)
		return sum
		
	def getexpensessum(self,year,month=0):
		sum = self._getflowsum(core.GRP_EXPENSES,year,month)
		return sum

	def getcurrentassetssum(self,year,month=0):
		return self._getgroupsum(core.GRP_ASSETS_C,year,month)

	def getcurrentliabilitiessum(self,year,month=0):
		return self._getgroupsum(core.GRP_LIABILITIES_C,year,month)

	def getassetssum(self,year,month=0):
		sum0 = self._getgroupsum(core.GRP_ASSETS_C,year,month)
		sum1 = self._getgroupsum(core.GRP_ASSETS_NC,year,month)
		return sum0+sum1		

	def getliabilitiessum(self,year,month=0):
		sum0 = self._getgroupsum(core.GRP_LIABILITIES_C,year,month)
		sum1 = self._getgroupsum(core.GRP_LIABILITIES_NC,year,month)
		return sum0+sum1

	def getassetschangesum(self,year,month=0):
		y0 = year
		m0 = month
		if month == 0:
			y1 = year-1
			m1 = month
		else:
			if month > 1:
				y1 = year
				m1 = month-1
			else:
				y1 = year-1
				m1 = 12
		sum0 = self.getassetssum(y0,m0,False) + self.getassetssum(y0,m0,True) - self.getliabilitiessum(y0,m0,False) - self.getliabilitiessum(y0,m0,True)
		sum1 = self.getassetssum(y1,m1,False) + self.getassetssum(y1,m1,True) - self.getliabilitiessum(y1,m1,False) - self.getliabilitiessum(y1,m1,True)
		sum = sum0 - sum1
		return sum

	def getassetshistoryplot(self,noncurrent=False):
		dat = []
		values = self.getassetshistory(noncurrent)
		for v in range(len(values[0])):
			dat.append([])
		for v in values:
			dat[0].append(v[0])
			for i,v0 in enumerate(v[1:]):
				dat[i+1].append(float(v0))
		return dat

	def getliabilitieshistoryplot(self,noncurrent=False):
		dat = []
		values = self.getliabilitieshistory(noncurrent)
		for v in range(len(values[0])):
			dat.append([])
		for v in values:
			dat[0].append(v[0])
			for i,v0 in enumerate(v[1:]):
				dat[i+1].append(float(v0))
		return dat

	def getrevenueshistoryplot(self):
		dat = []
		values = self.getrevenueshistory()
		for v in range(len(values[0])):
			dat.append([])
		for v in values:
			dat[0].append(v[0])
			for i,v0 in enumerate(v[1:]):
				dat[i+1].append(float(v0))
		return dat

	def getexpenseshistoryplot(self):
		dat = []
		values = self.getexpenseshistory()
		for v in range(len(values[0])):
			dat.append([])
		for v in values:
			dat[0].append(v[0])
			for i,v0 in enumerate(v[1:]):
				dat[i+1].append(float(v0))
		return dat

	def getincomehistoryplot(self):
		dat = self.getrevenueshistoryplot()
		dat.append(self.getexpenseshistoryplot()[1])
		dat3 = []
		for i,d in enumerate(dat[1]):
			dat3.append(d - dat[2][i])
		dat.append(dat3)
		return dat

	def getequityhistoryplot(self,diff=False):
		dat = self.getassetshistoryplot(False)
		dat0 = self.getassetshistoryplot(True)
		for i,d in enumerate(dat0[1]):
			dat[1][i] = dat[1][i] + d
		dat0 = self.getliabilitieshistoryplot(False)
		for i,d in enumerate(dat0[1]):
			dat[1][i] = dat[1][i] - d
		dat0 = self.getliabilitieshistoryplot(True)
		for i,d in enumerate(dat0[1]):
			dat[1][i] = dat[1][i] - d
		if diff == True and len(dat[1]) > 1:
			dat1 = dat[:]
			for i,d in enumerate(dat[1][0:len(dat[1])-1]):
				dat[1][i] = dat[1][i+1] - d
			dat[1][-1] = dat[1][-1] - dat[1][-2]
			dat[1].insert(0,0.0)
			dat[1].pop()
		return dat

# ----
# helper function
	def assetstolist(self,assets,all=False,storeid=False):
		labels = []
		values = []
		ids = []
		for a in assets:
			v = float(a[4])
			if v == 0.0 and all == False:
				continue
			labels.append(self.getassetname(a[0],ticker=True))
			values.append(v)
			ids.append(a[0])
		if storeid == False:
			return [labels,values]
		return [labels,values,ids]

	def assetgroupstolist(self,assets,all=False,storeid=False):
		labels = []
		values = []
		ids = []
		for a in assets:
			v = float(a[4])
			if v == 0.0 and all == False:
				continue
			labels.append(a[0])
			values.append(v)
			ids.append(a[0])
		if storeid == False:
			return [labels,values]
		return [labels,values,ids]

	def quotestolist(self,quotes):
		return self.transposelist(quotes)
	
	def transactionstolist(self,translist):
		newlist = []
		for t in translist:
			if not float(t[1]) == 0.0:
				newlist.append([t[0],t[2]])
		newlist = self.transposelist(newlist)
		return newlist

	#add core function to get all within one group
	def getassetssumlist(self,year,month=0):
		labels = []
		values = []
		groups = self.cores[0].getgrouplist(core.GRP_ASSETS_C)
		groups0 = self.cores[0].getgrouplist(core.GRP_ASSETS_NC)
		for grp in groups0:
			groups.append(grp)
		for grp in groups:
			sum = self._getgroupsum(grp,year,month)
			if float(sum) == 0.0:
				continue
			labels.append(grp)
			values.append(sum)
		return [labels,values]

	def ymtodates(self,ymlist):
		dates = []
		datelist = self.utils.ymtodatetime(ymlist)
		for d in datelist:
			dates.append(d.strftime("%B %Y"))
		return dates

	def transposelist(self,list):
		return self.utils.transposelist(list)
