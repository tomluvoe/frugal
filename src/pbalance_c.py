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

class pbalance_c(plugin_c):
	NAME = 'Balance Sheet'
	FUNCTIONS = ['Current Assets','Non-Current Assets','Current Liabilities','Non-Current Liabilities']

	# ATTR view type - plot, list, history, detailed.. 
	def createpanel(self,func='',attr=[]):
		self.func = func

		if(self.func == pbalance_c.FUNCTIONS[0]):
			self.cassetspanel(attr)
		elif(self.func == pbalance_c.FUNCTIONS[1]):
			self.cassetspanel(attr)
		elif(self.func == pbalance_c.FUNCTIONS[2]):
			self.cassetspanel(attr)
		elif(self.func == pbalance_c.FUNCTIONS[3]):
			self.cassetspanel(attr)
		else:
			self.balancepanel(attr)

	def cassetspanel(self,attr=[]):
		if(self.func == pbalance_c.FUNCTIONS[0]):
			group = self.dc.GROUPS[2][0]
		elif(self.func == pbalance_c.FUNCTIONS[1]):
			group = self.dc.GROUPS[3][0]
		elif(self.func == pbalance_c.FUNCTIONS[2]):
			group = self.dc.GROUPS[4][0]
		else:
			group = self.dc.GROUPS[5][0]

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
			self.createassetspanel(group)

	def ncassetspanel(self,attr=[]):
		self.createhassetspanel()

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
	# TODO SHOW ONLY FOR GROUPS
		today = date.today()
		year = date.today().year
		groups = self.dc.getgrouplabels(group)
		assets = self.dc.getdglvalues(groups,yto=year)
		#assets = []
		#groups = []
		#if(self.func == pbalance_c.FUNCTIONS[0]):
		#	cashgrp = self.creategrouplist('ACCOUNT')[0]
		#	cash = self.dc.getdglvalues([cashgrp[0]])
		#	assets.append(cash[0])
		#	groups.append(cashgrp[0])
		#	grouplist = self.creategrouplist('ASSETSNOACCOUNT')[0]
		#else:
		#	grouplist = [group]
		#for g in grouplist:
		#	assetslist = self.dc.getdassets(g,basecurrency=0,totsum=0)
		#	if assetslist == []:
		#		continue
		#	for a in assetslist:
		#		assets.append(a[3])
		#		groups.append(a[0])
		self.createplot(self.PIEPLOT,assets,groups,group+today.strftime(" (%Y-%m-%d)"))

	def createhassetspanel(self,group,year=0):
		du = datautils_c()
		columns = self.dc.getgrouplabels(group) 
		values = self.dc.gethassets(columns,year=year)
		values.reverse()
		columns.append('Sum')
		for i in range(len(values)):
			sum = 0
			for j in range(len(values[i])-1):
				sum = sum+float(values[i][j+1])
			values[i].append(du.rstr(sum)) 
		self.createlistctrl(values,columns,highlight=1) 

	def createhassetsplot(self,group,year=0):
		du = datautils_c()
		columns = self.dc.getgrouplabels(group)
		data = self.dc.gethassets(columns,year=year)
		values = []
		for i,c in enumerate(columns):
			values.append(self.getarraycolumn(data,i))
		self.createplot(self.LINEPLOT,values,columns,group,yearly=year)

	def createhbalancepanel(self,year=0):
		du = datautils_c()
		columns = [self.dc.GROUPS[2][0],self.dc.GROUPS[3][0],self.dc.GROUPS[4][0],self.dc.GROUPS[5][0]]
		values = self.dc.gethassets(columns,year=year)
		base = self.dc.getbasecurrency()
		columns.append('Equity')
		columns.append('%')
		equ2 = 0.0
		for i in range(len(values)):
			equ = float(values[i][1])+float(values[i][2])-float(values[i][3])-float(values[i][4])
			values[i][1] = values[i][1]+' '+base
			values[i][2] = values[i][2]+' '+base
			values[i][3] = values[i][3]+' '+base
			values[i][4] = values[i][4]+' '+base
			values[i].append(du.rstr(equ)+' '+base)
			if not equ2 == 0:
				equ2 = (equ-equ2)/equ2
			values[i].append(du.rstr(equ2*100,1)+' %')
			equ2 = equ
		values.reverse()
		self.createlistctrl(values,columns,highlight=1) 

	def createhbalanceplot(self,year=0):
		du = datautils_c()
		columns = [self.dc.GROUPS[2][0],self.dc.GROUPS[3][0],self.dc.GROUPS[4][0],self.dc.GROUPS[5][0]]
		data = self.dc.gethassets(columns,year=year)
		labels = ['Equity','Equity']
		values = []
		for d in data:
			values.append([d[0],du.rstr(float(d[1])+float(d[2])-float(d[3])-float(d[4]),0)])
		data = values
		values = []
		values.append(self.getarraycolumn(data,0))
		values.append(self.getarraycolumn(data,1))
		self.createplot(self.LINEPLOT,values,labels,'Equity',yearly=year)

	def _plotgrpbalance(self,list,grplst,year,hl):
		du = datautils_c()
		base = self.dc.getbasecurrency()
		for g in grplst:
			gs = self.dc.getgroupsum(g,yto=year)
			gs0 = self.dc.getgroupsum(g,yto=year-1)
			if not gs == 0 or not gs0 == 0:
				list.append([g.title(),du.rstr(gs,0)+' '+base,'',du.rstr(gs0,0)+' '+base])
				hl = hl + 1
		return hl

	def balancepanel(self,attr=[]):
		if attr[0] == 'history':
			self.createhbalancepanel()
			return
		elif attr[0] == 'historyy':
			self.createhbalancepanel(year=1)
			return
		elif attr[0] == 'ghistory':
			self.createhbalanceplot()
			return
		elif attr[0] == 'ghistoryy':
			self.createhbalanceplot(year=1)
			return

		du = datautils_c()
		dc_fia = self.dc.GROUPS[2][0]
		dc_fxa = self.dc.GROUPS[3][0]
		dc_cl = self.dc.GROUPS[4][0]
		dc_ncl = self.dc.GROUPS[5][0]
		values = []
		columns = ['','','','']
		hl = 0
		year = date.today().year
		fia = self.dc.getgroupsum(dc_fia,yto=year)
		fxa = self.dc.getgroupsum(dc_fxa,yto=year)
		lia = self.dc.getgroupsum(dc_cl,yto=year)
		ncl = self.dc.getgroupsum(dc_ncl,yto=year)
		base = self.dc.getbasecurrency()

		fia0 = self.dc.getgroupsum(dc_fia,yto=year-1)
		fxa0 = self.dc.getgroupsum(dc_fxa,yto=year-1)
		lia0 = self.dc.getgroupsum(dc_cl,yto=year-1)
		ncl0 = self.dc.getgroupsum(dc_ncl,yto=year-1)

		values.append(['Balance Sheet'.title(),str(year),'','December '+str(year-1)])
		values.append(['','','',''])
		values.append(['Assets'.upper(),'','',''])

		values.append([dc_fia.title(),'','',''])

		grplst = self.dc.getgrouplabels(dc_fia)
		hl = self._plotgrpbalance(values,grplst,year,hl)
		if not fia0 == 0:
			diff = du.rstr(100*(fia-fia0)/fia0,1)
		else:
			diff = '-'
		values.append(['',du.rstr(fia,0)+' '+base,diff+'%',du.rstr(fia0,0)+' '+base])

		values.append([dc_fxa.title(),'','',''])
		grplst = self.dc.getgrouplabels(dc_fxa)
		hl = self._plotgrpbalance(values,grplst,year,hl)
		if not fxa0 == 0:
			diff = du.rstr(100*(fxa-fxa0)/fxa0,1)
		else:
			diff = '-'
		values.append(['',du.rstr(fxa,0)+' '+base,diff+'%',du.rstr(fxa0,0)+' '+base])

		values.append(['','','',''])
		if not (fxa0+fia0) == 0:
			diff = du.rstr(100*(fia+fxa-fxa0-fia0)/(fia0+fxa0),1)
		else:
			diff = '-'
		values.append(['Total Assets'.upper(),du.rstr(fia+fxa,0)+' '+base,diff+'%',du.rstr(fia0+fxa0,0)+' '+base])

		values.append(['','','',''])
		values.append(['Liabilities and Equity'.upper(),'','',''])

		values.append([dc_cl.title(),'','',''])
		grplst = self.dc.getgrouplabels(dc_cl)
		hl = self._plotgrpbalance(values,grplst,year,hl)
		if not lia0 == 0:
			diff = du.rstr(100*(lia-lia0)/ncl0,1)
		else:
			diff = '-'
		values.append(['',du.rstr(lia,0)+' '+base,diff+'%',du.rstr(lia0,0)+' '+base])

		values.append([dc_ncl.title(),'','',''])
		grplst = self.dc.getgrouplabels(dc_ncl)
		hl = self._plotgrpbalance(values,grplst,year,hl)

		if not ncl0 == 0:
			diff = du.rstr(100*(ncl-ncl0)/ncl0,1)
		else:
			diff = '-'
		values.append(['',du.rstr(ncl,0)+' '+base,diff+'%',du.rstr(ncl0,0)+' '+base])
		values.append(['','','',''])
		
		if not (fia0+fxa0-lia0-ncl0) == 0:
			diff = du.rstr(100*(fia+fxa-lia-ncl-(fia0+fxa0-lia0-ncl0))/(fia0+fxa0-lia0-ncl0),1)
		else:
			diff = '-'
		values.append(['Your Equity'.title(),du.rstr(fia+fxa-lia-ncl,0)+' '+base,diff+'%',du.rstr(fia0+fxa0-lia0-ncl0,0)+' '+base])
		values.append(['','','',''])
		values.append(['Total Liabilities and Equity'.upper(),du.rstr(fia+fxa,0)+' '+base,'',du.rstr(fia0+fxa0,0)+' '+base])
		self.createlistctrl(values,columns,highlight=hl+17)

