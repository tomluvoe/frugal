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

import os
import re

from datautils_c import datautils_c

class pimport_c(plugin_c):
	NAME = 'Import CSV'
	FUNCTIONS = ['Import CSV file']

	def __del__(self):
		pass

	# NO ATTR
	def createpanel(self,func='',attr=[]):
		self.func = func

		if(self.func == pimport_c.FUNCTIONS[0]):
			self.importpanel()
		else:
			self.emptypanel()
			return
		#self.acc.. returns coords for button?
		#self.innersizer.Add(button)

	def importpanel(self):
		todaysdate = date.today().strftime('%Y%m%d')

		column1 = []
		column2 = []

		self.accountst = self.createaccountlist(self.dc.GROUPS[2][3][0][0])
		self.accounts = self.choicelist(self.accountst[1])
		column1.append(self.statictext('CSV account'))
		column2.append(self.accounts)
		
		btn = wx.Button(self,-1,'Select file')
		self.Bind(wx.EVT_BUTTON,self.handleselbutton,btn)
		column1.append(btn)
		column2.append(self.statictext(''))

		self.createsizercols([column1,column2])


	def handleselbutton(self,event):
		dialog = wx.FileDialog(self, 'Choose csv file', '.', '', '*.csv', wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			file = dialog.GetFilename()
			path = dialog.GetDirectory()
			#self.owner.importcsv(path,file)
		dialog.Destroy()

		if self.func == pimport_c.FUNCTIONS[0]:
			self.importcsv(path,file)

	def importcsv(self,dir,file):
	# import csv file
		du = datautils_c()
		if self.dc.tdict.dataok == False:
			return False
		filename = os.path.join(dir,file)
		if not os.path.exists(filename):
			return False
		f = open(filename,'r')
		lines = f.readlines()
		f.close

		sel = self.accounts.GetCurrentSelection()
		acc = self.accountst[0][sel]
		accn = self.accountst[1][sel]
		expenselist = self.createaccountlist(self.dc.GROUPS[1][0])
		incomelist = self.createaccountlist(self.dc.GROUPS[0][0])
		accountslist = self.createaccountlist2(self.creategrouplist('ACCOUNTLIABILITIES')[0])

		explist = [[],[]]
		explist[0] = expenselist[0] + accountslist[0]
		explist[1] = expenselist[1] + accountslist[1]
		
		inclist = [[],[]]
		inclist[0] = incomelist[0] + accountslist[0]
		inclist[1] = incomelist[1] + accountslist[1]

		for i,l in enumerate(lines):
			ditm = {}

			l = re.sub('"','',l)
			l = re.sub('\s+',' ',l)
			itm = l.split(';')
			a = float(itm[-1])
			asign = a

			if asign < 0:
				ditm['fs'] = acc
				acclist = explist
				a = -a
			else:
				ditm['ts'] = acc
				acclist = inclist
			
			breaknow = False
			while True:
				dialog = wx.SingleChoiceDialog(None,'('+str(i+1)+'/'+str(len(lines))+') '+itm[0]+' '+itm[1]+' '+str(asign),'Select cost or account',acclist[1])

				if dialog.ShowModal() == wx.ID_OK:
					acc1 = acclist[0][dialog.GetSelection()]
				else:
					dialog.Destroy()
					breaknow = True
					break
				dialog.Destroy()

				if not self.dc.accissamecurrency(acc,acc1):
					errmsg = 'Both accounts must be of the same currency!'
					self.errdlg(errmsg)
				else:
					break

			if breaknow == True:
				break

			if asign < 0:
				ditm['ts'] = acc1
			else:
				ditm['fs'] = acc1

			itm[0] = re.sub('-','',itm[0])
			ditm['d'] = itm[0]
			ditm['de'] = itm[1]
			ditm['fq'] = str(a)
			ditm['fp'] = '1'
			ditm['fc'] = '0'
			ditm['tq'] = str(a)
			ditm['tp'] = '1'
			ditm['tc'] = '0'
			#print ditm

			if not du.isint(ditm['d']):
				errmsg = 'The date is not an integer value! Skip to next transaction.'
				self.errdlg(errmsg)
				continue
			stdmsg = 'The transaction has been added to the program.'
			if not (du.isint(ditm['fs']) and du.isfloat(ditm['fq']) and du.isfloat(ditm['fp']) and du.isfloat(ditm['fc'])):
				errmsg = 'Amount is not a floating point value!  Skip to next transaction.'
				self.errdlg(errmsg)
				continue
			if not (du.isint(ditm['ts']) and du.isfloat(ditm['tq']) and du.isfloat(ditm['tp']) and du.isfloat(ditm['tc'])):
				errmsg = 'Amount is not a floating point value!  Skip to next transaction.'
				self.errdlg(errmsg)
				continue

			dict = self.dc.tdict
			dict.addtodict(ditm)
			#self.msgdlg(stdmsg)

