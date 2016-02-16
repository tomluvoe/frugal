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
from plugin_c import plugin_c

class praw_c(plugin_c):
	NAME = 'Raw Data'
	FUNCTIONS = ['Transactions','Accounts','Quotes','Currencies']

	def createpanel(self,func='',attr=[]):
		# OVERRIDE LOCALLY
		# INITIALIZES THE PANEL
		#
		# CODE EXAMPLE TO FIND WHICH SUBFUNC TO EXECUTE
		# IF NO MATCH CALL EMPTYPANEL
		# for i,f in enumerate(plugin_c.FUNCTIONS):
		#	if f == func:
		#		break
		#
		# createlistctrl(..)
		# createplot(..)
		#
		# HELP FUNCTIONS FOR LABELS AND TEXT
		# self.textctrl()
		# self.statictext(text)
		self.func = func

		if func == praw_c.FUNCTIONS[0]:
			self.createrawlist(func)
		elif func == praw_c.FUNCTIONS[1]:
			self.createrawlist(func)
		elif func == praw_c.FUNCTIONS[2]:
			self.createrawlist(func)
		elif func == praw_c.FUNCTIONS[3]:
			self.createrawlist(func)
		else:
			self.emptypanel()
			return

	def createrawlist(self,func):
		values = []
		if func == praw_c.FUNCTIONS[0]:
			dict = self.dc.tdict.dictionary
			columns = self.dc.tattr
		elif func == praw_c.FUNCTIONS[1]:
			dict = self.dc.adict.dictionary
			columns = self.dc.aattr
		elif func == praw_c.FUNCTIONS[2]:
			dict = self.dc.qdict.dictionary
			columns = self.dc.qattr
		elif func == praw_c.FUNCTIONS[3]:
			dict = self.dc.cdict.dictionary
			columns = self.dc.cattr
		for r in dict:
			row = []
			for c in columns:
				row.append(r[c])
			values.append(row)
		self.createlistctrl(values,columns,edit=1)

	def handlelistctrledit(self,event):
		idx = event.m_itemIndex
		col = event.m_col
		itm = event.m_item
		if self.func == praw_c.FUNCTIONS[0]:
			dict = self.dc.tdict
		elif self.func == praw_c.FUNCTIONS[1]:
			dict = self.dc.adict
		elif self.func == praw_c.FUNCTIONS[2]:
			dict = self.dc.qdict
		elif self.func == praw_c.FUNCTIONS[3]:
			dict = self.dc.cdict
		else:
			return
		dict.updatedict(idx,col,itm.GetText())

