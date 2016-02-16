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

class pincome_c(plugin_c):
	NAME = 'Income Statement'
	FUNCTIONS = ['Revenues','Expenses']

	# ATTR view type - plot, list, history, detailed.. 
	def createpanel(self,func='',attr=[]):
		self.func = func

		if(self.func == pincome_c.FUNCTIONS[0]):
			self.incomepanel(attr)
		elif(self.func == pincome_c.FUNCTIONS[1]):
			self.incomepanel(attr)
		else:
			self.incomestatementpanel(attr)

	def incomestatementpanel(self,attr=[]):
		if attr[0] == 'history':
			self.createhispanel()
		elif attr[0] == 'historyy':
			self.createhispanel(year=1)
		elif attr[0] == 'gdetails':
			self.createispanel()
			#self.createisplot()
		elif attr[0] == 'ghistory':
			self.createhisplot()
		elif attr[0] == 'ghistoryy':
			self.createhisplot(year=1)
		else: # 'details'
			self.createispanel()

	def createhispanel(self,year=0):
		du = datautils_c()
		columns = [self.dc.GROUPS[0][0],self.dc.GROUPS[1][0]]
		data = self.dc.gethassets(columns,diff=1,year=year)
		base = self.dc.getbasecurrency()
		values = []
		if year == 1:
			columns = ['','Profit/Loss','%','Income','Income/mo','%']
		else:
			columns = ['','Profit/Loss','%','Income']
		incmo2 = 0.0
		for d in data:
			inc = float(d[1])
			profit = inc-float(d[2])
			if inc > 0:
				profit2 = profit/inc
			else:
				profit2 = 0
			if year == 1:
				mo = float(d[0][4:6])
				if not mo == 12:
					mo = mo - 1
				if du.isfloat(mo) and mo >= 1:
					incmo = inc/mo
				else:
					incmo = 0.0
				if incmo2 == 0:
					incmo2 = incmo
				incmo2 = (incmo-incmo2)/incmo2
				values.append([d[0],du.rstr(profit,0)+' '+base,du.rstr(100*profit2,1)+' %',du.rstr(inc,0)+' '+base,du.rstr(incmo,0)+' '+base,du.rstr(100*incmo2,1)+' %'])
				incmo2 = incmo
			else:
				values.append([d[0],du.rstr(profit,0)+' '+base,du.rstr(100*profit2,1)+' %',du.rstr(inc,0)+' '+base])
		values.reverse()
		self.createlistctrl(values,columns)

	def createhisplot(self,year=0):
		du = datautils_c()
		columns = [self.dc.GROUPS[0][0],self.dc.GROUPS[1][0]]
		data = self.dc.gethassets(columns,diff=1,year=year)
		values = []
		labels = ['Profit/Loss','Profit/Loss']
		for d in data:
			values.append([d[0],float(d[1])-float(d[2])])
		data = values
		values = []
		values.append(self.getarraycolumn(data,0))
		values.append(self.getarraycolumn(data,1))
		self.createplot(self.BARPLOT,values,labels,'Profit/Loss',yearly=year)

	def incomepanel(self,attr=[]):
		if(self.func == pincome_c.FUNCTIONS[0]):
			group = self.dc.GROUPS[0][0]
		else:
			group = self.dc.GROUPS[1][0]

		if attr[0] == 'history':
			self.createhincexppanel(group)
		elif attr[0] == 'historyy':
			self.createhincexppanel(group,year=1)
		elif attr[0] == 'gdetails':
			self.createincexpplot(group)
		elif attr[0] == 'ghistory':
			self.createhincexpplot(group)
		elif attr[0] == 'ghistoryy':
			self.createhincexpplot(group,year=1)
		else: # 'details'
			self.createincexppanel(group)

	def createincexppanel(self,group):
		year = date.today().year
		#assets = self.dc.getdassets(group,yfrom=year,yto=year+1,diff=1)
		groups = self.dc.getgrouplabels(group)
		assets = []
		for g in groups:
			assets.extend(self.dc.getdassets(g,yfrom=year,yto=year,diff=1,totsum=0))
		columns = []
		columns.append('Description')
		columns.append('Quantity')
		columns.append('Price')
		columns.append('Sum')
		#self.createlistctrl(assets,columns,highlight=len(assets))
		self.createlistctrl(assets,columns)

	def createincexpplot(self,group):
		year = date.today().year
		groups = self.dc.getgrouplabels(group)
		assets = self.dc.getdglvalues(groups,yfrom=year,yto=year,diff=1)
		self.createplot(self.PIEPLOT,assets,groups,group+' ('+str(year)+')')

	def createhincexpplot(self,group,year=0):
		du = datautils_c()
		columns = self.dc.getgrouplabels(group) 
		data = self.dc.gethassets(columns,diff=1,year=year)
		values = []
		for i,c in enumerate(columns):
			values.append(self.getarraycolumn(data,i))
		self.createplot(self.BARPLOT,values,columns,group,yearly=year)

	def createhincexppanel(self,group,year=0):
		du = datautils_c()
		columns = self.dc.getgrouplabels(group) 
		values = self.dc.gethassets(columns,diff=1,year=year)
		values.reverse()
		columns.append('Sum')
		for i in range(len(values)):
			sum = 0
			for j in range(len(values[i])-1):
				sum = sum+float(values[i][j+1])
			values[i].append(du.rstr(sum)) 
		self.createlistctrl(values,columns,highlight=1) 

	def createispanel(self):
		du = datautils_c()
		year = date.today().year
		month = date.today().month
		dc_inc = self.dc.GROUPS[0][0]
		dc_exp = self.dc.GROUPS[1][0]
		base = self.dc.getbasecurrency()
		hl = 0
		values = []
		columns = ['','','']
		grplst = []
		grplst.append(self.dc.GROUPS[0][0])
		grplst.extend(self.dc.getgrouplabels(self.dc.GROUPS[0][0]))
		inclen = len(grplst)
		grplst.append(self.dc.GROUPS[1][0])
		grplst.extend(self.dc.getgrouplabels(self.dc.GROUPS[1][0]))
		data = self.dc.gethassets(grplst,diff=1,year=0)
		if month < 2:
			month0 = 12
			year0 = year - 1
		else:
			month0 = month - 1
			year0 = year
		j = -1
		for i,d in enumerate(data):
			if int(d[0]) == (year*100+month):
				j = i
				d1 = d
				d0 = data[i-1]
				y1 = d[0]
				y0 = data[i-1][0]
				break
		if j == -1:
			y1 = data[-1][0]
			y0 = data[-2][0]
		values.append(['Income Statement'.title(),str(y1),str(y0)])
		values.append(['','',''])
		values.append([dc_inc.upper(),'',''])
		inc1 = float(data[j][1])
		inc0 = float(data[j-1][1])
		exp1 = float(data[j][inclen+1])
		exp0 = float(data[j-1][inclen+1])

		for i,g in enumerate(grplst[2:]):
			if i == inclen-1:
				values.append(['','',''])
				values.append([dc_exp.upper(),'',''])
			else:
				if not (float(data[j][i+2]) == 0 and float(data[j-1][i+2]) == 0):
					hl = hl + 1
					values.append([g,data[j][i+2]+' '+base,data[j-1][i+2]+' '+base])
		values.append(['','',''])
		d1 = '-'
		d0 = '-'
		if inc1 > 0:
			d1 = du.rstr(100*(inc1-exp1)/inc1,1)
		if inc0 > 0:
			d0 = du.rstr(100*(inc0-exp0)/inc0,1)
		values.append(['Cash flow'.upper(),str(inc1-exp1)+' '+base,str(inc0-exp0)+' '+base])
		values.append(['Profit'.title(),d1+'%',d0+'%'])

		self.createlistctrl(values,columns,highlight=hl+7)

