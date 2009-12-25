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
		class myHttpErrorHandler(urllib2.HTTPDefaultErrorHandler):
			def http_error_default(self, req, fp, code, msg, hdrs):
					logging.info(u"访问出错: (%s,%s) %s \nheaders=%s",code,msg,req.get_full_url(),hdrs)
					return fp
##				logging.info(u"访问%s出错: %s,%s\nhdrs=%s",req.get_full_url(),code,msg,hdrs.readheaders())

		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj),myHttpErrorHandler)
		self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
		urllib2.install_opener(self.opener)
		self.opener.handle_open['http'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息
		self.opener.handle_open['https'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息

		self.verify=''

		self.policyNo='0000000009846'
##		self.policyNo='0000000009070'
		self.productNo='9846'
##		self.productNo='9070'

		self.pShowCart=re.compile(ur'商品编号：(\d+)'.encode('gbk'))
		self.pPay=re.compile(ur'<td>(\d+)</td>'.encode('gbk'))
		self.pCartVersion=re.compile(ur'<input id="cartversion" type="hidden" value="([a-z|0-9|-]+)" />'.encode('gbk'))
		self.cartversion=None

		self.data={#"cartVersion":None,
			"ident":"01",
			"cardno":"6225123456712458",
			"password":"584692",
			"expiredMonth":12,
			"expiredYear":12,
			"cvv":"123",
			"useBillAddress":True,
			"receiverName":"",
			"receiverIdentNo":"11024519881212457",
			"receiverPhone":"13914525782",
			"receiverAddress":"",
			"receiverPostalCode":"",
			"canelWhenOutOfStocks":[False]}
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
			self.ShowCart() # 查看购物车

	def ShowCart(self):
		logging.info(u"(2)查看购物车...")
		r=self.getResponse('http://ccclub.cmbchina.com/ccclub/Purchase/ShowCart.aspx')
		m=self.pShowCart.search(r[0])
		if m:
			logging.debug(u"%s",m.group())
			if m.group(1)==self.productNo:
				logging.info(u"购物车中找到目标商品！%s",self.productNo)
				self.Pay() # 去收银台结算
			else:
				logging.info(u"找到非目标商品编号 %s",m.group(1))
		else:
			logging.info(u"未找到商品编号！\n%s",r[0])

	def Pay(self):
		logging.info(u"(3)确认并支付订单...")
		r=self.getResponse('https://ccclub.cmbchina.com/ccclub/Purchase/Pay.aspx')
		m=self.pPay.search(r[0])
		logging.debug(u"%s",m.group())
		if m:
			if m.group(1)==self.productNo:
				logging.info(u"确认包含目标商品 %s",m.group(1))
				m=self.pCartVersion.search(r[0])
				if m:
					logging.info(u"cartversion=%s",m.group(1))
					logging.debug(u"%s",m.group())
					self.cartversion=m.group(1)
					self.data["cartVersion"]=self.cartversion

					self.PayNow1(self.getCookie()) # 立即付款

##					self.PayNow2(self.getCookie()) # 立即付款
				else:
					logging.info(u"找不到cartversion!")
			else:
				logging.info(u"商品")
		else:
			logging.info(u"没有包含商品!\n%s",r[0])

	def PayNow1(self,c):
		logging.info(u"(4)立即付款1...")
		header={}

##		header['Cookie']='C3Single.AuthSSL=aGx6hSUsFAgK0bbh7H7z1ualSp6vK0So; C3Single.Auth=CLNO=00183B3FxQ3O122509&SLNO=ypCgRL8oHicC9t8l5IOfI3NggBerMYXE'
##		header['Cookie']=c

		header['Host']='ccclub.cmbchina.com'
##		header['Connection']='keep-alive'
		header['Content-Type']='application/json; charset=utf-8'
		header['X-Requested-With']='XMLHttpRequest'
		header['Referer']='https://ccclub.cmbchina.com/ccclub/Purchase/Pay.aspx'
		r=self.getResponse('https://ccclub.cmbchina.com/ccclub/Purchase/ForPurchase.asmx/GuestPay',
	    data=None,
##			body=json.dumps(self.data,separators=(',',':')),
			body=json.JSONEncoder(separators=(',',':')).encode(self.data),
			headers=header)
		logging.info(u"调用返回: %s",r[0])


	def PayNow2(self,cookies):
		logging.info(u"(4)立即付款2...")
		addr=urlparse.urlparse('https://ccclub.cmbchina.com/ccclub/Purchase/ForPurchase.asmx')
		try:
			header={}
##			header['Cookie']='C3Single.AuthSSL=aGx6hSUsFAgK0bbh7H7z1ualSp6vK0So; C3Single.Auth=CLNO=00183B3FxQ3O122509&SLNO=ypCgRL8oHicC9t8l5IOfI3NggBerMYXE'
			header['Cookie']=cookies
			header['Host']=addr[1] #'ccclub.cmbchina.com'
			header['Content-Type']='application/json; charset=utf-8'
			header['X-Requested-With']='XMLHttpRequest'
			header['Referer']='https://ccclub.cmbchina.com/ccclub/Purchase/Pay.aspx'
			logging.info(u"连接到 %s ...",addr[1])
			conn=httplib.HTTPSConnection(addr[1])
			conn.set_debuglevel(1)
			logging.info(u"发送请求: %s",json.dumps(self.data,separators=(',',':')))
			s=StringIO()
			pprint(header,s)
			logging.debug(u"额外的headers: %s",s.getvalue())
			s.close()
			conn.request('POST',
				'/ccclub/Purchase/ForPurchase.asmx/GuestPay',
				json.dumps(self.data,separators=(',',':')),header)
			resp=conn.getresponse()
			r=resp.read()
			logging.info(u"返回: \n%s",r)
		except Exception,e:
			logging.info(u"发生异常: %s",e)
			return None

	def run(self):
		try:
			self.AddToCart()
		except KeyboardInterrupt:
			logging.info(u"用户中断执行.")

		logging.info(u"执行完毕.")

	def getResponse(self,url,data=None,body=None,headers={}):
		u"""获得请求url的响应 data将被urlencode后发送，body则会原样发送，二选一使用"""
		res,rurl=None,None
		for i in range(3): # 尝试3次
			if i!=0:
				logging.info(u"第 %d 次尝试...",i+1)
			try:
				r = self.opener.open(
					urllib2.Request(url,urllib.urlencode(data) if data else None,headers),
				  body,
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
				logging.info(u"未知错误! %s",e)

		return (res,rurl)

	def getCookie(self):
		c=''
		s=self.cj.as_lwp_str()
		logging.debug(u"cookies: %s",s)
		p=re.compile(r'Set-Cookie3: (.+?)\s')
		a=p.findall(s)
		a.reverse()
		for i in a:
			if c:
				c+=' '
			c+=i
		c=c.replace('"','')
		c=c[:-1]
		logging.info(u"构造的Cookie: %s",c)
		return c

if __name__=='__main__':
	import logging
##	from lxml import etree
	import re, time#, thread, webbrowser
	import urllib, urllib2, cookielib, json
	from pprint import pprint
	from cStringIO import StringIO
	import os
	import datetime
##	import socket
	import sys
	import httplib
	import xml.parsers.expat
	import urlparse

	import cProfile,pstats
	cProfile.run('''CMB().run()''',ur'd:\testcmb-profile.txt')
	#p=pstats.Stats(ur'd:\testcmb-profile.txt')
	#p.sort_stats('time', 'cum').print_stats('testcmb')
