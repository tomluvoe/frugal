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

import utils
import re
import datetime
import socket
import urllib2

class quotes():
	def __init__(self):
		self.utils = utils.utils()

	def getquotes(self,shares):
		quotes = []
		yho = []
		mor = []
		mquotes = []
		quotes = []
		for s in shares:
			if self.utils.isisin(s):
				continue
			if self.utils.ismorn(s):
				mor.append(s)
				continue
			if not re.search(' ',s):
				yho.append(s)
				continue
		if not yho == []:
			quotes = self.getyahooquotes(yho)
		if not mor == []:
			mquotes = self.getmorningstarquotes(mor)
		for m in mquotes:
			quotes.append(m)
		return quotes

	def getcurrencyrates(self,base,currencies=[]):
		return self.getecbrates(base,currencies)

	def getyahooquotes(self,shares):
	# get latest share quotes of list shares from yahoo finance
		shareurl = ''
		yhoshares = []
		for s in shares:
			if re.search(' ',s) or self.utils.isisin(s) or self.utils.ismorn(s):
				continue
			if shareurl == '':
				shareurl = s
			else:
				shareurl = shareurl + '+' + s
		if shareurl == '':
			return yhoshares
		yahoourl = 'http://uk.old.finance.yahoo.com/d/quotes.csv?s=%s&f=sl1t1n' % shareurl
		socket.setdefaulttimeout(5)
		try:
			fd = urllib2.urlopen(yahoourl)
			yho = fd.read()
			fd.close()
			yholist = yho.split('\n')
			for i,y in enumerate(yholist):
				if y == '':
					continue
				y = re.sub('"','',y)
				sh = y.split(',')
				if sh[2] == 'N/A':
					continue
				yhodate = datetime.datetime.strptime(sh[3]+' '+sh[2],'%m/%d/%Y %I:%M%p')
				sh[3] = yhodate.strftime('%Y%m%d')
				sh[2] = yhodate.strftime('%H:%M')
				yhoshares.append(sh)
		except Exception,e:
			pass
		return yhoshares

	def getmorningstarquotes(self,shares):
	# get latest mutual fund quotes from morningstar dot se
		mornshares = []
		mshares = []
		for s in shares:
			if not self.utils.ismorn(s):
				continue
			mshares.append(s)
		socket.setdefaulttimeout(5)
		for symbol in mshares:
			url = "http://quote.morningstar.com/fund/f.aspx?t=%s" % symbol
			try:
				fd = urllib2.urlopen(url)
				morn = fd.read()
				fd.close()
				pnav = re.compile('NAV:"(\d*?\,?\d+?.\d+?)"')
				pnam = re.compile('CompanyName:"(.+?)"')
				pdat = re.compile('LastDate:"(\d{4}-\d{2}-\d{2})')
				nav = pnav.findall(morn)
				nam = pnam.findall(morn)
				dat = pdat.findall(morn)
				#print nav,nam,dat
				if nav == [] or nam == [] or dat == []:
					continue
				pcom = re.compile(',')
				nav[0] = pcom.sub('',nav[0])
				if not self.utils.isfloat(nav[0]):
					continue
				mosdate = datetime.datetime.strptime(dat[0],'%Y-%m-%d')
				mornshares.append([symbol,nav[0],'17:00',mosdate.strftime('%Y%m%d'),nam[0]])
			except Exception,e:
				pass
		return mornshares

	def getecbrates(self,base,currencies=[]):
	# get latest exchange rates from the ECB and re-calculate result to base currency
		ecbrates = []
		ratedate = ''
		ecburl = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
		socket.setdefaulttimeout(5)
		try:
			fd = urllib2.urlopen(ecburl)
			ecb = fd.read()
			fd.close()
			ecblist = ecb.split('\n')
			for i,e in enumerate(ecblist):
				if e == '':
					continue
				if re.search('time',e):
					ratedate = re.search('time=\'.*?\'',e).group()
					ratedate = re.sub('\'','',ratedate)
					ratedate = re.sub('-','',ratedate)
					ratedate = ratedate.split('=')[1]
				if not re.search('currency',e):
					continue
				e = re.sub('\t','',e)
				currency = re.search('currency=\'.*?\'',e).group()
				currency = re.sub('\'','',currency)
				currency = currency.split('=')[1]
				rate = re.search('rate=\'.*?\'',e).group()
				rate = re.sub('\'','',rate)
				rate = rate.split('=')[1]
				ecbrates.append([ratedate,currency,rate])
			ecbrates.append([ratedate,'EUR','1.0'])
			ecbrates = self._calcecbtobase(base,ecbrates)
			newrates = []
			if not currencies == []:
				for c in currencies:
					for r in ecbrates:
						if r[1] == c:
							newrates.append(r)
				ecbrates = newrates
		except Exception,e:
			pass
		newrates = []
		for e in ecbrates:
			newrates.append([e[1],e[2],'17:00',e[0],e[1]])
		return newrates

	def _calcecbtobase(self,base,rates):
	# re-calculate ecb result depeding on base currency
		newrates = []
		baserate = 0
		for r in rates:
			if r[1] == base:
				baserate = float(r[2])
		if baserate == 1.0:
			return rates
		if not baserate == 0:
			for r in rates:
				rv = self.utils.rstr(baserate / float(r[2]),4)
				newrates.append([r[0],r[1],rv])
		return newrates
