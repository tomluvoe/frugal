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

import wx
from datetime import date

from plugin_c import plugin_c
from datautils_c import datautils_c

class pportfolio_c(plugin_c):
	NAME = 'Stock Portfolio'
	FUNCTIONS = ['Transaction History','Stock Split']

	# ATTR view type - plot, list, history, detailed..
	def createpanel(self,func='',attr=[]):
		self.func = func

		if(self.func == pportfolio_c.FUNCTIONS[0]):
			self.transactionhist(attr)
		elif(self.func == pportfolio_c.FUNCTIONS[1]):
			self.createstocksplitpanel(attr)
		else:
			self.portfolio(attr)

	def portfolio(self,attr=[]):
		group = self.dc.GROUPS[2][0]

		if attr[0] == 'history':
			self.createhassetspanel(group)
		elif attr[0] == 'historyy':
			self.createhassetspanel(group,year=1)
		elif attr[0] == 'gdetails':
			self.createassetsplot(group)
		elif attr[0] == 'ghistory':
			self.createhassetsplot(group)
		elif attr[0] == 'ghistoryy':
			self.createhassetsplot(group,year=1)
		else: # 'details'
			self.portfoliopanel()

	def createstocksplitpanel(self,attr=[]):
		todaysdate = date.today().strftime('%Y%m%d')
		column1 = []
		column2 = []

		column1.append(self.statictext('Select Share'))
		column1.append(self.statictext('Received X Shares for Y Held'))
		column1.append(self.statictext('X'))
		column1.append(self.statictext('Y'))
		column1.append(self.statictext('Split Date'))
		column1.append(self.statictext('Share Price (after split)'))

		self.shares = self.dc.getdassets(self.dc.GROUPS[2][3][1][0],mini=2)
		shlist = []
		for s in self.shares:
			shlist.append(s[0])
		self.split = self.choicelist(shlist)
		self.splitx = self.textctrl('1')
		self.splity = self.textctrl('1')
		self.splitd = self.textctrl(todaysdate)
		self.splitp = self.textctrl('1.0')

		column2.append(self.split)
		column2.append(self.statictext(''))
		column2.append(self.splitx)
		column2.append(self.splity)
		column2.append(self.splitd)
		column2.append(self.splitp)

	        btn = wx.Button(self,-1,'Add Stock Split')
	        self.Bind(wx.EVT_BUTTON,self.handlesplitbutton,btn)
		column1.append(btn)

		self.createsizercols([column1,column2])

	def handlesplitbutton(self,event):
		du = datautils_c()

		sel = self.split.GetCurrentSelection()
		s = self.shares[sel][1]
		st = self.dc.accticker(s)
		x = self.splitx.GetLineText(0)
		y = self.splity.GetLineText(0)
		a = self.dc.getapps(s)
		d = self.splitd.GetLineText(0)
		p = self.splitp.GetLineText(0)
		c = self.dc.acccurrency(s)
		cn = self.dc.currencyname(c)
		q = self.dc.getaccbalance(s)

		qn = float(q)*float(x)/float(y)
		qeven = qn-round(qn)
		an = float(a)*float(q)/float(qn)

		if not (du.isint(d) and int(d) > 19700101 and int(d) < 21000101):
			errmsg = 'Input data is not correct. Date must be YYYYMMDD.'
			self.errdlg(errmsg)
			return

		if not (du.isint(x) and du.isint(y)):
			errmsg = 'Input data is not correct. X and Y must be whole number.'
			self.errdlg(errmsg)
			return

		if not (du.isfloat(p)):
			errmsg = 'Input data is not correct. Price must be floating point number.'
			self.errdlg(errmsg)
			return

		if not (qeven == 0.0 and qn > 0.0):
			errmsg = 'Split '+x+'-for-'+y+' shares of '+st+' result in uneven number of shares. Please sell all extra shares first.'
			self.errdlg(errmsg)
			return

		msg = wx.MessageDialog(self,'Split '+x+'-for-'+y+' shares of '+st+' on '+d+'.\nAfter split '+st+' balance will be '+str(qn)+' shares at '+p+' '+cn+'.','Add Stock Split?',wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
		rv = msg.ShowModal()
		msg.Destroy()
		if rv == wx.ID_NO:
			return

		num = self.dc.naccid(self.dc.GROUPS[2][3][1][0])
		if not(du.isint(num)):
			self.errdlg('Internal Error: Failed to create share!')
			return

		ditm = {}
		ditm['num'] = str(num)
		ditm['de'] = st
		ditm['c'] = cn
		ditma = ditm

		ditm = {}
		ditm['d'] = d
		ditm['p'] = p
		ditm['a'] = str(num)
		ditmq = ditm

		ditm = {}
		ditm['d'] = d
		ditm['de'] = 'Stock split '+st
		ditm['fs'] = s
		ditm['fq'] = q
		ditm['fp'] = a
		ditm['fc'] = '0'
		ditm['ts'] = str(num)
		ditm['tq'] = str(qn)
		ditm['tp'] = str(an)
		ditm['tc'] = '0'

		dict = self.dc.adict
		dict.addtodict(ditma)
		dict = self.dc.qdict
		dict.addtodict(ditmq)
		dict = self.dc.tdict
		dict.addtodict(ditm)

		self.splitx.SetValue('1')
		self.splity.SetValue('1')
		self.splitp.SetValue('1.0')

		rv = self.yesnotdlg('Copy and adjust share quotes?')
		if rv == wx.ID_YES:
			pd = wx.ProgressDialog('Copying and adjusting quotes','Please wait - this might take a while...',100,self)
			rv = self.dc.copyquotes(str(s),str(num),float(y)/float(x),pd)
			pd.Destroy()
			if not rv == True:
				self.errdlg('Internal Error: Failed to copy quotes!')
				return

		self.msgdlg('The stock split has been added to the project.')

	def portfoliopanel(self):
		group = self.dc.GROUPS[2][0]
		du = datautils_c()
		year = date.today().year
		fia = self.dc.getgroupsum(group,yto=year)
		cas = self.dc.getgroupsum(self.dc.GROUPS[2][3][0][0],yto=year)
		groups = self.creategrouplist('ASSETSNOACCOUNT')[0]
		base = self.dc.getbasecurrency()
		assets = []
		hl = 0
		assets.append(['Stock Portfolio ('+str(int(year))+')'.title(),'','','','','','','',''])
		assets.append(['','','','','','','','',''])
		for g in groups:
			gsum = self.dc.getgroupsum(g,yto=year)
			if gsum == 0:
				continue
			assets.extend(self.dc.getdassets(g,yto=year,totsum=1,yoy=1,apps=1))
			assets.append(['','','',du.rstr(100*gsum/fia,1)+'%','','','','',''])
			assets.append(['','','','','','','','',''])
		assets.append(['Total'+' '+self.dc.GROUPS[2][3][0][0].title(),'','',du.rstr(cas,0)+' '+base,'','','','',''])
		assets.append(['','','',du.rstr(100*cas/fia,1)+'%','','','','',''])
		assets.append(['','','','','','','','',''])
		assets.append(['Total Portfolio Value'.title(),'','',du.rstr(fia,0)+' '+base,'','','','',''])
		columns = []
		columns.append('Description')
		columns.append('Shares')
		columns.append('Price')
		columns.append('Sum')
		columns.append('0-3 mo')
		columns.append('3-6 mo')
		columns.append('6-12 mo')
		columns.append('Avg Price')
		columns.append('Profit/Loss')
		self.createlistctrl(assets,columns,highlight=len(assets))

	def transactionhist(self,attr=[]):
		du = datautils_c()
		year0 = date.today().year
		groups = self.creategrouplist('ASSETSNOACCOUNT')[0]
		assets = []
		for i in range(3):
			year = year0 - i
			#self.dc.getdtransactionhist(groups[0],yfrom=year,yto=year,trtype='buy')
			sales = []
			buys = []
			for g in groups:
				sales.extend(self.dc.getdtransactionhist(g,yfrom=year,yto=year,trtype='sell'))
				buys.extend(self.dc.getdtransactionhist(g,yfrom=year,yto=year,trtype='buy'))
			assets.append(['Transaction History'.title(),'('+str(int(year))+')'.title(),'','','','','',''])
			assets.append(['','','','','','','',''])
			assets.append(['Sold','','Shares','Price','Commission','','Profit/Loss',''])
			if len(sales) == 0:
				assets.append(['','None.','','','','','',''])
			else:
				assets.extend(sales)
			assets.append(['','','','','','','',''])
			assets.append(['Bought','','Shares','Price','Commission','','Avg Price',''])
			if len(buys) == 0:
				assets.append(['','None.','','','','','',''])
			else:
				assets.extend(buys)
			assets.append(['','','','','','','',''])
		columns = []
		columns = ['','','','','','','','']
		#columns.append('Transaction Dates')
		#columns.append('Name')
		#columns.append('Shares')
		#columns.append('Price')
		#columns.append('Commission')
		#columns.append('Sum')
		#columns.append('Profit/Loss')
		#columns.append('Profit/Loss')
		self.createlistctrl(assets,columns)

	# Copied from pbalance_c.py
	def createassetspanel(self,group):
		groups = self.dc.getgrouplabels(group)
		assets = []
		for g in groups:
			assets.extend(self.dc.getdassets(g,totsum=0))
		columns = []
		columns.append('Description')
		columns.append('Quantity')
		columns.append('Price')
		columns.append('Sum')
		#self.createlistctrl(assets,columns,highlight=len(assets))
		self.createlistctrl(assets,columns)

	def createassetsplot(self,group):
		today = date.today()
		assets = []
		groups = []
		cashgrp = self.creategrouplist('ACCOUNT')[0]
		cash = self.dc.getdglvalues([cashgrp[0]])
		assets.append(cash[0])
		groups.append(cashgrp[0])
		grouplist = self.creategrouplist('ASSETSNOACCOUNT')[0]
		for g in grouplist:
			assetslist = self.dc.getdassets(g,basecurrency=0,totsum=0)
			if assetslist == []:
				continue
			for a in assetslist:
				assets.append(a[3])
				groups.append(a[0])
		self.createplot(self.PIEPLOT,assets,groups,'Stock Portfolio'+today.strftime(" (%Y-%m-%d)"))

	def createhassetspanel(self,group,year=0):
		du = datautils_c()
		columns = self.dc.getgrouplabels(group)
		values = self.dc.gethassets(columns,year=year)
		columns.append('Total')
		columns.append('%')
		base = self.dc.getbasecurrency()
		equ2 = 0
		for i in range(len(values)):
			equ = 0
			for j in range(len(values[i])-1):
				equ = equ+float(values[i][j+1])
				values[i][j+1] = values[i][j+1]+' '+base
			values[i].append(du.rstr(equ)+' '+base)
			if not equ2 == 0:
				equ2 = (equ-equ2)/equ2
			values[i].append(du.rstr(equ2*100,1)+' %')
			equ2 = equ
		values.reverse()
		self.createlistctrl(values,columns,highlight=1)

	def createhassetsplot(self,group,year=0):
		du = datautils_c()
		columns = self.dc.getgrouplabels(group)
		data = self.dc.gethassets(columns,year=year)
		values = []
		for i,c in enumerate(columns):
			values.append(self.getarraycolumn(data,i))
		self.createplot(self.LINEPLOT,values,columns,'Stock Portfolio',yearly=year)
