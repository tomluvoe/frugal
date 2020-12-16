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

import wx
from datetime import date
from plugin_c import plugin_c

from datautils_c import datautils_c

class padddata_c(plugin_c):
	NAME = 'Add Data'
	FUNCTIONS = ['Add Bank Account','Add Transaction (detailed)','Add Stock Quotes','Add Currency Rates','Add Share','Add Asset / Liability','Add Currency']

	def __del__(self):
		pass

	# NO ATTR
	def createpanel(self,func='',attr=[]):
		self.func = func

		if(self.func == padddata_c.FUNCTIONS[1]):
			self.transactionpanel()
		elif(self.func == padddata_c.FUNCTIONS[3]):
			self.currencypanel()
		elif(self.func == padddata_c.FUNCTIONS[2]):
			self.quotepanel()
		elif(self.func == padddata_c.FUNCTIONS[0]):
			self.accountpanel()
		elif(self.func == padddata_c.FUNCTIONS[4]):
			self.accountpanel()
		elif(self.func == padddata_c.FUNCTIONS[5]):
			self.accountpanel()
		elif(self.func == padddata_c.FUNCTIONS[6]):
			self.addcurrencypanel()
		else:
			self.emptypanel()
			return
		#self.acc.. returns coords for button?
		#self.innersizer.Add(button)

	def addcurrencypanel(self):
		column1 = []
		column2 = []

		base = self.dc.getbasecurrency()

		column1.append(self.statictext('Select currency'))
		column1.append(self.statictext('Currency rate ['+base+']'))

		self.cname = self.choicelist(self.dc.ALLOWEDCURRENCIES)
		self.crate = self.textctrl('1.0')

		column2.append(self.cname)
		column2.append(self.crate)

		btn0 = wx.Button(self,-1,'Get latest rate from the internet')
		self.Bind(wx.EVT_BUTTON,self.handleecbbutton,btn0)
		column1.append(btn0)
		btn1 = wx.Button(self,-1,'Add')
		self.Bind(wx.EVT_BUTTON,self.handleaddcbutton,btn1)
		column1.append(btn1)

		self.createsizercols([column1,column2])

	def transactionpanel(self):
		todaysdate = date.today().strftime('%Y%m%d')
		self.accounts = self.createaccountlist()

		column1 = []
		column2 = []

		column1.append(self.statictext('Date'))
		column1.append(self.statictext('Description'))
		column1.append(self.statictext('Source share'))
		column1.append(self.statictext('Source quantity [0.0]'))
		column1.append(self.statictext('Source price [0.0]'))
		column1.append(self.statictext('Source commission [0.0]'))
		column1.append(self.statictext('Destination share'))
		column1.append(self.statictext('Destination quantity [0.0]'))
		column1.append(self.statictext('Destination price [0.0]'))
		column1.append(self.statictext('Destination commission [0.0]'))

		self.date = self.datepicker()
		self.desc = self.textctrl(wide=True)
		self.fshare = self.choicelist(self.accounts[1])
		self.fquant = self.textctrl()
		self.fprice = self.textctrl()
		self.fcommi = self.textctrl()
		self.tshare = self.choicelist(self.accounts[1])
		self.tquant = self.textctrl()
		self.tprice = self.textctrl()
		self.tcommi = self.textctrl()

		column2.append(self.date)
		column2.append(self.desc)
		column2.append(self.fshare)
		column2.append(self.fquant)
		column2.append(self.fprice)
		column2.append(self.fcommi)
		column2.append(self.tshare)
		column2.append(self.tquant)
		column2.append(self.tprice)
		column2.append(self.tcommi)

		btn = wx.Button(self,-1,'Add')
		self.Bind(wx.EVT_BUTTON,self.handleaddbutton,btn)
		column1.append(btn)

		self.createsizercols([column1,column2])

	#TODO REFACTOR
	def currencypanel(self):
		todaysdate = date.today().strftime('%Y%m%d')
		values = []
		columns = ['Currency','Date','Quote','Latest']
		cn = 0
		base = self.dc.getbasecurrency()
		for c in self.dc.cdlist:
			lrate = self.dc.getlatestrate(c)
			if c == base:
				values.append([c,'N/A','N/A','(N/A)'])
			else:
				values.append([c,todaysdate,'----------','('+lrate[1]+' '+base+' - '+lrate[0]+')'])
			cn = cn + 1
		values.append(['','','',''])
		values.append(['Add','','',''])
		cn = cn + 2
		self.createlistctrl(values,columns,highlight=cn,edit=1,select=1)

	#TODO REFACTOR
	def handlelistctrlselect(self,event):
		du = datautils_c()
		#idx = event.m_itemIndex
		idx = event.GetIndex()
		col = event.m_col
		itm = event.m_item
		qts = 0
		if not itm.GetText() == 'Add':
			return
		if self.func == padddata_c.FUNCTIONS[2]: # QUOTES
			dict = self.dc.qdict
			numitm = self.lc.GetItemCount()
			for i in range(numitm):
				ditm = {}
				nam = self.lc.GetItem(i,0).GetText()
				ditm['d'] = self.lc.GetItem(i,1).GetText()
				ditm['p'] = self.lc.GetItem(i,2).GetText()
				if not (du.isint(ditm['d']) and du.isfloat(ditm['p'])):
					continue
				ditm['a'] = self.lc.GetItem(i,5).GetText()
				if not (du.isint(ditm['a'])):
					continue
				if int(ditm['a']) == 0:
					continue
				dict.addtodict(ditm)
				qts = qts + 1
			stdmsg = str(qts)+' quote(s) added to project.'
		elif self.func == padddata_c.FUNCTIONS[3]: # CURRENCY
			dict = self.dc.cdict
			numitm = self.lc.GetItemCount()
			for i in range(numitm):
				ditm = {}
				ditm['c'] = self.lc.GetItem(i,0).GetText()
				ditm['d'] = self.lc.GetItem(i,1).GetText()
				ditm['p'] = self.lc.GetItem(i,2).GetText()
				if not (du.isint(ditm['d']) and du.isfloat(ditm['p'])):
					continue
				dict.addtodict(ditm)
				qts = qts + 1
			stdmsg = str(qts)+' currency rate(s) added to project.'
		self.msgdlg(stdmsg)

	#TODO REFACTOR
	def quotepanel(self):
		#groups = self.dc.getallgrouplabels()
		groups = self.creategrouplist('ASSETSNOACCOUNTLIABILITIES')[0]
		todaysdate = date.today().strftime('%Y%m%d')
		values = []
		columns = ['Asset name','Date','Quote','Currency','Latest','ID']
		gn = 0
		for g in groups:
			assets = self.dc.getdassets(g,mini=2)
			for a in assets:
				aid = a[1]
				if aid == 0:
					cnam = ''
					lquo = self.dc.getlatestquote()
				else:
					cid = self.dc.acccurrency(eval(aid))
					cnam = self.dc.cdlist[cid]
					lquo = self.dc.getlatestquote(aid)
				values.append([a[0],todaysdate,'----------',cnam,'('+lquo[1]+' '+cnam+' - '+lquo[0]+')',aid])
				gn = gn + 1
		values.append(['','','','',''])
		values.append(['Add','','','',''])
		gn = gn + 2
		self.createlistctrl(values,columns,highlight=gn,edit=1,select=1,zerowidth=5)

	def accountpanel(self):
		self.currencies = self.createcurrencylist()
		todaysdate = date.today().strftime('%Y%m%d')

		column1 = []
		column2 = []

		self.acco = self.textctrl(wide=True)
		self.acur = self.choicelist(self.currencies)
		self.adat = self.datepicker()
		btn = wx.Button(self,-1,'Add')
		self.Bind(wx.EVT_BUTTON,self.handleaddbutton,btn)

		if self.func == padddata_c.FUNCTIONS[0]:
			column1.append(self.statictext('Account name'))
			column1.append(self.statictext('Account currency'))
			column1.append(self.statictext('Opening balance [0.0]'))
			column1.append(self.statictext('Opening date'))
			self.abal = self.textctrl('0.0')
		elif self.func == padddata_c.FUNCTIONS[4]:
			self.groups = self.creategrouplist('ASSETSNOACCOUNT')
			column1.append(self.statictext('Share symbol / ticker'))
			column1.append(self.statictext('Share type'))
			column1.append(self.statictext('Share currency'))
			column1.append(self.statictext('Initial date'))
			column1.append(self.statictext('Initial price [1.0]'))
			column1.append(self.statictext('Initial balance [0.0]'))
			column1.append(self.statictext(''))
			self.abal = self.textctrl('0.0')
			self.apri = self.textctrl('1.0')
			yhobtn = wx.Button(self,-1,'Get latest price from the internet')
			self.Bind(wx.EVT_BUTTON,self.handleyhobutton,yhobtn)
			self.atyp = self.choicelist(self.groups[0])
		elif self.func == padddata_c.FUNCTIONS[5]:
			self.groups = self.creategrouplist('ASSETSLIABILITIES')
			column1.append(self.statictext('Asset / Liability name'))
			column1.append(self.statictext('Asset / Liability type'))
			column1.append(self.statictext('Asset / Liability currency'))
			column1.append(self.statictext('Opening balance [0.0]'))
			column1.append(self.statictext('Opening date'))
			column1.append(self.statictext('Initial price [1.0]'))
			self.abal = self.textctrl('0.0')
			self.atyp = self.choicelist(self.groups[0])
			self.apri = self.textctrl('1.0')

		if self.func == padddata_c.FUNCTIONS[0]:
			column2.append(self.acco)
			column2.append(self.acur)
			column2.append(self.abal)
			column2.append(self.adat)
		elif self.func == padddata_c.FUNCTIONS[4]:
			column2.append(self.acco)
			column2.append(self.atyp)
			column2.append(self.acur)
			column2.append(self.adat)
			column2.append(self.apri)
			column2.append(self.abal)
			column1.append(yhobtn)
		elif self.func == padddata_c.FUNCTIONS[5]:
			column2.append(self.acco)
			column2.append(self.atyp)
			column2.append(self.acur)
			column2.append(self.abal)
			column2.append(self.adat)
			column2.append(self.apri)

		column1.append(btn)
		column2.append(self.statictext(''))

		self.createsizercols([column1,column2])

	def handleaddbutton(self,event):
		if self.func == padddata_c.FUNCTIONS[1]:
			self.addtransaction()
		elif self.func == padddata_c.FUNCTIONS[0]:
			self.addaccount()
		elif self.func == padddata_c.FUNCTIONS[4]:
			self.addaccount()
		elif self.func == padddata_c.FUNCTIONS[5]:
			self.addaccount()

	def handleaddcbutton(self,event):
		du = datautils_c

		#todaysdate = date.today().strftime('%Y%m%d')
		cdate = '19700101'
		cname = self.cname.GetStringSelection()
		crate = self.crate.GetLineText(0)

		dict = self.dc.cdict
		ditm = {}
		ditm['d'] = cdate
		ditm['c'] = cname
		ditm['p'] = crate
		dict.addtodict(ditm)
		stdmsg = 'The currency has been added to the project.'
		self.msgdlg(stdmsg)

	def handleecbbutton(self,event):
		currency = self.cname.GetStringSelection()
		rate = self.dc.getecbrate(currency)
		errmsg = 'Online currency rate failed!'
		if float(rate) == 0.0:
			self.errdlg(errmsg)
		else:
			self.crate.SetValue(rate)

	def handleyhobutton(self,event):
		symbol = self.acco.GetLineText(0)
		quote = self.dc.getonlinequote(symbol)
		errmsg = 'The share symbol / ticker was not found on online or service unavailable. Automatic quote update will not work for this symbol.'
		if float(quote) == 0.0:
			self.errdlg(errmsg)
		else:
			self.apri.SetValue(quote)

	def addtransaction(self):
		du = datautils_c()

		ditm = {}
		ditm['d'] = self.datepicker_getdate(self.date)
		ditm['de'] = self.desc.GetLineText(0)
		sel = self.fshare.GetCurrentSelection()
		ditm['fs'] = self.accounts[0][sel]
		ditm['fq'] = self.fquant.GetLineText(0)
		ditm['fp'] = self.fprice.GetLineText(0)
		ditm['fc'] = self.fcommi.GetLineText(0)
		sel = self.tshare.GetCurrentSelection()
		ditm['ts'] = self.accounts[0][sel]
		ditm['tq'] = self.tquant.GetLineText(0)
		ditm['tp'] = self.tprice.GetLineText(0)
		ditm['tc'] = self.tcommi.GetLineText(0)

		if not du.isint(ditm['d']):
			errmsg = 'The date is not an integer value! Type as YYYYMMDD'
			self.errdlg(errmsg)
			return
		if not (du.isint(ditm['fs']) and du.isfloat(ditm['fq']) and du.isfloat(ditm['fp']) and du.isfloat(ditm['fc'])):
			errmsg = 'From data is not correct! Type as numbers. Floating point as 0.0.'
			self.errdlg(errmsg)
			return
		if not (du.isint(ditm['ts']) and du.isfloat(ditm['tq']) and du.isfloat(ditm['tp']) and du.isfloat(ditm['tc'])):
			errmsg = 'To data is not correct! Type as numbers. Floating point as 0.0.'
			self.errdlg(errmsg)
			return

		dict = self.dc.tdict
		dict.addtodict(ditm)
		stdmsg = 'The transaction has been added to the project.'
		self.msgdlg(stdmsg)

		self.desc.SetValue('')
		self.fquant.SetValue('')
		self.fprice.SetValue('')
		self.fcommi.SetValue('')
		self.tquant.SetValue('')
		self.tprice.SetValue('')
		self.tcommi.SetValue('')


	def addaccount(self):
		du = datautils_c()

		if self.func == padddata_c.FUNCTIONS[0]:
			atyp = self.dc.GROUPS[2][3][0][0]
			desc = self.acco.GetLineText(0)
			sel = self.acur.GetCurrentSelection()
			acur = self.currencies[sel]
			apri = '1'
			abal = self.abal.GetLineText(0)
			adat = self.datepicker_getdate(self.adat)
		elif self.func == padddata_c.FUNCTIONS[4]:
			desc = self.acco.GetLineText(0)
			sel = self.atyp.GetCurrentSelection()
			atyp = self.groups[1][sel]
			sel = self.acur.GetCurrentSelection()
			acur = self.currencies[sel]
			adat = self.datepicker_getdate(self.adat)
			abal = self.abal.GetLineText(0)
			apri = self.apri.GetLineText(0)
		elif self.func == padddata_c.FUNCTIONS[5]:
			desc = self.acco.GetLineText(0)
			sel = self.atyp.GetCurrentSelection()
			atyp = self.groups[1][sel]
			sel = self.acur.GetCurrentSelection()
			acur = self.currencies[sel]
			apri = self.apri.GetLineText(0)
			abal = self.abal.GetLineText(0)
			adat = self.datepicker_getdate(self.adat)

		num = self.dc.naccid(atyp)
		errmsg = 'Internal Error: Failed to create share!'
		if not(du.isint(num)):
			self.errdlg(errmsg)
			return

		ditm = {}
		ditm['num'] = str(num)
		ditm['de'] = desc
		ditm['c'] = acur
		ditma = ditm

		ditm = {}
		ditm['d'] = adat
		ditm['p'] = apri
		ditm['a'] = str(num)
		if not(du.isint(ditm['d'])):
			errmsg = 'The date is not an integer value! Type as YYYYMMDD'
			self.errdlg(errmsg)
			return
		if not(du.isfloat(ditm['p'])):
			errmsg = 'Price is not a floating point value! Type as 0.0'
			self.errdlg(errmsg)
			return
		ditmq = ditm

		ditm = {}
		ditm['d'] = adat
		ditm['de'] = 'Opening balance'
		ditm['fs'] = '0'
		ditm['fq'] = '0'
		ditm['fp'] = '0'
		ditm['fc'] = '0'
		ditm['ts'] = str(num)
		ditm['tq'] = abal
		ditm['tp'] = apri
		ditm['tc'] = '0'
		if not(du.isfloat(ditm['tq'])) or not(du.isfloat(ditm['tp'])):
			errmsg = 'Either initial balance or price is not a floating point value! Type as 0.0'
			self.errdlg(errmsg)
			return

		dict = self.dc.adict
		dict.addtodict(ditma)
		dict = self.dc.qdict
		dict.addtodict(ditmq)
		dict = self.dc.tdict
		dict.addtodict(ditm)

		if self.func == padddata_c.FUNCTIONS[0]:
			self.acco.SetValue('')
			self.abal.SetValue('0.0')
			stdmsg = 'The account has been added to the project.'
		elif self.func == padddata_c.FUNCTIONS[4]:
			self.acco.SetValue('')
			self.apri.SetValue('1.0')
			stdmsg = 'The share has been added to the project.'
		elif self.func == padddata_c.FUNCTIONS[5]:
			self.acco.SetValue('')
			self.apri.SetValue('1.0')
			self.abal.SetValue('0.0')
			stdmsg = 'The asset or liability has been added to the project.'
		self.msgdlg(stdmsg)
