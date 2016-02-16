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

import sys

import api
import wx
import wxgui
import webbrowser
import datetime

import utils

class frugal(wx.PySimpleApp):
# Application Initialization
	def OnInit(self):
		self.project_active = False
		self.api = api.api()
		self.utils = utils.utils()

		frametitle = self.api.getprogramname()
		
		wx.InitAllImageHandlers()
		self.frame = wxgui.FrugalFrame(None,-1,"")
		self.SetTopWindow(self.frame)
		self.frame.SetTitle(frametitle)
		self.frame.Show()

		self.shareframe = []

		self.configure_eventhandlers()

		if len(sys.argv) > 1:
			# assume path to project is first variable
			path = sys.argv[1]
			self.tool_openproject(path)

		return True

	def configure_eventhandlers(self):
		wx.EVT_CLOSE(self, self.checksave)
		wx.EVT_MENU(self, wxgui.ID_NEW, self.evt_menu_new)
		wx.EVT_MENU(self, wxgui.ID_QUIT, self.evt_menu_quit)
		wx.EVT_MENU(self, wxgui.ID_OPEN, self.evt_menu_open)
		wx.EVT_MENU(self, wxgui.ID_SAVE, self.evt_menu_save)
		wx.EVT_MENU(self, wxgui.ID_SPLIT, self.evt_menu_split)
		wx.EVT_MENU(self, wxgui.ID_TRANSACTION, self.evt_menu_transaction)
		wx.EVT_TOOL(self, wxgui.ID_ADDINCOME, self.evt_tool_addincome)
		wx.EVT_MENU(self, wxgui.ID_ADDINCOMEMNU, self.evt_tool_addincome)
		wx.EVT_TOOL(self, wxgui.ID_ADDEXPENSE, self.evt_tool_addexpense)
		wx.EVT_MENU(self, wxgui.ID_ADDEXPENSEMNU, self.evt_tool_addexpense)
		wx.EVT_TOOL(self, wxgui.ID_TRANSFERMONEY, self.evt_tool_transfermoney)
		wx.EVT_MENU(self, wxgui.ID_TRANSFERMONEYMNU, self.evt_tool_transfermoney)
		wx.EVT_TOOL(self, wxgui.ID_BUYSELLSHARES, self.evt_tool_buysellshares)
		wx.EVT_MENU(self, wxgui.ID_BUYSELLSHARESMNU, self.evt_tool_buysellshares)
		wx.EVT_TOOL(self, wxgui.ID_RECALCULATE, self.evt_tool_recalculate)
		wx.EVT_MENU(self, wxgui.ID_RECALCULATEMNU, self.evt_tool_recalculate)
		wx.EVT_TOOL(self, wxgui.ID_DOWNLOADQUOTES, self.evt_tool_downloadquotes)
		wx.EVT_MENU(self, wxgui.ID_DOWNLOADQUOTESMNU, self.evt_tool_downloadquotes)
		wx.EVT_MENU(self, wxgui.ID_USERSGUIDE, self.evt_menu_usersguide)
		wx.EVT_MENU(self, wxgui.ID_ABOUT, self.evt_menu_about)
		wx.EVT_MENU(self, wxgui.ID_UPDATE, self.evt_notsupported)
		wx.EVT_MENU(self, wxgui.ID_ADDHOUSE, self.evt_notsupported)
		wx.EVT_MENU(self, wxgui.ID_ADDLIAB, self.evt_notsupported)
		wx.EVT_MENU(self, wxgui.ID_ADDQUOTES, self.evt_notsupported)
		wx.EVT_LIST_ITEM_ACTIVATED(self, wxgui.ID_PORTFOLIOLIST, self.evt_portfolio_activated)

	def error(self,message):
		dlg = wx.MessageDialog(self.frame,message,'Error!',wx.OK|wx.ICON_ERROR)
		rv = dlg.ShowModal()
		dlg.Destroy()
		return rv

	def info(self,message):
		dlg = wx.MessageDialog(self.frame,message,'Information',wx.OK|wx.ICON_INFORMATION)
		rv = dlg.ShowModal()
		dlg.Destroy()
		return rv

	def yesnocancel(self,message):
		dlg = wx.MessageDialog(self.frame,message,'Question',wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
		rv = dlg.ShowModal()
		dlg.Destroy()
		return rv

	def progress(self,message='Please wait while the program executes the command...'):
		pd = wx.ProgressDialog('Please wait',message)
		pd.Update(10)
		return pd
		

# Setup project
	def setup_project(self):
		self.setup_variables()
	
		self.currency = self.api.getcurrency()
		self.setup_balancesheet()
		self.setup_incomestatement()
		self.setup_stockportfolio()
		self.setup_budget()
		self.free_variables()

	def setup_variables(self):
		today = datetime.date.today()
		self.thismo = [today.timetuple()[0],today.timetuple()[1]]
		self.lastmo = self.getprevmonth(self.thismo[0],self.thismo[1])
		self.lastye = [self.thismo[0]-1,12]

		lastmonth = datetime.date(self.lastmo[0],self.lastmo[1],1)
		lastyear  = datetime.date(self.lastye[0],self.lastye[1],1)

		self.column = []
		self.column.append(today.strftime("%B %Y"))
		self.column.append(lastmonth.strftime("%B %Y"))
		self.column.append(lastyear.strftime("%B %Y"))
		self.column.append(today.strftime("%Y"))
		self.column.append(lastyear.strftime("%Y"))

		tmo = self.thismo
		lmo = self.lastmo
		lye = self.lastye

		# income statement
		self.incomehistory = self.api.getincomehistoryplot()

		self.revenues = []
		self.revenues.append(self.api.getrevenues(tmo[0],tmo[1]))
		self.revenues.append(self.api.getrevenues(lmo[0],lmo[1]))
		self.revenues.append(self.api.getrevenues(tmo[0]))
		self.revenues.append(self.api.getrevenues(int(tmo[0])-1))

		self.revenuegroups = []
		self.revenuegroups.append(self.api.getrevenuegroups(tmo[0],tmo[1]))
		self.revenuegroups.append(self.api.getrevenuegroups(lmo[0],lmo[1]))
		self.revenuegroups.append(self.api.getrevenuegroups(tmo[0]))
		self.revenuegroups.append(self.api.getrevenuegroups(int(tmo[0])-1))

		self.expenses = []
		self.expenses.append(self.api.getexpenses(tmo[0],tmo[1]))
		self.expenses.append(self.api.getexpenses(lmo[0],lmo[1]))
		self.expenses.append(self.api.getexpenses(tmo[0]))
		self.expenses.append(self.api.getexpenses(int(tmo[0])-1))

		self.expensegroups = []
		self.expensegroups.append(self.api.getexpensegroups(tmo[0],tmo[1]))
		self.expensegroups.append(self.api.getexpensegroups(lmo[0],lmo[1]))
		self.expensegroups.append(self.api.getexpensegroups(tmo[0]))
		self.expensegroups.append(self.api.getexpensegroups(int(tmo[0])-1))

		sum = [0.0,0.0]
		for i,e in enumerate(self.revenuegroups[2]):
			sum[0] = sum[0] + float(e[4])
			sum[1] = sum[1] + float(self.revenuegroups[3][i][4])
		self.revenuesum = sum

		sum = 0.0
		sum = [0.0,0.0]
		for i,e in enumerate(self.expensegroups[2]):
			sum[0] = sum[0] + float(e[4])
			sum[1] = sum[1] + float(self.expensegroups[3][i][4])
		self.expensesum = sum

		# balance sheet
		self.assets = []
		self.assets = self.api.getassets()
				
		self.assetssum = self.api.getassetssum(tmo[0])
		self.liabilitiessum = self.api.getliabilitiessum(tmo[0])
		
		self.assetslist = []
		self.assetslist.append(self.api.getassetssumlist(tmo[0]))
		self.assetslist.append(self.api.getassetssumlist(lmo[0],lmo[1]))
		self.assetslist.append(self.api.getassetssumlist(lye[0],lye[1]))

		self.assetshistory = self.api.getassetshistoryplot(False)
		self.assetshistory.append(self.api.getassetshistoryplot(True)[1])

		self.liabilitieshistory = self.api.getliabilitieshistoryplot(False)
		self.liabilitieshistory.append(self.api.getliabilitieshistoryplot(True)[1])

		self.histid = []
		self.histid.append(self.get_historyid(tmo[0],tmo[1],self.assetshistory[0]))
		self.histid.append(self.get_historyid(lmo[0],lmo[1],self.assetshistory[0]))
		self.histid.append(self.get_historyid(lye[0],lye[1],self.assetshistory[0]))

		# balance sheet and income statement
		self.equityhistory = self.api.getequityhistoryplot()
		self.equityhistorydiff = self.api.getequityhistoryplot(diff=True)
		
		# stock portfolio
		self.accounts = self.api.getaccounts()
		self.shares = self.api.getshares()
		self.mutualfunds = self.api.getmutualfunds()
		self.derivates = self.api.getderivates()
		self.bonds = self.api.getbonds()
		self.othercurrent = self.api.getothercurrent()
		self.liquidsum = self.api.getliquidssum()
		self.cassetssum = self.api.getcurrentassetssum(tmo[0])
		self.cliabilitiessum = self.api.getcurrentliabilitiessum(tmo[0])

		# transactions #TODO 
		self.accountslist = self.api.assetstolist(self.api.getaccounts(selcore=0,all=True),True,True)
		self.revenueslist = self.api.assetstolist(self.api.getrevenues(0,selcore=0),True,True)
		self.expenseslist = self.api.assetstolist(self.api.getexpenses(0,selcore=0),True,True)
		self.shareslist = self.api.assetstolist(self.api.getassetsminusaccounts(selcore=0,all=True),True,True)
				
	def get_historyid(self,year,month,list):
		for hid,l in enumerate(list):
			if int(l) == year*100+month:
				break
		return hid

	def free_variables(self):
		self.column = None
		self.thismo = None
		self.lastmo = None
		self.lastye = None
		#self.assets = None
		self.assetssum = None
		self.libailitiessum = None
		self.assetslist = None
		self.assetshistory = None
		self.liabilitieshistory = None
		self.equityhistory = None
		self.equityhistorydiff = None
		self.accounts = None
		self.shares = None
		self.mutualfunds = None
		self.derivates = None
		self.bonds = None
		self.othercurrent = None
		self.liquidsum = None

# Tools
	def getprevmonth(self,year,month):
		y0 = year
		m0 = month - 1
		if m0 < 1:
			m0 = 12
			y0 = year - 1
		return [y0,m0]
		
	def get_percentstr(self,f0,f1):
		if float(f1) == 0.0:
			return '- %'
		return str(round(100*(float(f0)-float(f1))/float(f1),1))+' %'

	def checksave(self,event):
		if self.api.issaved() == False:
			rv = self.yesnocancel('The project data is been modified.\nDo you want to save changes before exiting?')
			if rv == wx.ID_YES:
				self.api.save()
			elif rv == wx.ID_CANCEL:
				return False
		return True

	def checkisopen(self):
		return self.project_active 

# Event handlers
	def evt_menu_quit(self,event):
		if self.checksave(event) == False:
			return
		for sf in self.shareframe:
			if not type(sf) == wx._core._wxPyDeadObject:
				sf.Destroy()
		self.frame.Destroy()

	def evt_notsupported(self,event):
		self.error("Not supported in beta release!")

	def evt_menu_new(self,event):
		dlg = wx.DirDialog(self.frame,'Select new project directory','.',wx.DD_DEFAULT_STYLE)
		rv = dlg.ShowModal()
		path = dlg.GetPath()
		dlg.Destroy()
		if rv == wx.ID_OK:
			dlg = wx.SingleChoiceDialog(self.frame,'Choose project currency:','Currency',self.api.ALLOWEDCURRENCIES)
			if dlg.ShowModal() == wx.ID_OK:
				currency = dlg.GetStringSelection()
			else:
				currency = 'EUR'
			dlg.Destroy()
			pd = self.progress('Please wait while the new project is created...')
			rv = True
			if self.api.new(path,currency) == True:
				pd.Update(40)
				rv = self.tool_openproject(path,pd)
			else:
				rv = False
			pd.Destroy()
		if rv == False:
			self.error(self.api.error)
		return rv

	def tool_openproject(self,path,pd=False):
		if pd == False:
			pd = self.progress('Please wait while the project is opened...')
		rv = self.api.open(path)
		if rv == True:
			pd.Update(50)
			self.setup_project()
			pd.Update(90)
			pd.Destroy()
			self.project_active = True
			self.frame.SetTitle(self.api.getprogramname())
		else:
			pd.Destroy()
		if rv == False:
			self.error(self.api.error)
		return rv

	def evt_menu_open(self,event):
		opendlg = wx.DirDialog(self.frame,'Choose directory','.',wx.DD_DEFAULT_STYLE)
		rv = opendlg.ShowModal()
		path = opendlg.GetPath()
		opendlg.Destroy()
		if rv == wx.ID_OK:
			rv = self.tool_openproject(path)
		return rv

	def evt_menu_save(self,event):
		if not self.checkisopen() == True:
			self.error('Project not open. Can not save.')
			return False
		pd = self.progress('Please wait while the project data is stored to the disk...')
		rv = self.api.save()
		pd.Update(90)
		pd.Destroy()
		if not rv == True:
			self.error('Project save failed!')
		return rv

	def evt_menu_about(self,event):
		info = wx.AboutDialogInfo()
		about = self.api.getaboutinfo()
		info.SetName(about['name'])
		info.SetVersion(about['version'])
		info.SetDescription(about['description'])
		info.SetCopyright(about['copyright'])
		info.SetWebSite(about['website'])
		info.SetLicence(about['license'])
		info.AddDeveloper(about['developer'])
		wx.AboutBox(info)

	def evt_menu_usersguide(self,event):
		webbrowser.open('http://www.samoht.se/frugal/usersguide.php')

	def evt_menu_split(self,event):
		if not self.checkisopen() == True:
			return False
		self.shareframe.append(wxgui.SplitDialog(None,-1))
		sframe = self.shareframe[-1]
		sframe.combobox_assets.AppendItems(self.shareslist[0])
		sframe.combobox_assets.SetStringSelection(self.shareslist[0][0])
		if sframe.ShowModal() == wx.ID_OK:
			pd = self.progress('Please wait while the share is split...')
			date = sframe.datepicker_date.GetValue()
			datestr = date.FormatISODate()
			datetim = datetime.datetime.strptime(datestr,'%Y-%m-%d')			
			num = sframe.combobox_assets.GetCurrentSelection()
			num = self.shareslist[2][num]
			x = sframe.textctrl_x.GetValue()
			y = sframe.textctrl_y.GetValue()
			p = sframe.textctrl_price.GetValue()
			pd.Update(50)
			#print datestr,'x',x,'y',y,'p',p,num
			rv = self.api.splitasset(datetim,x,y,num,p)
			pd.Update(90)
			pd.Destroy()
			if rv == False:
				self.error(self.api.error)
			else:
				self.info('Stock split done. Please recalculate to see the change in project.')
		sframe.Destroy()
		return True

	def evt_menu_transaction(self,event):
		if not self.checkisopen() == True:
			return False
		self.shareframe.append(wxgui.GenericTransferDialog(None,-1))
		sframe = self.shareframe[-1]
		accounts = []
		accounts.append(self.accountslist[0])
		accounts.append(self.accountslist[1])
		accounts.append(self.accountslist[2])
		for i,s in enumerate(self.shareslist[0]):
			accounts[0].append(s)
			accounts[1].append(self.shareslist[1][i])
			accounts[2].append(self.shareslist[2][i])
		sframe.SetTitle('Transaction tool')
		sframe.combobox_toaccount.AppendItems(accounts[0])
		sframe.combobox_toaccount.SetStringSelection(accounts[0][0])
		sframe.textctrl_tocommission.SetValue('0.0')
		sframe.combobox_fromaccount.AppendItems(accounts[0])
		sframe.combobox_fromaccount.SetStringSelection(accounts[0][0])
		sframe.textctrl_fromcommission.SetValue('0.0')
		if sframe.ShowModal() == wx.ID_OK:
			desc = sframe.textctrl_description.GetValue()
			date = sframe.datepicker_date.GetValue()
			datestr = date.FormatISODate()
			datetim = datetime.datetime.strptime(datestr,'%Y-%m-%d')
			tacco = sframe.combobox_toaccount.GetCurrentSelection()
			tacco = accounts[2][tacco]
			tamou = sframe.textctrl_toamount.GetValue()
			tpric = sframe.textctrl_toprice.GetValue()
			tcomm = sframe.textctrl_tocommission.GetValue()
			facco = sframe.combobox_fromaccount.GetCurrentSelection()
			facco = accounts[2][facco]
			famou = sframe.textctrl_fromamount.GetValue()
			fpric = sframe.textctrl_fromprice.GetValue()
			fcomm = sframe.textctrl_fromcommission.GetValue()
			rv = self.api.addtransaction(datetim,desc,facco,famou,fpric,fcomm,tacco,tamou,tpric,tcomm)
			if rv == False:
				self.error('Add transaction failed!')
			else:
				self.info('Transaction added to project. Please recalculate to see the change in project.')
		sframe.Destroy()
		return True

	def create_new_asset_dlg(self,sframe,currency,type='ACCOUNT',price=1.0,datetim=datetime.datetime(1970, 1, 1, 12, 0, 0)):
		if type == 'SHARES':
			dlg = wx.TextEntryDialog(sframe,'Enter share name:','Create share', 'New share')
		else:
			dlg = wx.TextEntryDialog(sframe,'Enter account name:','Create account', 'New account')
		rv = dlg.ShowModal()
		de = dlg.GetValue()
		dlg.Destroy()
		if rv == wx.ID_OK:
			pd = self.progress('Please wait while the project data is calculated...')
			if type == 'SHARES':
				aid = self.api.addshare(de,price,currency,datetim)
			else:
				aid = self.api.addaccount(de,price,currency)
			pd.Update(90)
			pd.Destroy()
			if aid == False:
				rv = False
			else:
				rv = str(aid)
		return rv

	def evt_addtransaction_dlg(self,title,accounts,types):
		if self.checkisopen() == True and accounts and types:
			self.shareframe.append(wxgui.AddDialog(None,-1))
			sframe = self.shareframe[-1]
			sframe.SetTitle(title)
			a0 = self._listnewaccount(accounts)
			sframe.combobox_accounts.AppendItems(a0[0])
			sframe.combobox_accounts.SetStringSelection(a0[0][0])
			sframe.combobox_transactiontypes.AppendItems(types[0])
			sframe.combobox_transactiontypes.SetStringSelection(types[0][0])
			aid = False
			if sframe.ShowModal() == wx.ID_OK:
				desc = sframe.textctrl_description.GetValue()
				amou = sframe.textctrl_amount.GetValue()
				date = sframe.datepicker_date.GetValue()
				acco = sframe.combobox_accounts.GetCurrentSelection()
				tran = sframe.combobox_transactiontypes.GetCurrentSelection()
				aid = a0[2][acco]
				tid = types[2][tran]
				if int(aid) == 0:
					c = self.api.getaccountcurrency(tid)
					aid = self.create_new_asset_dlg(sframe,c)
			sframe.Destroy()
			if not aid == False:
				return [date,desc,amou,aid,tid]
		return False

	def tool_addincomeexpense(self,actiontxt,accountslist0,infomsg,reverse=False):
		list = self.evt_addtransaction_dlg(actiontxt,self.accountslist,accountslist0)
		if list == False:
			rv = False
		else:
			datestr = list[0].FormatISODate()
			datetim = datetime.datetime.strptime(datestr,'%Y-%m-%d')
			#print datetim,list[1],list[4],list[3],list[2]
			if reverse == True:
				fraccount = list[3]
				toaccount = list[4]
			else:
				fraccount = list[4]
				toaccount = list[3]
			rv = self.api.addsimpletransaction(datetim,list[1],fraccount,toaccount,list[2])
		if rv == False:
			self.error(actiontxt+' failed!')
		else:
			self.info(infomsg)
		return rv

	def evt_tool_addincome(self,event):
		rv = self.checkisopen()
		if rv == True:
			infotxt = 'Income added to project. Please recalculate to see the change in project.'
			rv = self.tool_addincomeexpense('Add income',self.revenueslist,infotxt)
		return rv
	
	def evt_tool_addexpense(self,event):
		rv = self.checkisopen()
		if rv == True:
			infotxt = 'Expense added to project. Please recalculate to see the change in project.'
			rv = self.tool_addincomeexpense('Add expense',self.expenseslist,infotxt,True)
		return rv
	
	def evt_tool_transfermoney(self,event):
		if not self.checkisopen() == True:
			return False
		self.shareframe.append(wxgui.TransferDialog(None,-1))
		sframe = self.shareframe[-1]
		sframe.SetTitle('Transfer money')
		sframe.combobox_fromaccount.AppendItems(self.accountslist[0])
		sframe.combobox_fromaccount.SetStringSelection(self.accountslist[0][0])
		a0 = self._listnewaccount(self.accountslist)
		sframe.combobox_toaccount.AppendItems(a0[0])
		sframe.combobox_toaccount.SetStringSelection(a0[0][0])
		if sframe.ShowModal() == wx.ID_OK:
			desc = sframe.textctrl_description.GetValue()
			amou = sframe.textctrl_amount.GetValue()
			date = sframe.datepicker_date.GetValue()
			facco = sframe.combobox_fromaccount.GetCurrentSelection()
			facco = self.accountslist[2][facco]
			tacco = sframe.combobox_toaccount.GetCurrentSelection()
			tacco = a0[2][tacco]
			datestr = date.FormatISODate()
			datetim = datetime.datetime.strptime(datestr,'%Y-%m-%d')
			rv = True
			if tacco == '0':
				c = self.api.getaccountcurrency(facco)
				tacco = self.create_new_asset_dlg(sframe,c)
				if tacco == False:
					errormsg = 'Add transaction failed! Create account failed.'
					rv = False
			if rv == True:
				if self.api.addsimpletransaction(datetim,desc,facco,tacco,amou) == False:
					rv = False
					errormsg = 'Add transaction failed!'
				else:
					self.info('Transacion added to project. Please recalculate to see the change in project.')
			if rv == False:
				self.error(errormsg)
		sframe.Destroy()
	
	def evt_tool_buysellshares(self,event):
		if not self.checkisopen() == True:
			return False
		self.shareframe.append(wxgui.ShareDialog(None,-1))
		sframe = self.shareframe[-1]
		sframe.SetTitle('Share transaction')
		ttypes = ['Buy','Sell']
		sframe.combobox_transactiontypes.AppendItems(ttypes)
		sframe.combobox_transactiontypes.SetStringSelection(ttypes[0])
		s0 = self._listnewshare(self.shareslist)
		sframe.combobox_shares.AppendItems(s0[0])
		sframe.combobox_shares.SetStringSelection(s0[0][0])
		a0 = self.accountslist
		sframe.combobox_accounts.AppendItems(a0[0])
		sframe.combobox_accounts.SetStringSelection(a0[0][0])
		if sframe.ShowModal() == wx.ID_OK:
			desc = sframe.textctrl_description.GetValue()
			date = sframe.datepicker_date.GetValue()
			datestr = date.FormatISODate()
			datetim = datetime.datetime.strptime(datestr,'%Y-%m-%d')
			comm = sframe.textctrl_commission.GetValue()
			quan = sframe.textctrl_quantity.GetValue()
			pric = sframe.textctrl_price.GetValue()
			type = sframe.combobox_transactiontypes.GetCurrentSelection()
			acco = sframe.combobox_accounts.GetCurrentSelection()
			acco = a0[2][acco]
			shar = sframe.combobox_shares.GetCurrentSelection()
			shar = s0[2][shar]
			rv = True
			if ttypes[type] == ttypes[0]:
				facco = acco
				famou = str(float(quan)*float(pric))
				fpric = 1.0
				fcomm = comm
				tacco = shar
				tamou = quan
				tpric = pric
				tcomm = 0.0
				if tacco == '0':
					c = self.api.getaccountcurrency(facco)
					tacco = self.create_new_asset_dlg(sframe,c,'SHARES',tpric,datetim)
					if tacco == False:
						rv = False
						errormsg = 'Add transaction failed! Create share failed.'
			else:
				facco = shar
				famou = quan
				fpric = pric
				fcomm = 0.0
				tacco = acco
				tamou = str(float(quan)*float(pric))
				tpric = 1.0
				tcomm = comm
				if facco == '0':
					rv = False
					errormsg = 'Add transaction failed! Can not create share to sell.'
			if rv == True:
				if self.api.addtransaction(datetim,desc,facco,famou,fpric,fcomm,tacco,tamou,tpric,tcomm) == False:
					rv = False
					errormsg = 'Add transaction failed!'
				else:
					self.info('Transacion added to project. Please recalculate to see the change in project.')
			if rv == False:
				self.error(errormsg)
		sframe.Destroy()
		
	def evt_tool_recalculate(self,event):
		if not self.checkisopen() == True:
			return False
		pd = self.progress('Please wait while the project data is calculated...')
		rv = self.api.calculate()
		pd.Update(50)
		self.setup_project()
		pd.Update(90)
		pd.Destroy()
		
	def evt_tool_downloadquotes(self,event):
		if not self.checkisopen() == True:
			return False
		pd = self.progress('Please wait while stock quotes are downloaded...')
		rv = self.api.downloadquotes()
		pd.Update(40)
		rv = self.api.calculate()
		pd.Update(90)
		pd.Destroy()
		self.setup_project()

	def evt_portfolio_activated(self,event):
		if not self.checkisopen() == True:
			return False
		itm = event.m_item
		if self.utils.isint(itm.GetText()) == True:
			self.shareframe.append(wxgui.ShareFrame(None,-1,""))
			sframe = self.shareframe[-1]
			shareid = itm.GetText()
			aquotes = self.api.getassetquotes(shareid)
			atrans = self.api.getassettransactions(shareid)
			aapps = self.api.getassetaverageprice(shareid)
			snam = self.api.getassetname(shareid)
			stic = self.api.getassetname(shareid,ticker=True)
			acur = '-'
			ahold = '-'
			asum = '-'
			if not self.assets == None:
				for a in self.assets:
					if int(a[0]) == int(shareid):
						ahold = a[1]
						apri = a[2]
						acur = a[3]
						asum = a[4]
			sframe.share_sharename.SetLabel(snam+' ('+stic+')')
			sframe.share_shareprice.SetLabel(apri+' '+acur)
			sframe.share_averageprice.SetLabel('Average price per share '+str(round(aapps,2))+' '+acur)
			sframe.share_holdings.SetLabel('Currently holding '+ahold+' shares at value '+asum+' '+self.currency)
			mpi = sframe.share_mixplot1
			spplot = self.api.quotestolist(aquotes)
			atbuy = self.api.transactionstolist(atrans[0])
			atsell = self.api.transactionstolist(atrans[1])
			spdates = []
			spvalues = []
			splines = []
			spmarkers = []
			if len(spplot) > 1:
				spdates.append(spplot[0])
				spvalues.append(spplot[1])
				splines.append('-')
				spmarkers.append('None')
				# average price per share
				spdates.append([spplot[0][0],spplot[0][-1]])
				spvalues.append([aapps,aapps])
				splines.append('-.')
				spmarkers.append('None')
			if len(atsell) > 1:
				spdates.append(atsell[0])
				spvalues.append(atsell[1])
				splines.append('None')
				spmarkers.append('v')
			if len(atbuy) > 1:
				spdates.append(atbuy[0])
				spvalues.append(atbuy[1])
				splines.append('None')
				spmarkers.append('^')
			mpi.plot('Share Price',None,spdates,spvalues,splines,spmarkers,[1,1.2])
			sframe.Show()


# Setup notebooks
	def setup_incomestatement(self):
		hid = self.histid

	## TABLE 1
		lcb = self.frame.listctrl_income1
		lcb.ClearAll()

		rev0 = self.revenuegroups[0]
		rev1 = self.revenuegroups[1]
		exp0 = self.expensegroups[0]
		exp1 = self.expensegroups[1]
		res0 = self.incomehistory[3][hid[0]]
		res1 = self.incomehistory[3][hid[1]]
		inchist = self.incomehistory
		net0 = '0.0'
		net1 = '0.0'
		equhist = self.equityhistory
		if len(equhist[1]) > 1:
			net0 = str(equhist[1][hid[0]] - equhist[1][hid[0]-1])
		if len(equhist[1]) > 2:
			net1 = str(equhist[1][hid[0]-1] - equhist[1][hid[0]-2])
		
		lcb.InsertColumn(0,'')
		lcb.InsertColumn(1,self.column[0],format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(2,self.column[1],format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(3,'')
	
		lcb.InsertStringItem(0,'Net result')
		lcb.SetStringItem(0,1,net0)
		lcb.SetStringItem(0,2,net1)
		lcb.SetStringItem(0,3,self.currency)
	
		lcb.InsertStringItem(1,'Cash-flow')
		lcb.SetStringItem(1,1,str(res0))
		lcb.SetStringItem(1,2,str(res1))
		lcb.SetStringItem(1,3,self.currency)

		lcb.InsertStringItem(2,'')
		lcb.InsertStringItem(3,'Revenues')
		
		i = 4
		for r in range(len(rev0)):
			if float(rev0[r][4]) == 0.0 and float(rev1[r][4]) == 0.0:
				continue
			lcb.InsertStringItem(i,rev0[r][0])
			lcb.SetStringItem(i,1,rev0[r][4])
			lcb.SetStringItem(i,2,rev1[r][4])
			lcb.SetStringItem(i,3,self.currency)
			i = i+1

		lcb.InsertStringItem(i,'')
		i = i + 1
		lcb.InsertStringItem(i,'Expenses')
		i = i + 1
		
		for e in range(len(exp0)):
			if float(exp0[e][4]) == 0.0 and float(exp1[e][4]) == 0.0:
				continue
			lcb.InsertStringItem(i,exp0[e][0])
			lcb.SetStringItem(i,1,exp0[e][4])
			lcb.SetStringItem(i,2,exp1[e][4])
			lcb.SetStringItem(i,3,self.currency)
			i = i+1

		lcb.SetColumnWidth(0,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(1,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(2,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(3,wx.LIST_AUTOSIZE)

	### PLOT 2
		mpi = self.frame.pieplot_income2
		exp1 = self.expensegroups[1]
		data = self.api.assetgroupstolist(exp1)
		mpi.plot('Expenses - '+self.column[1],data[0],data[1],[2,2])
		
	### TABLE 3
		lcb = self.frame.listctrl_income3
		lcb.ClearAll()

		inchist = self.incomehistory
		inclabels = ['Cash-flow','','Revenues','Expenses']
		incvalues = []

		incdates = self.api.ymtodates(inchist[0])
		incvalues.append(inchist[3])
		incvalues.append([''] * len(incdates))
		incvalues.append(inchist[1])
		incvalues.append(inchist[2])

		incdates.reverse()
		for iv in incvalues:
			iv.reverse()

		lcb.InsertColumn(0,'')
		lcb.InsertColumn(1,'')
		numvalues = len(incdates)
		numcolumns = numvalues + 2
		for i,id in enumerate(incdates):
			lcb.InsertColumn(i+2,id,format=wx.LIST_FORMAT_RIGHT)

		for i,iv in enumerate(incvalues):
			lcb.InsertStringItem(i,inclabels[i])
			if not inclabels[i] == '':
				lcb.SetStringItem(i,1,self.currency)
			for j in range(numvalues):
				lcb.SetStringItem(i,j+2,str(iv[j]))

		for iv in incvalues:
			iv.reverse()

		for i in range(numcolumns):
			lcb.SetColumnWidth(i,wx.LIST_AUTOSIZE)
		
	### PLOT 4
		mpi = self.frame.lineplot_income4
		inc = []

		inc.append(inchist[0])
		inc.append(inchist[3])
		if len(inc[0]) > 3:
			avg = [inc[1][0],(inc[1][0]+inc[1][1])/2,(inc[1][0]+inc[1][1]+inc[1][2])/3]
			for i in range(len(inc[0])-3):
				avg.append((inc[1][i+1] + inc[1][i+2] + inc[1][i+3]) / 3)
			inc[1] = avg
			title = 'Cash-flow 3-month average ('+self.currency+')'
		else:
			title = 'Cash-flow ('+self.currency+')'
		mpi.plot(title,None,inc,[2,2],style=mpi.PLOT_YEAR)

		return True

	def setup_balancesheet(self):
		tmo = self.thismo
		hid = self.histid
		
	### TABLE 1
		lcb = self.frame.listctrl_balance1
		lcb.ClearAll()

		al0 = self.assetslist[0]
		asshist = self.assetshistory
		liahist = self.liabilitieshistory
		equhist = self.equityhistory
		cas = []
		nca = []
		cas.append(str(asshist[1][hid[0]]))
		cas.append(str(asshist[1][hid[2]]))
		nca.append(str(asshist[2][hid[0]]))
		nca.append(str(asshist[2][hid[2]]))		
		cli = []
		ncl = []
		cli.append(str(liahist[1][hid[0]]))
		cli.append(str(liahist[1][hid[2]]))
		ncl.append(str(liahist[2][hid[0]]))
		ncl.append(str(liahist[2][hid[2]]))
		equ = []
		equ.append(str(equhist[1][hid[0]]))
		equ.append(str(equhist[1][hid[2]]))

		lcb.InsertColumn(0,'')
		lcb.InsertColumn(1,self.column[0],format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(2,'',format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(3,self.column[2],format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(4,'')

		lcb.InsertStringItem(0,'Assets')
		lcb.InsertStringItem(1,'Current Assets')
		lcb.SetStringItem(1,1,cas[0])
		lcb.SetStringItem(1,2,self.get_percentstr(cas[0],cas[1]))
		lcb.SetStringItem(1,3,cas[1])
		lcb.SetStringItem(1,4,self.currency)
		lcb.InsertStringItem(2,'Non-Current Assets')
		lcb.SetStringItem(2,1,nca[0])
		lcb.SetStringItem(2,2,self.get_percentstr(nca[0],nca[1]))
		lcb.SetStringItem(2,3,nca[1])
		lcb.SetStringItem(2,4,self.currency)

		lcb.InsertStringItem(3,'')
		
		lcb.InsertStringItem(4,'Liabilities')
		lcb.InsertStringItem(5,'Current Liabilities')
		lcb.SetStringItem(5,1,cli[0])
		lcb.SetStringItem(5,2,self.get_percentstr(cli[0],cli[1]))
		lcb.SetStringItem(5,3,cli[1])
		lcb.SetStringItem(5,4,self.currency)
		lcb.InsertStringItem(6,'Non-Current Liabilities')
		lcb.SetStringItem(6,1,ncl[0])
		lcb.SetStringItem(6,2,self.get_percentstr(ncl[0],ncl[1]))
		lcb.SetStringItem(6,3,ncl[1])
		lcb.SetStringItem(6,4,self.currency)

		lcb.InsertStringItem(7,'')
		lcb.InsertStringItem(8,'Your Equity')
		lcb.SetStringItem(8,1,equ[0])
		lcb.SetStringItem(8,2,self.get_percentstr(equ[0],equ[1]))
		lcb.SetStringItem(8,3,equ[1])
		lcb.SetStringItem(8,4,self.currency)

		lcb.SetColumnWidth(0,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(1,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(2,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(3,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(4,wx.LIST_AUTOSIZE)

	### PLOT 2
		mpi = self.frame.pieplot_balance2
		mpi.plot('Assets - '+self.column[0],al0[0],al0[1],[2,2])

	### PLOT 3
		as0 = self.assetssum
		li0 = self.liabilitiessum
		mpi = self.frame.pieplot_balance3
		mpi.plot('Assets vs. Liabilities - '+self.column[0],['Assets','Liabilities'],[as0,li0],[2,2])

	### PLOT 4
		mpi = self.frame.lineplot_balance4
		mpi.plot('Your Equity ('+self.currency+')',None,equhist,[2,2],style=mpi.PLOT_ALL)

		return True
		
	def setup_stockportfolio(self):
	
	### TABLE 1
		lcb = self.frame.listctrl_portfolio1
		lcb.ClearAll()

		lcb.InsertColumn(0,'')
		lcb.InsertColumn(1,'')
		lcb.InsertColumn(2,'Num',format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(3,'Price',format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(4,'')
		lcb.InsertColumn(5,'Sum',format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(6,'')

		lcb.InsertStringItem(0,'Shares')
		lcb.SetStringItem(0,1,'Shares')

		i = 1
		i = self._listctrl_portfolio(lcb,False,i,self.shares)
		i = self._listctrl_portfolio(lcb,'Mutual funds',i,self.mutualfunds)
		i = self._listctrl_portfolio(lcb,'Bonds',i,self.bonds)
		i = self._listctrl_portfolio(lcb,'Derivates',i,self.derivates)
		i = self._listctrl_portfolio(lcb,'Other current assets',i,self.othercurrent)
		i = self._listctrl_portfolio(lcb,'Accounts',i,self.accounts)

		lcb.SetColumnWidth(0,0)
		lcb.SetColumnWidth(1,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(2,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(3,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(4,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(5,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(6,wx.LIST_AUTOSIZE)

	### PLOT 1
		mpi = self.frame.pieplot_portfolio2
		lbls = ['Cash']
		vals = [self.liquidsum]
		alist = self._mergelist(self.shares,self.mutualfunds)
		alist = self._mergelist(alist,self.bonds)
		alist = self._mergelist(alist,self.derivates)
		alist = self._mergelist(alist,self.othercurrent)
		for a in alist:
			if round(float(a[1]),2) == 0.0:
				continue
			vals.append(float(a[4]))
			lbls.append(self.api.getassetname(a[0]))
		mpi.plot('Stock Portfolio - '+self.column[0],lbls,vals,[2,2])

	### PLOT 3
		as0 = self.cassetssum
		li0 = self.cliabilitiessum
		mpi = self.frame.pieplot_portfolio3
		mpi.plot('Current Assets vs. Current Liabilities - '+self.column[0],['Assets','Liabilities'],[as0,li0],[2,2])

	### PLOT 4
		cahist = self.assetshistory[1]
		clhist = self.liabilitieshistory[1]
		alia = []
		for i,a in enumerate(cahist):
			alia.append(float(a)-float(clhist[i]))
		spf = []
		spf.append(self.assetshistory[0])
		spf.append(alia)
		mpi = self.frame.lineplot_portfolio4
		mpi.plot('Net Stock Portfolio ('+self.currency+')',None,spf,[2,2],style=mpi.PLOT_YEAR)

		return True

	def setup_budget(self):

	### TABLE 1
		lcb = self.frame.listctrl_budget1
		lcb.ClearAll()

		rev0 = self.revenuegroups[2]
		exp0 = self.expensegroups[2]
		
		lcb.InsertColumn(0,'')
		lcb.InsertColumn(1,self.column[3],format=wx.LIST_FORMAT_RIGHT)
		lcb.InsertColumn(2,'')
		lcb.InsertColumn(3,'')
		lcb.InsertColumn(4,'')
	
		lcb.InsertStringItem(0,'Savings')
		lcb.SetStringItem(0,0,'Savings')
		
		savingsum = self.revenuesum[0]-self.expensesum[0]
		revenuesum = self.revenuesum[0] 
		budget = self.api.getbudget()

		i = 1
		lcb.InsertStringItem(i,'')
		lcb.SetStringItem(i,1,str(int(savingsum)))
		lcb.SetStringItem(i,2,self.currency)
		if revenuesum > 0:
			val = 100*savingsum/revenuesum
		else:
			val = 0
		res = val-100*budget[1][-1]
		lcb.SetStringItem(i,3,self.utils.rstr(val,1)+' %')
		lcb.SetStringItem(i,4,'('+self.utils.rstr(res,1)+' %)')
		if res > 0:
			pass
			#lcb.SetItemTextColour(i,wx.GREEN)
		else:
			lcb.SetItemTextColour(i,wx.RED)
		i = i+1

		lcb.InsertStringItem(i,'')
		i = i + 1
		lcb.InsertStringItem(i,'Expenses')
		i = i + 1
		
		for e in range(len(exp0)):
			if float(exp0[e][4]) == 0.0:
				continue
			lcb.InsertStringItem(i,exp0[e][0])
			lcb.SetStringItem(i,1,exp0[e][4])
			lcb.SetStringItem(i,2,self.currency)
			if revenuesum == 0.0:
				val = 0.0
			else:
				val = 100*float(exp0[e][4])/revenuesum
			lcb.SetStringItem(i,3,self.utils.rstr(val,1)+' %')
			val0 = 0.0
			for j,b in enumerate(budget[0]):
				if b == exp0[e][0]:
					val0 = float(budget[1][j])
					break
			lcb.SetStringItem(i,4,'('+self.utils.rstr(val-100*val0,1)+' %)')
			i = i+1

		lcb.SetColumnWidth(0,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(1,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(2,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(3,wx.LIST_AUTOSIZE)
		lcb.SetColumnWidth(4,wx.LIST_AUTOSIZE)

	### PLOT 2
		mpi = self.frame.pieplot_budget2
		exp1 = self.expensegroups[2]
		data = self.api.assetgroupstolist(exp1)
		data[0].append('Savings')
		data[1].append(self.revenuesum[0]-self.expensesum[0])
		mpi.plot('Expenses - '+self.column[3],data[0],data[1],[2,2])

	### PLOT 4
		mpi = self.frame.pieplot_budget4
		data = self.api.getbudget()
		mpi.plot('Ideal Budget',data[0],data[1],[2,2],palette='gray')

		return True

## internal functions

	def _listnewasset(self,alist,text):
		a0 = []
		a0.append(alist[0][:])
		a0.append(alist[1][:])
		a0.append(alist[2][:])
		a0[0].append(text)
		a0[1].append(0)
		a0[2].append('0')
		return a0

	def _listnewaccount(self,accounts):
		return self._listnewasset(accounts,'[Create new account]')

	def _listnewshare(self,shares):
		return self._listnewasset(shares,'[Create new share]')

	def _mergelist(self,l1,l2):
		list = []
		for l in l1:
			list.append(l)
		for l in l2:
			list.append(l)
		return list

	def _listctrl_portfolio(self,lcb,title,count,list):
		i = count
		if list == []:
			return i
		if not title == False:
			lcb.InsertStringItem(i,'')
			i = i + 1
			lcb.InsertStringItem(i,title)
			lcb.SetStringItem(i,1,title)
			i = i + 1
		for a in list:
			if round(float(a[1]),2) == 0.0:
				continue
			lcb.InsertStringItem(i,a[0])
			lcb.SetStringItem(i,1,self.api.getassetname(a[0]))
			lcb.SetStringItem(i,2,a[1])
			lcb.SetStringItem(i,3,a[2])
			lcb.SetStringItem(i,4,a[3])
			lcb.SetStringItem(i,5,a[4])
			lcb.SetStringItem(i,6,self.currency)
			i = i + 1
		return i

def main():
	app = frugal(0)
	app.MainLoop()

if __name__ == '__main__':
	main()
