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
import matplotlib
import utils
import datetime

matplotlib.use('WXAgg')

import matplotlib.dates as mdates

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class pieplot(wx.Panel):

	PALETTE1 = ['#ef2929','#ad7fa8','#729fcf','#8ae234','#e9b96e','#fcaf3e','#fce94f','#cc0000','#75507b','#3465a4','#73d216','#c17d11','#f57900','#edd400','#a40000','#5c3566','#204a87','#4e9a06','#8f5902','#ce5c00','#c4a000']
	PALETTE2 = ['#aaaaaa','#eeeeee','#555555','#cccccc','#777777','#444444','#dddddd','#888888']

	def __init__(self,parent,id):
		wx.Panel.__init__(self,parent,id)
		self.parent = parent


	def plot(self,title,labels,values,scale=[1,1],palette='color'):
	# len(labels) == len(values), labels = str, values = float
		if not len(labels) == len(values):
			return
	
		figure = Figure((4,4),dpi=50,facecolor='w')
		canvas = FigureCanvas(self,-1,figure)
		sp1 = figure.add_subplot(111,title=title)

		pal = pieplot.PALETTE1
		if palette == 'gray':
			pal = pieplot.PALETTE2

		sp1.pie(values,labels=labels,autopct='%.0f%%',colors=pal)

		psize = self.parent.GetClientSize()
		psize = psize[0]/scale[0],psize[1]/scale[1]
		siz = tuple(psize)
		canvas.SetSize(siz)
		#figure.set_size_inches(float(siz[0])/figure.get_dpi()/2,float(siz[1])/figure.get_dpi()/2)

class lineplot(wx.Panel):

	PALETTE1 = ['#ef2929','#ad7fa8','#729fcf','#8ae234','#e9b96e','#fcaf3e','#fce94f','#cc0000','#75507b','#3465a4','#73d216','#c17d11','#f57900','#edd400','#a40000','#5c3566','#204a87','#4e9a06','#8f5902','#ce5c00','#c4a000']

	PLOT_ALL = 0
	PLOT_YEAR = 1

	def __init__(self,parent,id):
		wx.Panel.__init__(self,parent,id)
		self.parent = parent

	def plot(self,title,labels,values,scale=[1,1],style=False):
	# len(labels) = len(values)-1, labels = str, values = [[date1,date2,...],[float1,float2,...],[float1,float2,...]]
		util = utils.utils()
		tmp1 = []

		if not labels == None and not (len(labels) == len(values) - 1):
			return

		figure = Figure((4,4),dpi=50,facecolor='w')
		canvas = FigureCanvas(self,-1,figure)
		sp1 = figure.add_subplot(111,title=title)

		for i in range(len(values[0])):
			tmp1.append(0.0)
		dates = util.ymtodatetime(values[0])
		sp1.plot_date(dates,tmp1,visible=False)
		for i,v in enumerate(values[1:]):
			tmp0 = []
			for k,j in enumerate(v):
				tmp0.append(float(j))
				tmp1[k] = tmp1[k] + float(j)
			if not labels == None:
				sp1.plot_date(dates,tmp0,label=labels[i],color=lineplot.PALETTE1[i%len(lineplot.PALETTE1)],marker='None',lw=2.0,linestyle='-')
			else:
				sp1.plot_date(dates,tmp0,color=lineplot.PALETTE1[i%len(lineplot.PALETTE1)],marker='None',lw=2.0,linestyle='-')
		sp1.grid()
		if style == lineplot.PLOT_YEAR:
			sp1.xaxis.set_major_locator(mdates.MonthLocator())
			sp1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
			miny = int(values[0][-1][0:4])-1
			minm = int(values[0][-1][4:6])
			maxy = int(values[0][-1][0:4])
			maxm = int(values[0][-1][4:6])+1
		else:
			sp1.xaxis.set_major_locator(mdates.YearLocator())
			sp1.xaxis.set_minor_locator(mdates.MonthLocator())
			sp1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
			miny = int(values[0][0][0:4])
			minm = int(values[0][0][4:6])
			maxy = int(values[0][-1][0:4])
			maxm = int(values[0][-1][4:6])+1
		if maxm > 12:
			maxm = maxm - 12
			maxy = maxy + 1
		datemin = datetime.date(miny,minm,1)
		datemax = datetime.date(maxy,maxm,1)
		sp1.set_xlim(datemin, datemax)
		figure.autofmt_xdate()
		if not labels == None:
			sp1.legend(loc='upper left')

		psize = self.parent.GetClientSize()
		psize = psize[0]/scale[0],psize[1]/scale[1]
		siz = tuple(psize)
		canvas.SetSize(siz)
		#figure.set_size_inches(float(siz[0])/figure.get_dpi()/2,float(siz[1])/figure.get_dpi()/2)

class mixplot(wx.Panel):

	PALETTE1 = ['#ef2929','#ad7fa8','#729fcf','#8ae234','#e9b96e','#fcaf3e','#fce94f','#cc0000','#75507b','#3465a4','#73d216','#c17d11','#f57900','#edd400','#a40000','#5c3566','#204a87','#4e9a06','#8f5902','#ce5c00','#c4a000']

	def __init__(self,parent,id):
		wx.Panel.__init__(self,parent,id)
		self.parent = parent

	def plot(self,title,labels,dates,values,linestyles,markers,scale=[1,1]):
	# len(labels) = len(values)-1, 
	# labels = [str,str,..] 
	# dates = [[date1,date2,...],[date1,date2,...],..]
	# values = [[float1,float2,...],[float1,float2,...],..],
	# linestyles = ['-','None',...]
	# markers = ['None','+',]
	
		util = utils.utils()
		tmp1 = []

		if not labels == None and not len(labels) == len(values):
			return

		if not len(values) == len(linestyles) or not len(linestyles) == len(markers):
			return

		figure = Figure((4,4),dpi=50,facecolor='w')
		canvas = FigureCanvas(self,-1,figure)
		sp1 = figure.add_subplot(111,title=title)

		dattime = []
		tmp1 = []
		for d0 in dates:
			dattime.append(util.ymtodatetime(d0))
		for i in range(len(dates[0])):
			tmp1.append(0.0)
		sp1.plot_date(dattime[0],tmp1,visible=False)
		for i,valuesi in enumerate(values):
			if not labels == None:
				sp1.plot_date(dattime[i],valuesi,label=labels[i],color=mixplot.PALETTE1[i%len(mixplot.PALETTE1)],marker=markers[i],ms=10.0,lw=2.0,linestyle=linestyles[i])
			else:
				sp1.plot_date(dattime[i],valuesi,color=mixplot.PALETTE1[i%len(mixplot.PALETTE1)],marker=markers[i],ms=10.0,lw=2.0,linestyle=linestyles[i])
		sp1.grid()
		sp1.xaxis.set_major_locator(mdates.YearLocator())
		sp1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
		sp1.xaxis.set_minor_locator(mdates.MonthLocator())
		miny = int(dates[0][0][0:4])
		minm = int(dates[0][0][4:6])
		maxy = int(dates[0][-1][0:4])
		maxm = int(dates[0][-1][4:6])+2
		if maxm > 12:
			maxm = maxm - 12
			maxy = maxy + 1
		datemin = datetime.date(miny,minm,1)
		datemax = datetime.date(maxy,maxm,1)
		sp1.set_xlim(datemin, datemax)
		figure.autofmt_xdate()
		if not labels == None:
			sp1.legend(loc='upper left')

		psize = self.parent.GetClientSize()
		psize = psize[0]/scale[0],psize[1]/scale[1]
		siz = tuple(psize)
		canvas.SetSize(siz)
