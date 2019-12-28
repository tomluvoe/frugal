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
import sys
from datetime import date
import webbrowser

from pbalance_c import pbalance_c as balance_c
from pincome_c import pincome_c as income_c
from pportfolio_c import pportfolio_c as portfolio_c
from padddata_c import padddata_c as adddata_c
from praw_c import praw_c as raw_c
from puseradd_c import puseradd_c as useradd_c
from plugin_c import plugin_c

from datautils_c import datautils_c
from datacoll_c import datacoll_c

class gui_c(wx.Frame):
	def __init__(self,parent,program,version,about,owner):
		wx.Frame.__init__(self,parent,-1,program+' '+version,size=(900,650))
		self.CreateStatusBar()
		self.SetMinSize((640,480))
		self.pinfo = program
		self.vinfo = version
		self.ainfo = about
		self.owner = owner
		self.projectopen = False
		self.frametitle = program+' '+version
		# CALLBACK
		owner.registerupdcallback(self.updatecallback)
		# PLUGINS
		#self.plugins = [balance_c,income_c,useradd_c,addquotes_c,raw_c,adddata_c]
		self.plugins = [balance_c,income_c,portfolio_c,useradd_c,adddata_c,raw_c]
		self.datacoll = self.owner.datacoll
		# COLOURS
		#self.palette = DEF_COLORS
		#self.palette1 = DEF_COLORS_PROFIT
		# MENU BAR
		self.menubar = wx.MenuBar()
		# FILE
		self.menufile = wx.Menu()
		item = self.menufile.Append(gui_c.ID_NEWPROJ,'New project...','Create a new project')
		item = self.menufile.Append(gui_c.ID_OPEPROJ,'Open project...','Open an existing project')
		item = self.menufile.Append(gui_c.ID_SAVPROJ,'Save project','Save current project')
		self.menufile.AppendSeparator()
		item = self.menufile.Append(gui_c.ID_EXIT,'Exit','Exit program')
		#self.menufile.Enable(gui_c.ID_SAVPROJ,False)
		self.menubar.Append(self.menufile,'File')
		# VIEW
		self.menuview = wx.Menu()
		item = self.menuview.Append(gui_c.ID_DETAILS,'Details','Show a detailed textual view',kind=wx.ITEM_RADIO)
		item = self.menuview.Append(gui_c.ID_HISTORY,'Monthly history','Show a monthly historical textual view',kind=wx.ITEM_RADIO)
		item = self.menuview.Append(gui_c.ID_HISTORYY,'Yearly history','Show a yearly historical textual view',kind=wx.ITEM_RADIO)
		item = self.menuview.Append(gui_c.ID_GDETAILS,'Detailed plot','Show a detailed graphical view',kind=wx.ITEM_RADIO)
		item = self.menuview.Append(gui_c.ID_GHISTORY,'Monthly graph','Show a monthly historical graphical view',kind=wx.ITEM_RADIO)
		item = self.menuview.Append(gui_c.ID_GHISTORYY,'Yearly graph','Show a yearly historical graphical view',kind=wx.ITEM_RADIO)
		self.menubar.Append(self.menuview,'View')
		# PROJECT
		self.menuproj = wx.Menu()
		item = self.menuproj.Append(gui_c.ID_UPDPROJ,'Download online quotes','Update stock quotes and currency rates online')
		item = self.menuproj.Append(gui_c.ID_CALPROJ,'Re-calculate result','Re-calculate all matrices and data')
		#self.menuproj.Enable(gui_c.ID_UPDPROJ,False)
		#self.menuproj.Enable(gui_c.ID_CALPROJ,False)
		self.menubar.Append(self.menuproj,'Project')
		# HELP
		self.menuabout = wx.Menu()
		item = self.menuabout.Append(gui_c.ID_UPDATE,'Search for updates...','Online update search')
		item = self.menuabout.Append(gui_c.ID_USERGU,'User\'s Guide... (web)','Frugal\'s User\'s Guide')
		item = self.menuabout.Append(gui_c.ID_ABOUT,'About','About %s'%(self.pinfo))
		self.menubar.Append(self.menuabout,'About')
		# UPDATE
		#self.menuupdate = wx.Menu()
		#item = self.menuupdate.Append(gui_c.ID_UPDATE,'Show available update','Show available updates')
		#self.menubar.Append(self.menuupdate,'Update')
		# ADD MENU AND EVENTS
		self.SetMenuBar(self.menubar)
		#self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
		#wx.EVT_MENU(self,gui_c.ID_NEWPROJ,self.new)
		self.Bind(wx.EVT_MENU, self.new, id=gui_c.ID_NEWPROJ)
		#wx.EVT_MENU(self,gui_c.ID_OPEPROJ,self.open)
		self.Bind(wx.EVT_MENU, self.open, id=gui_c.ID_OPEPROJ)
		#wx.EVT_MENU(self,gui_c.ID_SAVPROJ,self.save)
		self.Bind(wx.EVT_MENU, self.save, id=gui_c.ID_SAVPROJ)
		#wx.EVT_MENU(self,gui_c.ID_EXIT,self.quit)
		self.Bind(wx.EVT_MENU, self.quit, id=gui_c.ID_EXIT)
		#wx.EVT_MENU(self,gui_c.ID_UPDPROJ,self.updateproject)
		self.Bind(wx.EVT_MENU, self.updateproject, id=gui_c.ID_UPDPROJ)
		#wx.EVT_MENU(self,gui_c.ID_CALPROJ,self.calc)
		self.Bind(wx.EVT_MENU, self.calc, id=gui_c.ID_CALPROJ)
		#wx.EVT_MENU(self,gui_c.ID_USERGU,self.usersguide)
		self.Bind(wx.EVT_MENU, self.usersguide, id=gui_c.ID_USERGU)
		#wx.EVT_MENU(self,gui_c.ID_ABOUT,self.about)
		self.Bind(wx.EVT_MENU, self.about, id=gui_c.ID_ABOUT)
		#wx.EVT_MENU(self,gui_c.ID_UPDATE,self.showupdate)
		self.Bind(wx.EVT_MENU, self.showupdate, id=gui_c.ID_UPDATE)
		self.Bind(wx.EVT_CLOSE,self.closeprogram)
		# SPLITTER
		self.splitv = wx.SplitterWindow(self)
		# TREE
		self.tree = wx.TreeCtrl(self.splitv,-1)
		self.troot = self.tree.AddRoot('Frugal')
		self.tree.Expand(self.troot)
		self.tree.SelectItem(self.troot)
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED,self.treeevent)
		# PANEL
		lc = wx.ListCtrl(self.splitv,style=wx.LC_REPORT)
		# CONF SPLITTERS
		self.splitv.SplitVertically(self.tree,lc,200)
		self.Centre()
		if len(sys.argv) > 1:
			# assume path to project is first variable
			path = sys.argv[1]
			pd = wx.ProgressDialog('Opening project','Please wait - this might take a while...',100,self)
			pd.Update(10)
			self.openpath(path)
			pd.Destroy()

	def new(self,event):
		if self.projectopen == True:
			#TODO error message
			return
		dialog = wx.DirDialog(self,'Select new project directory','.',wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			dialog.Destroy()
			dialog = wx.SingleChoiceDialog(self,'Choose project currency:','Currency',self.datacoll.ALLOWEDCURRENCIES)
			if dialog.ShowModal() == wx.ID_OK:
				currency = dialog.GetStringSelection()
			else:
				currency = 'EUR'
			dialog.Destroy()
			pd = wx.ProgressDialog('Create new project','Please wait... this might take a while.',100,self)
			if self.owner.new(path,currency) == False:
				pd.Destroy()
				self.errdlg('Error: Failed to create new project!')
				return
		else:
			dialog.Destroy()
			return
		if currency == '':
			currency = 'EUR'
		self.openpath(path,pd)
		pd.Destroy()

	def open(self,event):
		if self.projectopen == True:
			#TODO error message
			return
		dialog = wx.DirDialog(self,'Select project directory','.',wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			pd = wx.ProgressDialog('Opening project','Please wait - this might take a while...',100,self)
			pd.Update(10)
			self.openpath(path,pd)
			pd.Destroy()
		dialog.Destroy()

	def openpath(self,path,pd=False):
		if self.owner.open(path,pd) == True:
			#self.menufile.Enable(gui_c.ID_NEWPROJ,False)
			#self.menufile.Enable(gui_c.ID_OPEPROJ,False)
			#self.menufile.Enable(gui_c.ID_SAVPROJ,True)
			#self.menuproj.Enable(gui_c.ID_UPDPROJ,True)
			#self.menuproj.Enable(gui_c.ID_CALPROJ,True)
			self.createtree()
			self.projectopen = True
		else:
			self.errdlg('Error: Failed to open project!')

	def save(self,event):
		if self.projectopen == False:
			#TODO error message
			return
		pd = wx.ProgressDialog('Saving project','Please wait - this might take a while...',100,self)
		pd.Update(10)
		rv = self.owner.save(pd)
		pd.Destroy()
		if rv == False:
			self.errdlg('Error: Failed to save project!')
			return
		self.unsaved_data = 0

	def closeprogram(self,event):
		if self.datacoll.unsaved == 1:
			msg = wx.MessageDialog(self,'The financial data has been modified.\nDo you want to save your changes before exiting?','Save data',wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
			rv = msg.ShowModal()
			msg.Destroy()
			if rv == wx.ID_YES:
				self.owner.datacoll.savefiles()
			if rv == wx.ID_CANCEL:
				return
		self.Destroy()

	def quit(self,event):
		self.Close()

	def updateproject(self,event):
		if self.projectopen == False:
			#TODO error message
			return
		pd = wx.ProgressDialog('Updating stock quotes and currency rates','Please wait - this might take a while...',100,self)
		pd.Update(10)
		if self.owner.downloadquotes(pd) == True:
			self.tree.SelectItem(self.troot)
		pd.Destroy()
		self.calc(0)

	def calc(self,event):
		if self.projectopen == False:
			#TODO error message
			return
		pd = wx.ProgressDialog('Calculating result','Please wait - this might take a while...',100,self)
		pd.Update(10)
		if self.owner.calc(pd) == True:
			self.tree.SelectItem(self.troot)
		pd.Destroy()

	def showupdate(self,event):
		updateavailable = self.owner.checkforupdate()
		if updateavailable == 1:
			msg = 'A new version of Frugal is available for download!\n\nPlease go to http://www.samoht.se/frugal/ and click Download!'
			self.SetTitle(self.frametitle+' (new version available for download)')
		elif updateavailable == -1:
			msg = 'Failed to read latest version! Please retry.'
		else:
			msg = 'No new version of Frugal available!'
		notice = wx.MessageDialog(self,msg,self.pinfo,wx.OK|wx.ICON_INFORMATION)
		notice.ShowModal()
		notice.Destroy()

	def updatecallback(self):
		# UPDATE
		#self.menuupdate = wx.Menu()
		#item = self.menuupdate.Append(gui_c.ID_UPDATE,'Show available update','Show available updates')
		#self.menubar.Append(self.menuupdate,'Update')
		self.SetTitle(self.frametitle+' (new version available for download)')

	def about(self,event):
		about = wx.MessageDialog(self,self.ainfo,self.pinfo,wx.OK|wx.ICON_INFORMATION)
		about.ShowModal()
		about.Destroy()

	def usersguide(self,event):
		webbrowser.open('http://www.samoht.se/frugal/usersguide.php')

	def createtree(self):
		for p in self.plugins:
			itm = self.tree.AppendItem(self.troot,p.NAME)
			for f in p.FUNCTIONS:
				self.tree.AppendItem(itm,f)
		self.tree.Expand(self.troot)

	def treeevent(self,event):
		itm = event.GetItem()
		text = self.tree.GetItemText(itm)
		selectedplugin = None
		attr = []
		if self.menuview.FindItemById(gui_c.ID_DETAILS).IsChecked():
			attr.append('details')
		elif self.menuview.FindItemById(gui_c.ID_HISTORY).IsChecked():
			attr.append('history')
		elif self.menuview.FindItemById(gui_c.ID_HISTORYY).IsChecked():
			attr.append('historyy')
		elif self.menuview.FindItemById(gui_c.ID_GDETAILS).IsChecked():
			attr.append('gdetails')
		elif self.menuview.FindItemById(gui_c.ID_GHISTORY).IsChecked():
			attr.append('ghistory')
		elif self.menuview.FindItemById(gui_c.ID_GHISTORYY).IsChecked():
			attr.append('ghistoryy')
		for p in self.plugins:
			if p.NAME == text:
				selectedplugin = p(self,self.splitv,func=p.NAME,attr=attr)
			for f in p.FUNCTIONS:
				if f == text:
					selectedplugin = p(self,self.splitv,func=f,attr=attr)
		if not selectedplugin == None:
			self.showpanel(selectedplugin)

	def showpanel(self,panel):
		old = self.splitv.GetWindow2()
		self.splitv.ReplaceWindow(old,panel)
		old.Destroy()

	def errdlg(self,text='',title='Error',style=wx.OK|wx.ICON_ERROR):
		return self.msgdlg(text,title,style)

	def msgdlg(self,text='',title='Information',style=wx.OK|wx.ICON_INFORMATION):
		msg = wx.MessageDialog(self,text,title,style)
		rv = msg.ShowModal()
		msg.Destroy()
		return rv

	ID_NEWPROJ = 1001
	ID_OPEPROJ = 1002
	ID_SAVPROJ = 1003
	ID_EXIT    = 1004
	ID_CALPROJ = 1005
	ID_ABOUT   = 1006
	ID_ADDTRAN = 1007
	ID_DETAILS = 1008
	ID_HISTORY = 1009
	ID_GDETAILS = 1010
	ID_GHISTORY = 1011
	ID_CLOPROJ = 1012
	ID_UPDATE = 1013
	ID_HISTORYY = 1014
	ID_GHISTORYY = 1015
	ID_UPDPROJ = 1016
	ID_USERGU = 1017

class appl_c(wx.App):
	def OnInit(self):
		return True

	def setup(self,program,version,about,owner):
		frame = gui_c(None,program,version,about,owner)
		frame.Show()
