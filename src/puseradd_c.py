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

class puseradd_c(plugin_c):
	NAME = 'Add Transactions'
	FUNCTIONS = ['Simple Income','Simple Expense','Transfer Money','Buy / Sell Share']

	def __del__(self):
		pass

	# NO ATTR
	def createpanel(self,func='',attr=[]):
		self.func = func

		if(self.func == puseradd_c.FUNCTIONS[0]):
			self.transactionpanel()
		elif(self.func == puseradd_c.FUNCTIONS[1]):
			self.transactionpanel()
		elif(self.func == puseradd_c.FUNCTIONS[2]):
			self.transactionpanel()
		elif(self.func == puseradd_c.FUNCTIONS[3]):
			self.transactionpanel()
		else:
			self.emptypanel()
			return
		#self.acc.. returns coords for button?
		#self.innersizer.Add(button)

	def transactionpanel(self):
		todaysdate = date.today().strftime('%Y%m%d')

		column1 = []
		column2 = []
		column1.append(self.statictext('Date'))
		column1.append(self.statictext('Description'))
		self.date = self.datepicker()
		self.desc = self.textctrl(wide=True)
		column2.append(self.date)
		column2.append(self.desc)

		if self.func == puseradd_c.FUNCTIONS[0]:
			self.accountsf = self.createaccountlist(self.dc.GROUPS[0][0])
			self.accountst = self.createaccountlist(self.dc.GROUPS[2][3][0][0])
			self.fshare = self.choicelist(self.accountsf[1])
			self.tshare = self.choicelist(self.accountst[1])
			self.amount = self.textctrl()
			column1.append(self.statictext('Source'))
			column1.append(self.statictext('Account'))
			column1.append(self.statictext('Amount'))
			column2.append(self.fshare)
			column2.append(self.tshare)
			column2.append(self.amount)
		elif self.func == puseradd_c.FUNCTIONS[1]:
			self.accountsf = self.createaccountlist(self.dc.GROUPS[2][3][0][0])
			self.accountst = self.createaccountlist(self.dc.GROUPS[1][0])
			self.fshare = self.choicelist(self.accountsf[1])
			self.tshare = self.choicelist(self.accountst[1])
			self.amount = self.textctrl()
			column1.append(self.statictext('Account'))
			column1.append(self.statictext('Expense group'))
			column1.append(self.statictext('Amount'))
			column2.append(self.fshare)
			column2.append(self.tshare)
			column2.append(self.amount)
		elif self.func == puseradd_c.FUNCTIONS[2]:
			self.accountsf = self.createaccountlist2(self.creategrouplist('ACCOUNTLIABILITIES')[0])
			self.accountst = self.createaccountlist2(self.creategrouplist('ACCOUNTLIABILITIES')[0])
			self.fshare = self.choicelist(self.accountsf[1])
			self.tshare = self.choicelist(self.accountst[1])
			self.amount = self.textctrl()
			column1.append(self.statictext('Transfer from'))
			column1.append(self.statictext('Transfer to'))
			column1.append(self.statictext('Amount'))
			column2.append(self.fshare)
			column2.append(self.tshare)
			column2.append(self.amount)
		elif self.func == puseradd_c.FUNCTIONS[3]:
			self.trtype = self.choicelist(['Buy','Sell'])
			self.accountsf = self.createaccountlist(self.dc.GROUPS[2][3][0][0])
			self.accountst = self.createaccountlist2(self.creategrouplist('ASSETSNOACCOUNT')[0])
			self.fshare = self.choicelist(self.accountsf[1])
			self.tshare = self.choicelist(self.accountst[1])
			self.price = self.textctrl()
			self.quantity = self.textctrl()
			self.commission = self.textctrl()
			column1.append(self.statictext('Transaction type'))
			column1.append(self.statictext('Account'))
			column1.append(self.statictext('Share'))
			column1.append(self.statictext('Share price'))
			column1.append(self.statictext('Number of shares'))
			column1.append(self.statictext('Commission'))
			column2.append(self.trtype)
			column2.append(self.fshare)
			column2.append(self.tshare)
			column2.append(self.price)
			column2.append(self.quantity)
			column2.append(self.commission)

		btn = wx.Button(self,-1,'Add')
		self.Bind(wx.EVT_BUTTON,self.handleaddbutton,btn)
		column1.append(btn)

		self.createsizercols([column1,column2])


	def handleaddbutton(self,event):
		if self.func == puseradd_c.FUNCTIONS[0]:
			self.addtransaction()
		elif self.func == puseradd_c.FUNCTIONS[1]:
			self.addtransaction()
		elif self.func == puseradd_c.FUNCTIONS[2]:
			self.addtransaction()
		elif self.func == puseradd_c.FUNCTIONS[3]:
			self.addtransaction()

	def addtransaction(self):
		du = datautils_c()

		ditm = {}
		ditm['d'] = self.datepicker_getdate(self.date)
		ditm['de'] = self.desc.GetLineText(0)

		if self.func == puseradd_c.FUNCTIONS[0] or self.func == puseradd_c.FUNCTIONS[1] or self.func == puseradd_c.FUNCTIONS[2]:
			sel = self.fshare.GetCurrentSelection()
			ditm['fs'] = self.accountsf[0][sel]
			ditm['fq'] = self.amount.GetLineText(0)
			ditm['fp'] = '1'
			ditm['fc'] = '0'
			sel = self.tshare.GetCurrentSelection()
			ditm['ts'] = self.accountst[0][sel]
			ditm['tq'] = self.amount.GetLineText(0)
			ditm['tp'] = '1'
			ditm['tc'] = '0'
		elif self.func == puseradd_c.FUNCTIONS[3]:
			trtype = self.trtype.GetCurrentSelection()
			sel = self.fshare.GetCurrentSelection()
			fs = self.accountsf[0][sel]
			sel = self.tshare.GetCurrentSelection()
			ts = self.accountst[0][sel]
			qu = self.quantity.GetLineText(0)
			pr = self.price.GetLineText(0)
			co = self.commission.GetLineText(0)
			# EXTRA CHECK IN THIS CASE
			if not du.isfloat(qu) or not du.isfloat(pr) or not du.isfloat(co):
				errmsg = 'Price, number of shares and commission must be floating point values! Type as 0.0'
				self.errdlg(errmsg)
				return
			if trtype == 0:
				ditm['fs'] = fs
				ditm['fq'] = str(float(qu)*float(pr))
				ditm['fp'] = '1'
				ditm['fc'] = co
				ditm['ts'] = ts
				ditm['tq'] = qu
				ditm['tp'] = pr
				ditm['tc'] = '0'
			else:
				ditm['fs'] = ts
				ditm['fq'] = qu
				ditm['fp'] = pr
				ditm['fc'] = '0'
				ditm['ts'] = fs
				ditm['tq'] = str(float(qu)*float(pr))
				ditm['tp'] = '1'
				ditm['tc'] = co
			if not self.dc.accissamecurrency(ditm['fs'],ditm['ts']):
				errmsg = 'Account and share must be of the same currency!'
				self.errdlg(errmsg)
				return
		else:
			return

		stdmsg = 'The transaction has been added to the program.'
		if not self.dc.accissamecurrency(ditm['fs'],ditm['ts']):
			errmsg = 'Both accounts must be of the same currency!'
			self.errdlg(errmsg)
			return
		if not du.isint(ditm['d']):
			errmsg = 'The date is not an integer value! Type as YYYYMMDD'
			self.errdlg(errmsg)
			return
		if not (du.isint(ditm['fs']) and du.isfloat(ditm['fq']) and du.isfloat(ditm['fp']) and du.isfloat(ditm['fc'])):
			errmsg = 'Amount is not a floating point value! Type as 0.0'
			self.errdlg(errmsg)
			return
		if not (du.isint(ditm['ts']) and du.isfloat(ditm['tq']) and du.isfloat(ditm['tp']) and du.isfloat(ditm['tc'])):
			errmsg = 'Amount is not a floating point value! Type as 0.0'
			self.errdlg(errmsg)
			return

		dict = self.dc.tdict
		dict.addtodict(ditm)
		self.msgdlg(stdmsg)

		self.desc.SetValue('')
		if self.func == puseradd_c.FUNCTIONS[0] or self.func == puseradd_c.FUNCTIONS[1] or self.func == puseradd_c.FUNCTIONS[2]:
			self.amount.SetValue('')
		elif self.func == puseradd_c.FUNCTIONS[3]:
			self.price.SetValue('')
			self.commission.SetValue('')
			self.quantity.SetValue('')
