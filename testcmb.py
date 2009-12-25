#!/usr/bin/env python
#coding=utf-8

class CMB(object):
	def __init__(self):
		reload(sys)
		sys.setdefaultencoding('gbk')
		self.curdir=os.path.abspath('.')

		# logging to file
		self.logdir=u'd:\\'
		if self.logdir:
			if not os.path.isabs(self.logdir):
				self.logdir=os.path.join(self.curdir,self.logdir)
			self.logfile=os.path.join(self.logdir,'testcmb-%s.log'%(time.strftime('%Y%m%d'),))
			logging.basicConfig(level=logging.DEBUG,
		#			format="%(asctime)s %(levelname)s %(funcName)s | %(message)s",
				  format='%(asctime)s %(thread)d %(levelname)s %(funcName)s %(lineno)d | %(message)s',
				  datefmt='%H:%M:%S',
				  filename=self.logfile,
				  filemode='a')
			# loggin to console
			console=logging.StreamHandler()
			console.setLevel(logging.INFO)
			console.setFormatter(logging.Formatter('%(thread)d %(message)s'))
			logging.getLogger('').addHandler(console)
			logging.info(u"log file: %s",self.logfile)

		logging.info(u"\n\n%s\n%s start %s %s\n%s\n",'='*75,'='*((75-8-len(sys.argv[0]))/2),sys.argv[0],'='*((75-8-len(sys.argv[0]))/2),'='*75)

		self.cookiefile=ur'd:\testcmb.cookie'
		logging.info(u"cookie file: %s",self.cookiefile)

		self.cj = cookielib.LWPCookieJar()
		try:
			self.cj.revert(self.cookiefile)
		except:
			None
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
		urllib2.install_opener(self.opener)
		self.opener.handle_open['http'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息

		self.verify=''

		self.policyNo='0000000009846'
##		self.policyNo='0000000009070'
		self.productName='大行自行车'
		self.productNo='9846'
##		self.productNo='9070'

		self.pShowCart=re.compile(ur'商品编号：(\d+)'.encode('gbk'))
		self.pPay=re.compile(ur'<td>(\d+)</td>'.encode('gbk'))
		self.pCartVersion=re.compile(ur'<input id="cartversion" type="hidden" value="([a-z|0-9|-]+)" />'.encode('gbk'))
		self.cartversion=None

		logging.info(u"%s 初始化完成.",self.__class__.__name__)

	def AddToCart(self):
		logging.info(u"(1)放入购物车...")
		r=self.getResponse('http://ccclub.cmbchina.com/ccclub/Purchase/AddToCart.aspx?policyNo=%s'%(self.policyNo,))
		i=r[0].find(u'商品已成功放入购物车！')
		if i==-1:
			logging.info(u"失败! \n%s",r[0])
		else:
			logging.info(u"商品已成功放入购物车！%d",i)
			self.cj.save(self.cookiefile)
			self.ShowCart()

	def ShowCart(self):
		logging.info(u"(2)查看购物车...")
		r=self.getResponse('http://ccclub.cmbchina.com/ccclub/Purchase/ShowCart.aspx')
		m=self.pShowCart.search(r[0])
		logging.debug(u"%s",m.group())
		if m:
			if m.group(1)==self.productNo:
				logging.info(u"成功放入购物车.")
				self.Pay()
			else:
				logging.info(u"找到非目标商品编号 %s",m.group(1))
		else:
			logging.info(u"未找到商品编号！\n%s",r[0])

	def Pay(self):
		logging.info(u"(3)确认并支付订单...")
		r=self.getResponse('https://ccclub.cmbchina.com//ccclub/Purchase/Pay.aspx')
		m=self.pPay.search(r[0])
		logging.debug(u"%s",m.group())
		if m:
			if m.group(1)==self.productNo:
				logging.info(u"包含目标商品 %s",m.group(1))
				m=self.pCartVersion.search(r[0])
				if m:
					logging.info(u"cartversion=%s",m.group(1))
					self.cartversion=m.group(1)
					self.PayNow()
				else:
					logging.info(u"找不到cartversion!")
			else:
				logging.info(u"商品")
		else:
			logging.info(u"没有包含商品!\n%s",r[0])

	def PayNow(self):
		logging.info(u"(4)立即支付...")
##		data=(("cartVersion",self.cartversion),
##			("ident","01"),
##			("cardno","6225015785641257"),
##			("password","584692"),
##			("expiredMonth","06"),
##			("expiredYear","11"),
##			("cvv","358"),
##			("useBillAddress",True),
##			("receiverName",""),
##			("receiverIdentNo",""),
##			("receiverPhone","13915715429"),
##			("receiverAddress",""),
##			("receiverPostalCode",""),
##			("canelWhenOutOfStocks","[false]"))
		data={"cartVersion":self.cartversion,
			"ident":"01",
			"cardno":"6225015785641257",
			"password":"584692",
			"expiredMonth":6,
			"expiredYear":11,
			"cvv":358,
			"useBillAddress":True,
			"receiverName":"",
			"receiverIdentNo":"11010119880601114X",
			"receiverPhone":"13915715429",
			"receiverAddress":"",
			"receiverPostalCode":"",
			"canelWhenOutOfStocks":[False]}

##		r=self.getResponse('https://ccclub.cmbchina.com/ccclub/Purchase/ForPurchase.asmx/GuestPay',data)
##		logging.info(u"%s",r[0])
		s=soapRequest()
		s.GuestPay(data)

	def run(self):
		try:
			self.AddToCart()
		except KeyboardInterrupt:
			logging.info(u"用户中断执行.")

		logging.info(u"执行完毕.")

	def getResponse(self,url,data=None,headers={}):
		u"""获得请求url的响应"""
		res,rurl=None,None
		for i in range(3): # 尝试3次
			if i!=0:
				logging.info(u"第 %d 次尝试...",i+1)
			try:
				r = self.opener.open(
					urllib2.Request(url,urllib.urlencode(data) if data else None,headers),
					timeout=5)
				res=r.read()
				rurl=r.geturl()
				break
			except urllib2.HTTPError,e:
				logging.exception(u"请求出错！ %s",e)
			except urllib2.URLError,e:
				logging.exception(u"访问地址失败! %s",e)
			except IOError,e:
				logging.info(u"IO错误! %s",e)
			except Exception,e:
				logging.info(u"未知错误!")

		return (res,rurl)


class soapRequest:
	def __init__(self):
		self.url='https://ccclub.cmbchina.com/ccclub/Purchase/ForPurchase.asmx'
		self.xmlns='https://ccclub.cmbchina.com'

	def genJsonRequest(self,data):
		ret=json.dumps(data,separators=(',',':'))
##		logging.debug(u"json数据: %s",ret)
		return ret

	def genXmlRequest(self,funcName,strxmlns,dictarg):
		ret="<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soapenc=\"http://schemas.xmlsoap.org/soap/encoding/\">"
		ret+="<soap:Body>"
		ret+="<%s xmlns=\"%s/\">"%(funcName,strxmlns)
		for (k,v) in dictarg:
			if v is int:
				ret+="<%s>%s</%s>"%(k,str(v),k)
			else:
				ret+="<%s>%s</%s>"%(k,v,k)
		ret+="</%s>"%(funcName)
		ret+="</soap:Body>"
		ret+="</soap:Envelope>"
		return ret

	def GuestPay(self,data):
		func="GuestPay"
		addr=urlparse.urlparse(self.url)

		try:
			header={}
			header['Host']='ccclub.cmbchina.com'
			header['Content-Type']='application/json; charset=utf-8'
			header['X-Requested-With']='XMLHttpRequest'
			header['Referer']='https://ccclub.cmbchina.com/ccclub/Purchase/Pay.aspx'
			logging.info(u"连接到 %s ...",addr[1])
			conn=httplib.HTTPConnection(addr[1])
			logging.info(u"发送请求: %s",self.genJsonRequest(data))
			s=StringIO()
			pprint(header,s)
			logging.info(u"额外的headers: %s",s.getvalue())
			s.close()
##			conn.request('POST','ForPurchase.asmx/GuestPay',self.genJsonRequest(data),header)
			conn.request('POST','https://ccclub.cmbchina.com/ccclub/Purchase/ForPurchase.asmx/GuestPay',self.genJsonRequest(data),header)
			resp=conn.getresponse()
			dataxml=resp.read()
			logging.info(u"返回: \n%s",dataxml)
		except Exception,e:
			logging.info(u"发生异常: %s",e)
			return None

		return dataxml

##	def GuestPay(self,data):
##		func="GuestPay"
##		addr=urlparse.urlparse(self.url)
##
##		try:
##			header={}
##			header['Host']='ccclub.cmbchina.com'
##			header['Content-Type']='text/xml'
##			header['SOAPAction']='%s'%('\"ForPurchase.asmx/GuestPay"',)
##			logging.info(u"连接到 %s ...",addr[1])
##			conn=httplib.HTTPConnection(addr[1])
##			logging.info(u"发送请求: %s",self.genXmlRequest(func,self.xmlns,data))
##			s=StringIO()
##			pprint(header,s)
##			logging.info(u"额外的headers: %s",s.getvalue())
##			s.close()
##			conn.request('POST','ForPurchase.asmx/GuestPay',self.genXmlRequest(func,self.xmlns,data),header)
####			logging.info(u"获取返回信息...")
##			resp=conn.getresponse()
####			logging.info(u"读取返回信息...")
##			dataxml=resp.read()
##			logging.info(u"返回: \n%s",dataxml.decode('utf8'))
##		except Exception,e:
##			logging.info(u"发生异常: %s",e)
##			return None
##
##		return dataxml

if __name__=='__main__':
	import logging
	from lxml import etree
	import re, time#, thread, webbrowser
	import urllib, urllib2, cookielib, json
	from pprint import pprint
	from cStringIO import StringIO
	import os
	import datetime
	import socket
	import sys
	import httplib
	import xml.parsers.expat
	import urlparse

	import cProfile,pstats
	cProfile.run('''CMB().run()''',ur'd:\testcmb-profile.txt')
	#p=pstats.Stats(ur'd:\testcmb-profile.txt')
	#p.sort_stats('time', 'cum').print_stats('testcmb')
