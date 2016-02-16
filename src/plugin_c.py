"""
Frugal - Copyright 2006-2010 Thomas Larsson

This file is part of Frugal.

Frugal is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Frugal.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import datetime

import wx
import wx.lib.mixins.listctrl as lcmix

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Figurecanvas

from datautils_c import datautils_c

# datacoll_c can be accessed as self.dc from any plugin

class plugin_c(wx.Panel):
	# OVERRIDER NAME AND FUNCTIONS VARIABLES LOCALLY
	NAME = 'Generic'
	FUNCTIONS = ['Generic','Generic']

	PIEPLOT = 0
	BARPLOT = 1
	LINEPLOT = 2
	# Tango icon theme colors
	PALETTE1 = ['#ef2929','#ad7fa8','#729fcf','#8ae234','#e9b96e','#fcaf3e','#fce94f','#cc0000','#75507b','#3465a4','#73d216','#c17d11','#f57900','#edd400','#a40000','#5c3566','#204a87','#4e9a06','#8f5902','#ce5c00','#c4a000']

	def __init__(self,parent,splitter,name='',func='',attr=[]):
		wx.Panel.__init__(self,splitter,name=name)

		self.parent = parent
		self.dc = self.parent.datacoll

		self.dat = None

		self.outersizer = wx.StaticBox(self)
		self.middlesizer = wx.StaticBoxSizer(self.outersizer,wx.VERTICAL)
		self.innersizer = wx.GridBagSizer(5,5)

		self.createpanel(func,attr)

		if self.dat == None:
			self.middlesizer.Add(self.innersizer,0,wx.TOP|wx.LEFT,15)
			self.SetSizerAndFit(self.middlesizer)
		else:
			self.SetSizerAndFit(self.dat)

	def createpanel(self,func='',attr=[]):
		# OVERRIDE LOCALLY
		# INITIALIZES THE PANEL
		#
		# CODE EXAMPLE TO FIND WHICH SUBFUNC TO EXECUTE
		# IF NO MATCH CALL EMPTYPANEL
		# self.func = func
		# if(self.func == plugin_c.FUNCTIONS[0]):
		#	...
		# elif(...):
		#	...
		# else:
		#	... # TREAT AS func == plugin_c.NAME
		#
		# createlistctrl(..)
		# createplot(..)
		#
		# HELP FUNCTIONS FOR LABELS AND TEXT
		# self.textctrl()
		# self.statictext(text)
		# self.datepicker()
		# self.datepicker_getdate(datepicker)
		#
		# MESSAGE DIALOG
		# self.msgdlg(text,title[,style])
		# self.errdlg(text,title[,style])
		pass

	def handlelistctrledit(self,event):
		# OVERRIDE LOCALLY
		# ONLY USED FOR LISTCTRL
		idx = event.m_itemIndex
		col = event.m_col
		itm = event.m_item

	def handlelistctrlselect(self,event):
		# OVERRIDE LOCALLY
		# ONLY USED FOR LISTCTRL
		idx = event.m_itemIndex
		col = event.m_col
		itm = event.m_item

	def emptypanel(self):
		txt = self.statictext('[This page intentionally left blank]')
		self.innersizer.Add(txt,(0,0))

	def createlistctrl(self,rows,columns,highlight=-1,edit=0,select=0,zerowidth=-1):
		if edit == 1:
			lc = listctrledit_c(self,style=wx.LC_REPORT)
		else:
			lc = wx.ListCtrl(self,style=wx.LC_REPORT)
		if edit == 1:
			self.Bind(wx.EVT_LIST_END_LABEL_EDIT,self.handlelistctrledit,lc)
		if select == 1:
			self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.handlelistctrlselect,lc)
		for i,c in enumerate(columns):
			if i > 0:
				lc.InsertColumn(i,c,format=wx.LIST_FORMAT_RIGHT)
			else:
				lc.InsertColumn(i,c)
		for i,r in enumerate(rows):
			idx = lc.InsertStringItem(sys.maxint,r[0])
			for j,vv in enumerate(r):
				lc.SetStringItem(idx,j,vv)
		for i,c in enumerate(columns):
			lc.SetColumnWidth(i,wx.LIST_AUTOSIZE)
		if not zerowidth == -1:
			lc.SetColumnWidth(zerowidth,0)
		if not highlight == -1:
			itm = lc.GetItem(highlight-1)
			itm.SetBackgroundColour("light blue")
			lc.SetItem(itm)
		box = wx.BoxSizer()
		box.Add(lc,1,wx.EXPAND|wx.ALL)
		self.lc = lc
		self.dat = box

	def createplot(self,plottype,values,labels,title='',yearly=0):
		du = datautils_c()
		win = wx.Window(self)
		win.SetBackgroundColour("white")
		fig = Figure([8,8],facecolor='w')
		sp1 = fig.add_subplot(111,title=title)
		if plottype == self.PIEPLOT:
			sp1.pie(values,labels=labels,autopct='%.1f%%',colors=self.PALETTE1)
		elif plottype == self.LINEPLOT:
			tmp1 = []
			for i in range(len(values[0])):
				tmp1.append(0.0)
			dates = du.ymtodatetime(values[0])
			sp1.plot_date(dates,tmp1,visible=False)
			for i,v in enumerate(values[1:]):
				tmp0 = []
				for k,j in enumerate(v):
					tmp0.append(float(j))
					tmp1[k] = tmp1[k] + float(j)
				sp1.plot_date(dates,tmp0,label=labels[i+1],color=self.PALETTE1[i%len(self.PALETTE1)],marker='None',lw=2.0,linestyle='-')
			if i > 1:
				sp1.plot_date(dates,tmp1,label='Total',color=self.PALETTE1[(i+1)%len(self.PALETTE1)],marker='None',lw=2.0,linestyle='-')
			sp1.grid()
			sp1.xaxis.set_major_locator(mdates.YearLocator())
			sp1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
			sp1.xaxis.set_minor_locator(mdates.MonthLocator())
			miny = int(values[0][0][0:4])
			minm = int(values[0][0][4:6])
			maxy = int(values[0][-1][0:4])
			maxm = int(values[0][-1][4:6])+2
			if maxm > 12:
				maxm = maxm - 12
				maxy = maxy + 1
			if not yearly == 0:
				maxy = maxy + 1
				maxm = 2
				#minm = 6
				#miny = miny - 1
				pass
			datemin = datetime.date(miny,minm,1)
			datemax = datetime.date(maxy,maxm,1)
			sp1.set_xlim(datemin, datemax)
			fig.autofmt_xdate()
			sp1.legend(loc='upper left')
		elif plottype == self.BARPLOT:
			yoff = []
			for i in range(len(values[0])):
				yoff.append(1.0)
			if yearly == 0:
				dates = du.ymtodatetime(values[0],fixdate=1)
				barw = 31.0
			else:
				dates = du.ymtoyear(values[0],fixdate=1)
				barw = 124.0
			for i,vv in enumerate(values[1:]):
				tmpv = []
				for v in vv:
					tmpv.append(float(v))
				values[i+1] = tmpv
			for i,v in enumerate(values[1:]):
				tmps = list(set(v))
				sp1.bar(0,0,bottom=yoff[0],width=barw,color=self.PALETTE1[i%len(self.PALETTE1)],label=labels[i+1])
				if not (len(tmps) == 1 and float(tmps[0]) == 0.0):
					sp1.bar(dates,v,bottom=yoff,width=barw,color=self.PALETTE1[i%len(self.PALETTE1)],edgecolor=self.PALETTE1[i%len(self.PALETTE1)])
				for j,y in enumerate(yoff):
					yoff[j] = yoff[j] + v[j]
			sp1.grid()
			sp1.xaxis.set_major_locator(mdates.YearLocator())
			sp1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
			sp1.xaxis.set_minor_locator(mdates.MonthLocator())
			miny = int(values[0][0][0:4])
			minm = int(values[0][0][4:6])
			maxy = int(values[0][-1][0:4])
			maxm = int(values[0][-1][4:6])+2
			if maxm > 12:
				maxm = maxm - 12
				maxy = maxy + 1
			if not yearly == 0:
				maxm = 7
				minm = 6
				miny = miny - 1
			datemin = datetime.date(miny,minm,1)
			datemax = datetime.date(maxy,maxm,1)
			sp1.set_xlim(datemin, datemax)			
			fig.autofmt_xdate()
			sp1.legend(loc='upper left')
		else:
			return
		canvas = Figurecanvas(win,-1,fig)
		box = wx.BoxSizer()
		box.Add(canvas,1,wx.EXPAND|wx.ALL)
		win.SetSizer(box)
		outerbox = wx.BoxSizer()
		outerbox.Add(win,1,wx.EXPAND|wx.ALL)
		self.dat = outerbox

	def createsizercols(self,cols):
		for i,c1 in enumerate(cols):
			for j,c2 in enumerate(c1):
				self.innersizer.Add(c2,(j,i))

	def yesnotdlg(self,text='',title='Question?',style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION):
		msg = wx.MessageDialog(self,text,title,style)
		rv = msg.ShowModal()
		msg.Destroy()
		return rv

	def msgdlg(self,text='',title='Information',style=wx.OK|wx.ICON_INFORMATION):
		msg = wx.MessageDialog(self,text,title,style)
		rv = msg.ShowModal()
		msg.Destroy()
		return rv

	def errdlg(self,text='',title='Error',style=wx.OK|wx.ICON_ERROR):
		return self.msgdlg(text,title,style)

	# GUI HELP FUNCTION
	def statictext(self,text=''):
		return wx.StaticText(self,-1,text)

	# GUI HELP FUNCTION
	def textctrl(self,text='',wide=False):
		if wide == True:
			return wx.TextCtrl(self,-1,text,size=(250,-1))
		return wx.TextCtrl(self,-1,text,size=(75,-1))

	# GUI HELP FUNCTION
	def datepicker(self):
		return wx.DatePickerCtrl(self, -1,style=wx.DP_DROPDOWN)
	
	def datepicker_getdate(self,datepicker):
		date = datepicker.GetValue()
		datestr = date.FormatISODate()
		datetim = datetime.datetime.strptime(datestr,'%Y-%m-%d')
		d = datetim.strftime("%Y%m%d")
		return d

	# GUI HELP FUNCTION
	def choicelist(self,choices=[]):
		return wx.Choice(self,-1,choices=choices)

	# GET ARRAY COLUMN AS LIST
	def getarraycolumn(self,array,column):
		result = []
		for a in array:
			result.append(a[column])
		return result

	#TODO NEXT TWO CREATE - IN PLUGIN OR DATACOLL?
	def createaccountlist(self,group=False):
		dict = self.dc.adict
		de = []
		num = []
		for a in dict.dictionary:
			if group == False:
				de.append(a['de']+' ('+self.dc.accgroup(a['num'])+')')
				num.append(a['num'])
			elif self.dc.accisgroup(a['num'],group) == True:
				de.append(a['de'])
				num.append(a['num'])
		accounts = []
		accounts.append(num)
		accounts.append(de)
		return accounts

	def createaccountlist2(self,groups=[]):
		dict = self.dc.adict
		de = []
		num = []
		for a in dict.dictionary:
			for g in groups:
				if self.dc.accisgroup(a['num'],g) == True:
					de.append(a['de'])
					num.append(a['num'])
		accounts = []
		accounts.append(num)
		accounts.append(de)
		return accounts

	# REMOVE, IS IN DATACOLL
	def createcurrencylist(self):
		return self.dc.getcurrencies()

	# MOVE TO DATACOLL
	def creategrouplist(self,pre=0):
		de = []
		gr = []
		groups = []
		if pre == 0:
			for og in self.dc.GROUPS:
				for ig in og[3]:
					de.append(str(ig[0])+' ('+og[0]+')')
					gr.append(ig[0])
		else:
			securities = [self.dc.GROUPS[2][3][1][0],self.dc.GROUPS[2][3][2][0],self.dc.GROUPS[2][3][3][0],self.dc.GROUPS[2][3][4][0],self.dc.GROUPS[2][3][5][0]]
			accounts = [self.dc.GROUPS[2][3][0][0]]
			cassets = [self.dc.GROUPS[2][3][0][0],self.dc.GROUPS[2][3][1][0],self.dc.GROUPS[2][3][2][0],self.dc.GROUPS[2][3][3][0],self.dc.GROUPS[2][3][4][0],self.dc.GROUPS[2][3][5][0]]
			ncassets = [self.dc.GROUPS[3][3][0][0],self.dc.GROUPS[3][3][1][0],self.dc.GROUPS[3][3][2][0]]
			cliabilities = [self.dc.GROUPS[4][3][0][0],self.dc.GROUPS[4][3][1][0]]
			ncliabilities = [self.dc.GROUPS[5][3][0][0],self.dc.GROUPS[5][3][1][0]]
			index = [self.dc.GROUPS[6][3][0][0]]
			if pre == 'ASSETSNOACCOUNT':
				grps = [securities]
			elif pre == 'ACCOUNT':
				grps = [accounts]
			elif pre == 'ASSETSLIABILITIES':
				grps = [cassets,ncassets,cliabilities,ncliabilities,index]
			elif pre == 'ASSETSNOACCOUNTLIABILITIES':
				grps = [securities,ncassets,cliabilities,ncliabilities,index]
			elif pre == 'ACCOUNTLIABILITIES':
				grps = [accounts,cliabilities,ncliabilities]
			else:
				grps = []
			for g in grps:
				for g2 in g:
					de.append(g2)
					gr.append(g2)
		groups.append(de)
		groups.append(gr)
		return groups

class listctrledit_c(wx.ListCtrl,lcmix.TextEditMixin):
	def __init__(self,parent,style):
		wx.ListCtrl.__init__(self,parent,style=style)
		lcmix.TextEditMixin.__init__(self)

