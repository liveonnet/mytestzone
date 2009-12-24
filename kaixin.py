#!/usr/bin/env python
#coding=utf-8

#def GetAccCode(content):
	#u"""直接调用MSScriptControl.ScriptControl执行脚本"""
##	regex=re.compile('function\s*?checkSwf\(\)\s*{[\s\S]*if\s\("function[\s\S]*gotoMyself\(\)\;\s*}\s*\}\s*\}\s*(?P<acc>var [\s\S]*function\s*?acc\(\)\s*{[\s\S]*var\sacc[\s\S]*return acc\;\s*\}[\S\s]*)function _bodyonload',re.IGNORECASE)
	#regex=re.compile(r"}\s*(?P<acc>var.*?function\s+acc\(\).*?)function\s+_bodyonload\(\)",re.I|re.S)
##	con=regex.search(content)
	#con=re.search(regex,content)
	#print '*'*30
	#pprint(con.group('acc'))
	#print '*'*30
	## 需要安装Windows ScriptControl 插件
	## 地址 http://download.microsoft.com/download/winscript56/Install/1.0/W982KMe/CN/sct10chs.exe
	#js=win32com.client.Dispatch('MSScriptControl.ScriptControl')
	#js.Language='JavaScript'
	#js.AllowUI=False
	#js.AddCode(con.group('acc'))
	#acc=js.Run('acc')
	#return acc


class Kaixin(object):
	def __init__(self,inifile='kaixin.ini'):
		reload(sys)
		sys.setdefaultencoding('gbk')
		self.curdir=os.path.abspath('.')

		self.inifile=inifile
		if not os.path.isabs(inifile):
			self.inifile=os.path.join(self.curdir,self.inifile)

		self.cfg=ConfigParser.SafeConfigParser()
		self.cfg.readfp(codecs.open(self.inifile,'r','utf-8-sig'))

		# logging to file
		self.logdir=self.cfg.get('account','logdir',self.curdir)
		if self.logdir:
			if not os.path.isabs(self.logdir):
				self.logdir=os.path.join(self.curdir,self.logdir)
			self.logfile=os.path.join(self.logdir,'kaixin-%s.log'%(time.strftime('%Y%m%d'),))
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
		else: # 为空则认为是log不写入文件，只输出到stdout
			logging.basicConfig(level=logging.INFO,
				format='%(thread)d %(message)s')
			logging.info(u"=== log不写入文件.===")

		logging.info(u"\n\n%s\n%s start %s %s\n%s\n",'='*75,'='*((75-8-len(sys.argv[0]))/2),sys.argv[0],'='*((75-8-len(sys.argv[0]))/2),'='*75)
		logging.info(u"ini file: %s",self.inifile)

		self.email=self.cfg.get('account','email')
		self.pwd=self.cfg.get('account','pwd')
		self.cookiefile=self.cfg.get('account','cookiefile')
		logging.info(u"cookie file: %s",self.cookiefile)

		self.signed_in = False
		self.cj = cookielib.LWPCookieJar()
		try:
			self.cj.revert(self.cookiefile)
		except:
			None
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
		urllib2.install_opener(self.opener)
		#self.opener.handle_open['http'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息

		seedlist=self.cfg.get('account','seedlist')
		self.seedlist=json.JSONDecoder().decode(seedlist)
		logging.info(u"已知作物数 %d",len(self.seedlist))
		#self.seedlist.sort(cmp=lambda x,y: cmp(x[0], y[0]),reverse=True)

		animallist=self.cfg.get('account','animallist')
		self.animallist=json.JSONDecoder().decode(animallist)
		logging.info(u"已知牧场产品数 %d",len(self.animallist))

		ignoreseeds=self.cfg.get('account','ignoreseeds')
		self.ignoreseeds=json.JSONDecoder().decode(ignoreseeds) # 忽略不处理的作物

		forcestealseeds=self.cfg.get('account','forcestealseeds')
		self.forcestealseeds=json.JSONDecoder().decode(forcestealseeds) # 强制偷取的作物(不考虑其价值)

		antisteal=self.cfg.get('account','antisteal')
		self.antisteal=json.JSONDecoder().decode(antisteal) # 有防偷期的动物
		#pprint(self.antisteal)

		self.internal=self.cfg.getint('account','internal') # 轮询间隔
		logging.info(u"轮询间隔 %d",self.internal)
		self.bStealCrop=self.cfg.getboolean('account','StealCrop') # 偷农场作物
		self.bStealRanch=self.cfg.getboolean('account','StealRanch') # 偷牧场副产品
		self.bGetGranaryInfo=self.cfg.getboolean('account','GetGranaryInfo') # 获取仓库信息(据此更新seedlist的价格)

		friends=self.cfg.get('account','friends')
		self.friends=json.JSONDecoder().decode(friends) # 好友列表
		logging.info(u"已知好友数 %d",len(self.friends))

		# 打印忽略作物
		s=StringIO()
		s.write(u"")
		for i,j in [(x[1],x[2]) for x in self.seedlist if x[1] in self.ignoreseeds]:
			s.write(u"%s(%s) "%(j,i))
		logging.info(u"忽略作物: %s",s.getvalue())
		s.close()

		# 打印强制偷取的作物
		s=StringIO()
		s.write(u"")
		for i,j in [(x[1],x[2]) for x in self.seedlist if x[1] in self.forcestealseeds]:
			s.write(u"%s(%s) "%(j,i))
		logging.info(u"强制偷取的作物: %s",s.getvalue())
		s.close()

		self.friends4garden=[] # 待检查garden的用户
		self.friends4ranch=[] # 待检查ranch的用户
		self.crops2steal=[] # 待偷的作物列表

		self.tasklist={} # 定时任务

		# 统计收获
		if self.logdir:
			self.statistics=shelve.open(os.path.join(self.logdir,'kaixin.statistics'))
		else:
			self.statistics=shelve.open(os.path.join(self.curdir,'kaixin.statistics'))

		self.verify=''

		logging.info(u"%s 初始化完成.",self.__class__.__name__)

	def signin(self):
		u"""登录"""
		r = self.getResponse('http://www.kaixin001.com/home/')
		if r[1] == 'http://www.kaixin001.com/?flag=1&url=%2Fhome%2F':
			logging.debug(u"需要登录!")
			params = {'email':self.email, 'password':self.pwd, 'remember':1,'invisible_mode':0,'url':'/home/'}
			r = self.getResponse('http://www.kaixin001.com/login/login.php',params)

			m=re.match(r'http://www.kaixin001.com/home/\?uid=(\d{7,}|)',r[1])
			if m:
				logging.debug(u"登录成功! uid=%s .",m.group(1))
				self.cj.save(self.cookiefile)
				self.signed_in = True
			else:
				logging.info(u"登录失败! %s",r[1])
				#logging.info("%s",r.read())

				#for i in xrange(1):
					## 帐号被认为使用了外挂要输入验证码 下面提取验证码图片
					#rcode='%.16f_%d'%(random(),time.time()*1000) # 保存生成的随机数，用于需要验证码的登录请求
					#randimgurl='http://www.kaixin001.com/interface/regcreatepng.php?randnum='+ rcode + '&norect=1'
					#import webbrowser
					#webbrowser.open(randimgurl)
					##r=urllib2.urlopen(randimgurl)
					##with open(ur'd:\img.gif','wb') as f:
						##f.write(r.read())
					##r.close()

					##logging.info("image file is d:\\img.gif")
					#raw_input('(%d)input the code to d:\\img.txt: '%(i,))
					#with open(ur'd:\img.txt') as f:
						#code=f.read()
						#code.strip()
						#logging.info("you input code: "+code)

					#params = {'email':self.email, 'password':self.pwd,
						#'remember':1,'invisible_mode':0,'url':'/home/',
						#'rcode':rcode,'rpkey':'','diarykey':'',
						#'code':code}
					#req = urllib2.Request(
						#'http://www.kaixin001.com/login/login.php',
						#urllib.urlencode(params)
					#)
					#r = self.opener.open(req)
					#logging.info("r.geturl()=%s",r.geturl())
					#if re.match(r'http://www.kaixin001.com/home/',r.geturl()):
						#logging.info("logging in ! %s",r.geturl())
						#self.signed_in=True
						#break
					#else:
						#logging.info("logging in failed!(code error?) %s\n%s",r.geturl(),r.read())
						#r.close()

				if not self.signed_in:
					sys.exit(1)
		else:
			logging.debug(u"无需登录!")
			self.signed_in = True

	def getFriends4garden(self):
		u"""获取可偷取花园作物的好友列表"""
		if not self.signed_in:
			self.signin()
		if self.signed_in:
			del self.friends4garden[:]
			r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
			m = re.search('var g_verify = "(.+)";', r[0])
			self.verify = m.group(1)
			#logging.info(u"verify=%s",self.verify)

			#req = urllib2.Request(
				#'http://www.kaixin001.com/!house/!garden/getfriendmature.php',
				#urllib.urlencode({'verify':self.verify})
			#)

			#r = self.opener.open(req)
			##s=r.read()
			##open('d:\\res.txt','w').write(s)
			##data = json.loads(s)[u'friend']
			#data = json.loads(r.read())[u'friend']
			##pprint(data)

			#for f in data:
				#fname,fuid=f['realname'],unicode(f['uid'])
				#self.friends4garden.append((fname,fuid))
				#if fuid not in self.friends:
					#self.friends[fuid]=fname


			r = self.getResponse('http://www.kaixin001.com/!house/!garden/friendlist.php',
				{'verify':self.verify})

			data = json.loads(r[0])
			#pprint(data)

			for f in data:
				#if f.get('harvest',None):
				if f.get('antiharvest',None):
					pass
					#logging.info(u"%s(%s) 有防偷!",f['real_name'],f['uid'])
				fname,fuid=f['real_name'],unicode(f['uid'])
				if (fname,fuid) not in self.friends4garden:
					self.friends4garden.append((fname,fuid))
				if fuid not in self.friends:
					self.friends[fuid]=fname

			#logging.info(u"self.friends4garden=%s",self.friends4garden)
			#logging.info(u"self.friends=%s",self.friends)
			#raw_input()


	def checkGarden(self):
		u"""地块	1,2, 3, 9,13
							4,5, 8,11,14
							6,7,10,12,15
		"""
		logging.info(u"共检查%d个好友的花园.",len(self.friends4garden))

		p=re.compile(ur'(?:已产|产量)?：(?P<all>\d+)<br />剩余：(?P<left>\d+)')
		pgrow=re.compile(ur'生长阶段：(\d+)%.+?距离收获：(\d+天)?(\d+小时)?(\d+分)?(\d+秒)?')

		cnt=0
		del self.crops2steal[:]
		for fname,fuid in self.friends4garden:
			cnt+=1
			#if fuid==u"115502":		continue # 跳过
			logging.info(u" %02d) 检查 %s(%s)... ",cnt,fname,fuid)
			r = self.getResponse('http://www.kaixin001.com/house/garden/getconf.php',
				{'verify':self.verify,'fuid':fuid})
			tree = etree.fromstring(r[0])

			items=tree.xpath('garden/item')
#			logging.debug("total %d farms in this garden",len(items))
			for i in items:
				farmnum=i.xpath('farmnum')[0].text

				try:
					name=i.xpath('name')[0].text
				except IndexError:
					#logging.debug(u"地块 %s 为空",farmnum)
					continue

				try:
					crops=i.xpath('crops')[0].text
				except IndexError:
					logging.debug(u"地块 %s 是 %s(枯死的植物)!",farmnum,name)
					continue

				farm=i.xpath('farm')[0].text
				if farm.find(u'爱心地')!=-1:
					friendname=farm=i.xpath('friendname')[0].text
					#logging.debug(u"地块 %s 是 %s 的爱心地!",farmnum,friendname)
					continue

				seedid=i.xpath('seedid')[0].text
				if seedid in self.ignoreseeds:
					#logging.info(u"忽略 %s(%s)",name,seedid)
					continue

				# 检查seedid是否是未知的
				if seedid not in [x[1] for x in self.seedlist]: # 未知
					self.seedlist.append([4321,seedid,name])
					logging.info(u"发现未知作物:\n\t[4321,\"%s\",\"%s\"],\n",seedid,name)

				m=re.match(p,crops)
				if m:
					all=m.group('all')
					left=int(m.group('left'))
					if crops.find(u'已摘过')==-1 and crops.find(u'已枯死')==-1:

						n=re.search(ur'再过(\d+小时)?(\d+分)?(\d+秒)?好友可摘',crops)
						if n:
							logging.info(u"地块 %s %s(%s) 在防偷期! (%s)",farmnum,name,seedid,crops)

							scd=self.getSleepTime(n.groups())
							if scd<self.internal+10: # 下次轮询前不需执行则不加入定时任务
								k='crop-%s-%s-%s'%(fuid,farmnum,seedid)
								if k not in self.tasklist: # 相同的任务不存在
									# 判断是否存在同一块地不同seedid的任务，如果存在则先删除
									samek='crop-%s-%s-'%(fuid,farmnum)
									for i in self.tasklist.keys():
										if i.startswith(samek):
											logging.info(u"终止并删除对同一块地的定时任务 key=%s",samek)
											self.tasklist[i].cancel()
											del self.tasklist[i]
								else:
									logging.info(u"更新前删除相同的定时任务")
									self.tasklist[k].cancel()
									del self.tasklist[k]

								logging.info(u"加入定时执行队列 key=%s %d (%s,%s,%s)",k,scd,farmnum,seedid,fuid)
								if scd<60:
									t=Timer(scd+0.1, self.stealOneCrop,(farmnum,seedid,fuid,k))
								else:
									t=Timer(scd, self.task_garden,(farmnum,seedid,fuid,k))
								t.start()
								self.tasklist[k]=t

						elif left>1:
							logging.info(u"(可偷) %d/%s (地块%s--%s(%s)--%s)",left,all,farmnum,name,seedid,crops)
							self.crops2steal.append((farmnum,seedid,fuid))
					else:
						#logging.info(u"地块 %s %s(%s) 已摘过/已枯死 (%s)",farmnum,name,seedid,crops)
						pass
				else:
					pass
					#m=re.search(pgrow,crops)
					#if m:
						#precent=m.group(1)
						#scd=self.getSleepTime(m.groups()[1:])
						#rawscd=(m.group(2) and [m.group(2)] or [''])[0]\
							#+(m.group(3) and [m.group(3)] or [''])[0]\
							#+(m.group(4) and [m.group(4)] or [''])[0]\
							#+(m.group(5) and [m.group(5)] or [''])[0]
						#logging.debug(u"地块 %s %s(%s) 处于生长期 %s%% 距离收获 %s 秒(%s)",farmnum,name,seedid,precent,scd,rawscd)
					#else:
						#logging.debug(u"地块 %s %s(%s) 处于生长期 (%s)",farmnum,name,seedid,crops)

			# 查看有没有蜂蜜可偷
			items=tree.xpath('account/yh_honey')
			if items:
				count=items[0].xpath('count')[0].text
				count_a=items[0].xpath('count_a')[0].text # 洋槐蜂蜜
				count_b=items[0].xpath('count_b')[0].text # 枸杞蜂蜜
				count_c=items[0].xpath('count_c')[0].text # 党参蜂蜜
				total=items[0].xpath('total')[0].text
				sumtext=items[0].xpath('sum')[0].text
				#logging.info(u"洋槐蜂蜜 %s, 枸杞蜂蜜 %s, 党参蜂蜜 %s, count/total/sum=%s/%s/%s",
					#count_a,count_b,count_c,count,total,sumtext)

				items=tree.xpath('account/yh_stealinfo')
				if items:
					stealinfo=items[0].text
					if stealinfo.find(u'已摘过')!=-1:
						logging.info(u"蜂蜜 已摘过! (%s)",stealinfo)
				else:
					logging.info(u"(可偷) 洋槐蜂蜜 %s, 枸杞蜂蜜 %s, 党参蜂蜜 %s, count/total/sum=%s/%s/%s",
						count_a,count_b,count_c,count,total,sumtext)
					self.stealHoney(fuid)


	def stealCrop(self):
		u"""依次尝试偷取值得偷的作物"""
		# 只偷贵的
		tosteal=self.getValueItems(1000)
		logging.info(u"根据作物价值偷%d个.",len(tosteal))
		if tosteal==0:
			return True

		# 将 crops2steal 打乱顺序
		s=StringIO()
		pprint(tosteal,s)
		logging.info(u"original\n%s",s.getvalue())
		s.close()
		tosteal=self.__class__.OutOfOrder(tosteal,1)
		t=StringIO()
		pprint(tosteal,t)
		logging.info(u"processed\n%s",t.getvalue())
		t.close()

		# 看是否有曼陀罗，如果有则放到最后偷
		foundStramonium=False
		seednamelist=[x[1] for x in self.seedlist if x[2].find(u"曼陀罗")!=-1] # 叫曼陀罗的植物的seedid列表
		toend=[] # 存放需要后移的曼陀罗
		for farmnum,seedid,fuid in tosteal:
			if seedid in seednamelist:
				foundStramonium=True
				logging.info(u"发现有曼陀罗 (%s,%s,%s)",farmnum,seedid,fuid)
				toend.append((farmnum,seedid,fuid))
		if foundStramonium:
			for i in toend:	tosteal.remove(i)
			#for i in toend:	tosteal.append(i) # 注释掉以避免偷取曼陀罗类作物
			#t=StringIO()
			#pprint(tosteal,t)
			#logging.info(u"found Stramonium\n%s",t.getvalue())
			#t.close()

		for idx,(farmnum,seedid,fuid) in enumerate(tosteal):
			rslt=self.stealOneCrop(farmnum,seedid,fuid)
			if rslt==False: # 被反外挂检测到
				break
			if idx!=len(tosteal)-1:
				sleeptime=uniform(3,7)
				logging.debug(u"延迟%f秒以逃避反外挂检测...",sleeptime)
				time.sleep(sleeptime)

		return True

	def stealOneCrop(self,farmnum,seedid,fuid,taskkey=''):
		u"""偷取单一作物"""
		tasklogstring=u''
		if taskkey!='':
			tasklogstring=u'[任务 %s]'%(taskkey,)
			logging.info(u"执行定时任务 %s ...",taskkey)
			# 从tasklist中删除任务
			if taskkey in self.tasklist:
				del self.tasklist[taskkey]

		logging.debug(u"<=== %s 从 %s(%s) 偷取 %s(farmnum=%s) ... ",tasklogstring,self.friends[fuid],fuid,filter(lambda x: x[1]==seedid,self.seedlist)[0][2],farmnum)
		r = self.getResponse('http://www.kaixin001.com/house/garden/havest.php',
			{'verify':self.verify,'farmnum':farmnum,'seedid':seedid,'fuid':fuid})
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!=u'succ':
			reason=tree.xpath('reason')[0].text
			logging.info(u"===> %s !!! 偷取失败! (%s,%s)",tasklogstring,ret,reason)
			if reason.find(u'正在麻醉中')!=-1:
				logging.info(u"麻醉中，不能偷植物产品.")
				return False
			#return False
			return True

		anti=tree.xpath('anti')[0].text
		if anti==u'1':
			logging.error(u"===> %s anti=1!!! 被反外挂检测到了 \n%s",tasklogstring,etree.tostring(tree,encoding='gbk'))
			return False

		try:
			leftnum=tree.xpath('leftnum')[0].text
			stealnum=tree.xpath('stealnum')[0].text
			num=tree.xpath('num')[0].text
			seedname=tree.xpath('seedname')[0].text
			logging.debug(u"%s anti=%s,leftnum=%s,stealnum=%s,num=%s,seedname=%s",tasklogstring,anti,leftnum,stealnum,num,seedname)
			logging.info(u"===> %s *** 成功偷取 %s(%s)的 %s %s",tasklogstring,self.friends[fuid],fuid,stealnum,seedname)
			self.statistics[seedname.encode('utf8')]=self.statistics.get(seedname.encode('utf8'),0)+int(stealnum)
		except IndexError:
			logging.error(u"===> %s 解析结果失败!!! \n%s",tasklogstring,etree.tostring(tree,encoding='gbk'))

		return True

	def getFriends4ranch(self):
		u"""获取可偷取牧场产品的好友列表"""
		if not self.signed_in:
			self.signin()
		if self.signed_in:
			del self.friends4ranch[:]
			r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=ranch/index.php')
			m = re.search('var g_verify = "(.+)";', r[0])
			self.verify = m.group(1)
			#logging.info(u"verify=%s",self.verify)

			r = self.getResponse('http://www.kaixin001.com/!house/!ranch/friendlist.php')
			data = json.loads(r[0])

			for f in data:
				#logging.debug(u"%s  %s",f['real_name'],f['uid'])
				fname,fuid=f['real_name'],unicode(f['uid'])
				#if f.get('harvest',None):
				if f.get('antiharvest',None):
					pass
					#logging.info(u"%s(%s) 有防偷!",fname,fuid)
				self.friends4ranch.append((fname,fuid))
				if fuid not in self.friends:
					self.friends[fuid]=fname


	def checkRanch(self):
		logging.info(u"共检查%d个好友的牧场.",len(self.friends4ranch))
		p=re.compile(ur'剩余数量：(?P<left>\d+)')

		cnt=0
		for fname,fuid in self.friends4ranch:
			cnt+=1
			logging.info(u" %02d) 检查 %s(%s)... ",cnt,fname,fuid)
			r = self.getResponse('http://www.kaixin001.com/house/ranch/getconf.php',
				{'verify':self.verify,'fuid':fuid})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!=u'succ':
				logging.error(u"===>获取牧场信息失败!!! ret=%s (%s)",ret,etree.tostring(tree,encoding='gbk'))
				continue

			items=tree.xpath('product2/item')
#			logging.debug("total %d product2 items in this garden",len(items))
			for i in items:
				try:
					fuidtext=i.xpath('uid')[0].text # fuid
					num=int(i.xpath('num')[0].text)
					stealnum=int(i.xpath('stealnum')[0].text)
					skey=i.xpath('skey')[0].text # skey
					pname=i.xpath('pname')[0].text
					#logging.info(u"pname=%s",pname)
					tips=i.xpath('tips')[0].text
					typetext=i.xpath('type')[0].text # type
					#oa=i.xpath('oa')[0].text

					if skey not in self.animallist: # 未知副产品
						logging.info(u"添加未知牧场品种 %s(%s)",skey,pname)
						self.animallist[skey]=[int(typetext),pname]
					if self.animallist[skey][1]!=pname:
						logging.info(u"牧场品种名称不符 %s(now=%s,should=%s)",skey,self.animallist[skey][1],pname)


					m=re.search(p,tips)
					if m:
						left_from_tips=m.group('left')
						if tips.find(u'距下次可收获还有')!=-1:
							logging.debug(u"%s 已收获过! (%s)",pname,tips)
							continue
						n=re.search(ur'再过(\d+小时)?(\d+分)?(\d+秒)?好友可收获',tips)
						if n:
							rawscd=(n.group(1) and [n.group(1)] or [''])[0]\
								+(n.group(2) and [n.group(2)] or [''])[0]\
								+(n.group(3) and [n.group(3)] or [''])[0]

							logging.info(u"%s 在防偷期, 再过 %s 可收获! (%s)",pname,rawscd,tips)

							scd=self.getSleepTime(n.groups())
							if scd<self.internal: # 下次轮询前不需要执行则不加入定时任务
								k='ranch-%s-%s-%s'%(fuidtext,skey,typetext)
								if k in self.tasklist: # 相同的任务已经存在
									logging.info(u"更新前删除相同任务")
									self.tasklist[k].cancel()
									del self.tasklist[k]
								logging.info(u"加入定时执行队列 key=%s %d (%s,%s,%s)",k,scd,fuidtext,skey,typetext)
								if scd<60:
									t=Timer(scd+0.15, self.stealRanchProduct,(fuidtext,skey,typetext,k))
								else:
									t=Timer(scd,self.task_ranch,(fuidtext,skey,typetext,k))
								t.start()
								self.tasklist[k]=t

							continue
				except Exception,e:
					logging.error(u"解析product2失败! (%s)(%s)",e,etree.tostring(i,encoding='gbk'))

				logging.debug(u"(可偷) %d/%d (%s--%d--%d--%s)",num-stealnum,num,pname,num,stealnum,tips)
				reslt=self.stealRanchProduct(fuidtext,skey,typetext)

			pproduct=re.compile(ur'预计产量：(\d+).+?距离可收获还有(\d+分)?(\d+秒)?')
			items=tree.xpath('animals/item')
			for i in items:
				try:
					bproduct=i.xpath('bproduct')[0].text
					if bproduct!='1':
						continue
					skey=i.xpath('skey')[0].text
					if skey not in self.animallist: # 未知副产品
						try:
							aname=i.xpath('aname')[0].text
							self.animallist[skey]=[0,aname]
							logging.info(u"添加未知牧场品种 %s(%s)",skey,aname)
						except Exception:
							logging.info(u"未知牧场品种 %s(%s)",skey,etree.tostring(i,encoding='gbk'))
							continue # 因为不知道名字，所以不处理

					tips=i.xpath('tips')[0].text
					m=re.search(pproduct,tips)
					if m:
						#logging.debug(u"item: %s",etree.tostring(i,encoding='gbk'))
						scd=self.getSleepTime(m.groups()[1:])
						rawscd=(m.group(2)!=None and [m.group(2)] or [''])[0]+\
						  (m.group(3)!=None and [m.group(3)] or [''])[0]
						logging.info(u"%s 预计产量 %s 距离收获 %d(%s)",skey,m.group(1),scd,rawscd)

						if skey in self.antisteal:
							logging.info(u"%s 有防偷期，不追踪.",skey)
							continue

						if scd<self.internal:
							k='ranch-p-%s-%s-%s'%(fuid,skey,'0')
							if k in self.tasklist: # 相同的任务已经存在
								if getattr(self.tasklist[k],'sleeptime',0)>scd: # 已存在的相同任务的等待时间更长,则替换为等待时间短的
									logging.info(u"更新前删除相同任务")
									self.tasklist[k].cancel()
									del self.tasklist[k]
								else: # 已存在的相同任务的等待时间已经是最短的，不必更新
									logging.info(u"相同任务已经存在%s(%d<=%d)，略过",k,getattr(self.tasklist[k],'sleeptime',0),scd)
									continue # 不更新
							logging.info(u"加入定时执行队列 key=%s %d (%s,%s,%s)",k,scd,fuid,skey,'0')
							if scd<60:
								t=Timer(scd+0.15, self.stealRanchProduct,(fuid,skey,'0',k))
								t.sleeptime=scd
							else:
								t=Timer(scd,self.task_ranch,(fuid,skey,'0',k))
								t.sleeptime=scd
							t.start()
							self.tasklist[k]=t

				except Exception,e:
					logging.exception(u"解析animals失败! (%s)",etree.tostring(i,encoding='gbk'))

	def stealRanchProduct(self,fuid,skey,typetext,taskkey=''):
		u"""steal one item 偷取一个牧场产品"""
		tasklogstring=u''
		if taskkey!='':
			tasklogstring=u'%s'%(taskkey,)
			#logging.info(u"%s (%s,%s,%s)...",tasklogstring,fuid,skey,typetext)
			# 从tasklist中删除任务
			if taskkey in self.tasklist:
				del self.tasklist[taskkey]


		logging.debug(u"<=== %s (%s,%s,%s) 偷取 %s(%s) 的 %s ... ",tasklogstring,fuid,skey,typetext,self.friends[fuid],fuid,self.animallist[skey][1])
		r = self.getResponse('http://www.kaixin001.com/!house/!ranch/havest.php',
			{'verify':self.verify,'fuid':fuid,'skey':skey,'seedid':'0','id':'0','type':typetext,'foodnum':'1'})
		if not r[0]:
			return False
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!=u'succ':
			reason=tree.xpath('reason')[0].text
			logging.info(u"===> %s !!! 偷取 %s(%s) 的 %s 失败! (%s,%s)",tasklogstring,self.friends[fuid],fuid,self.animallist[skey][1],ret,reason)
			return False

		try:
			res_ptype=tree.xpath('ptype')[0].text
			res_action=tree.xpath('action')[0].text
			res_num=tree.xpath('num')[0].text
			res_skey=tree.xpath('skey')[0].text
			logging.debug(u"%s action=%s,num=%s,skey=%s,ptype=%s",tasklogstring,res_action,res_num,res_skey,res_ptype)
			logging.info(u"===> %s *** 成功偷取 %s %s~",tasklogstring,res_num,self.animallist[res_skey][1])
			self.statistics[self.animallist[res_skey][1].encode('utf8')]=self.statistics.get(self.animallist[res_skey][1].encode('utf8'),0)+int(res_num)
		except IndexError:
			logging.error(u"===> %s 解析结果失败!!! \n%s",tasklogstring,etree.tostring(tree,encoding='gbk'))
			return False

		return True

	def run(self):
		#self.getSeedList()
		try:
			while True:
				if self.bGetGranaryInfo:
					self.getGranaryInfo()
					#self.saveCfg()
					self.bGetGranaryInfo=False
					logging.info(u"重新设置 getgranaryinfo=False")
					break

				if self.bStealCrop:
					self.getFriends4garden()
					self.checkGarden()
					self.stealCrop()

				if self.bStealRanch:
					self.getFriends4ranch()
					self.checkRanch()

				logging.info(u"\n%s\n%s %d 秒后再次执行(%s) ...  %s\n%s\n",'='*75,'='*15,self.internal,
					(datetime.datetime.now()+datetime.timedelta(seconds=self.internal)).strftime("%Y-%m-%d %H:%M:%S"),
					'='*15,'='*75)
				time.sleep(self.internal)
		except KeyboardInterrupt:
			logging.info(u"用户中断执行.")

		self.saveCfg()
		for k,v in self.tasklist.iteritems():
			logging.info(u"删除定时任务 %s",k)
			v.cancel()
		self.tasklist.clear()

		if len(self.statistics)!=0:
			stat=StringIO()
			for k,v in self.statistics.iteritems():
				stat.write(u"%s: %d\t"%(k.decode('utf8'),v))
			logging.info(u"统计: %s",stat.getvalue())
			stat.close()
			self.statistics.close()

		logging.info(u"执行完毕.")
		time.sleep(1)

	@staticmethod
	def OutOfOrder(l,n=4):
		u"""返回一个乱序后的list。返回的list是将list中item的顺序打乱以尽量保证列表中
		不出现连续n个item都是一个好友的情况
		"""
		def pickone(cur,sorted_key):
			u"""根据情况选择出排在cur之后的k，返回k对应的value(是个列表)中的一个值"""
			found=False
			ret=None
			for dummy,k in sorted_key:
				if found==True:
					if k not in tmp: # sorted_key 与 tmp 在k的存在与否上要保持一致
						sorted_key.remove((dummy,k))
						continue

					ret=tmp[k][0] # 返回一个值
					tmp[k].remove(ret) # 从value的list中删除掉这个值
					#tmp[k]=tmp[k][1:] # 从value的list中删除掉这个值
					if len(tmp[k])==0: # 如果value的list为空则删掉此k
						del tmp[k]
	#					sorted_key=sorted([(len(tmp[k]),k) for k in tmp.iterkeys()],reverse=True)
					break
				if k==cur: # 找到了当前cur 则下一次迭代的就是要找的k
					found=True
			return ret

		tmp={} # key为好友id，
		for i in l:
			if i[2] in tmp:
				tmp[i[2]].append(i)
			else:
				tmp[i[2]]=[i]

		# 返回一个列表，表中元素为(好友下的可偷作物数,用户id)，按可偷作物数从多到少排序
		sorted_key= sorted([(len(tmp[k]),k) for k in tmp.iterkeys()],reverse=True)
	#	pprint(sorted_key)

		try:
			puzzled_list=[]
			while len(tmp)!=0:
				cur=max([(len(tmp[k]),k) for k in tmp.iterkeys()])[1] # 找出当前可偷作物最多的好友的id
				while n<len(tmp[cur]):
					puzzled_list+=tmp[cur][:n]
					tmp[cur]=tmp[cur][n:]
					x=pickone(cur,sorted_key) # 每隔n个就插入第二多的k中的一个value
					if x:
						puzzled_list+=[x]

				puzzled_list+=tmp[cur]
				del tmp[cur]

			assert len(l)==len(puzzled_list)
		except Exception,e:
			logging.error(u"异常 (%s) ",e)
			pprint(l,console)

		return puzzled_list

	def getValueItems(self,threshold_value):
		u"""从l挑出价值大于 threshold_value 或者是强制偷取的 的 item 以列表形式返回"""
		ret=[]
		# 从seedlist中选出价值不低于threshold的seedid的列表
		threshold_list=[i[1] for i in self.seedlist if i[0]>=threshold_value]
		# 将强制要偷的seedid加入
		for i in self.forcestealseeds:
			if i not in threshold_list:
				threshold_list.append(i)

		# 从上一步结果中选出包含在可偷列表中的seed
		threshold_list=filter(lambda x: x in [i[1] for i in self.crops2steal],threshold_list)

		for i in threshold_list:
			t=[item for item in self.crops2steal if item[1]==i]
			ret+=t
		return ret

	#def getSeedList(self):
		#u"""get seed list from server 获取商店中植物列表"""
		#if not self.signed_in:
			#self.signin()

		#if self.signed_in:
			#r = self.opener.open('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
			#m = re.search('var g_verify = "(.+)";', r.read())
			#self.verify = m.group(1)

			#logging.debug(u"获取seedlist ... ")
			#req = urllib2.Request('http://www.kaixin001.com/house/garden/seedlist.php',
					#urllib.urlencode({'verify':self.verify})
				#)

			#r = self.opener.open(req)
			#fname=r'd:\steedlist.xml'
			#open(fname,'w').write(r.read())
			#tree = etree.parse(fname)
			##tree = etree.parse(r)

			#items=tree.xpath('seed/item')
			#for i in items:
				#try:
					#seedname=i.xpath('name')[0].text
					#seedid=i.xpath('seedid')[0].text
					#price=i.xpath('price')[0].text
					#logging.debug(u"seedname=%s,seedid=%s,price=%s",seedname,seedid,price)
				#except IndexError:
					#logging.error(u"===>解析seed item失败!!! \n%s",etree.tostring(i,encoding='gbk'))

		#return True

	def getGranaryInfo(self):
		u"""get seed/product info from granary 获取仓库中作物信息"""
		if not self.signed_in:
			self.signin()

		if self.signed_in:
			if not self.verify:
				r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
				m = re.search('var g_verify = "(.+)";', r[0])
				self.verify = m.group(1)
				logging.info(u"verify=%s",self.verify)

			logging.debug(u"获取仓库植物产品信息 ... ")
			r = self.getResponse('http://www.kaixin001.com/!house/!garden/mygranary.php',
				{'verify':self.verify})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!=u'succ':
				logging.debug(u"===> 获取仓库植物产品信息失败! (%s)\n%s",ret,etree.tostring(tree,encoding='gbk'))
				return False

			totalprice=tree.xpath('totalprice')[0].text
			logging.info(u"仓库中植物产品总价值 %s",totalprice)

			items=tree.xpath('fruit/item')
			for i in items:
				try:
					seedid=i.xpath('seedid')[0].text
					num=i.xpath('num')[0].text
					name=i.xpath('name')[0].text
					logging.debug(u"seedid=%s,name=%s,num=%s",seedid,name,num)
					self.getGardenFruitInfo(seedid)
				except IndexError:
					logging.error(u"===>解析植物产品信息失败!!! \n%s",etree.tostring(i,encoding='gbk'))



			logging.debug(u"获取仓库动物产品信息 ... ")
			r = self.getResponse('http://www.kaixin001.com/!house/!ranch/mygranary.php',
				{'verify':self.verify})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!=u'succ':
				logging.debug(u"===> 获取仓库动物产品信息失败! (%s)\n%s",ret,etree.tostring(tree,encoding='gbk'))
				return False

			totalprice=tree.xpath('totalprice')[0].text
			logging.info(u"仓库中动物产品总价值 %s",totalprice)

			items=tree.xpath('fruit/item')
			for i in items:
				try:
					aid=i.xpath('aid')[0].text
					num=i.xpath('num')[0].text
					name=i.xpath('name')[0].text
					typetext=i.xpath('type')[0].text # 0: 普通 1: 精品(精羊毛) 2: 成年
					logging.debug(u"aid=%s,name=%s,num=%s,type=%s",aid,name,num,typetext)
					self.getRanchFruitInfo(typetext,aid)
				except IndexError:
					logging.error(u"===>解析仓库动物产品信息失败!!! \n%s",etree.tostring(i,encoding='gbk'))

		return True


	def getGardenFruitInfo(self,seedid):
		u"""获取植物产品的具体信息"""
		if not self.signed_in:
			self.signin()

		if self.signed_in:
			if not self.verify:
				r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
				m = re.search('var g_verify = "(.+)";', r[0])
				self.verify = m.group(1)
				logging.info(u"verify=%s",self.verify)

			logging.debug(u"获取作物 %s 具体信息 ... ",seedid)
			r = self.getResponse('http://www.kaixin001.com/house/garden/myfruitinfo.php',
				{'verify':self.verify,'seedid':seedid,'word':''})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!=u'succ':
				logging.debug(u"===> 获取作物 %s 具体信息失败! (%s)\n%s",seedid,ret,etree.tostring(tree,encoding='gbk'))
				return False

			try:
				rank=tree.xpath('rank')[0].text
				name=tree.xpath('name')[0].text
				fruit_minprice=tree.xpath('fruit_minprice')[0].text
				fruit_maxprice=tree.xpath('fruit_maxprice')[0].text
				fruitnum=tree.xpath('fruitnum')[0].text
				selfnum=tree.xpath('selfnum')[0].text
				bpresent=tree.xpath('bpresent')[0].text
				fruitprice=tree.xpath('fruitprice')[0].text
				jtitle=tree.xpath('jtitle')[0].text
				if jtitle:
					lohas=tree.xpath('lohas')[0].text
					jprice=tree.xpath('jprice')[0].text
					jratio=tree.xpath('jratio')[0].text
					logging.debug(u"name=%s,fruitnum=%s,fruitprice=%s,jtitle=%s,lohas=%s,jprice=%s,jratio=%s",name,fruitnum,fruitprice,jtitle,lohas,jprice,jratio)
				else:
					logging.debug(u"name=%s,fruitnum=%s,fruitprice=%s",name,fruitnum,fruitprice)

				try:
					old=filter(lambda x:x[1]==seedid,self.seedlist)[0]
					if old:
						oldprice=old[0]
						if oldprice!=int(fruitprice):
							old[0]=int(fruitprice)
							logging.info(u"更新作物信息 [%d,%s,%s] 到 [%d,%s,%s].",oldprice,old[1],old[2],old[0],old[1],old[2])
				except IndexError:
					logging.info(u"添加未知作物 [%s,%s,%s]!",fruitprice,seedid,name)
					self.seedlist.append([int(fruitprice),seedid,name])
				except Exception,e:
					logging.error(u"===>更新作物信息失败!!! \n%s",e)
			except IndexError:
				logging.error(u"===>解析仓库信息失败!!! \n%s",etree.tostring(tree,encoding='gbk'))

		return True

	def saveCfg(self):
		u"""更新配置文件"""
		logging.info(u"更新配置文件")
		seedlist=copy.copy(self.seedlist)
		seedlist.sort(cmp=lambda x,y: cmp(int(x[1]),int(y[1])))
		seedlist=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(seedlist)
		seedlist=seedlist.replace(u',['.encode('utf8'),u',\n['.encode('utf8')) # 一个item占一行便于手工编辑
		self.cfg.set('account','seedlist',seedlist)

		antisteal=copy.copy(self.antisteal)
		antisteal.sort()
		antisteal=json.JSONEncoder(ensure_ascii=False,separators=(',', ':')).encode(antisteal)
		antisteal=antisteal.replace(u',"'.encode('utf8'),u',\n"'.encode('utf8')) # 一个item占一行便于手工编辑
		self.cfg.set('account','antisteal',antisteal)

		friends=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.friends)
		self.cfg.set('account','friends',friends)

		animallist=copy.copy(self.animallist)
		animallist=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(animallist)
		animallist=animallist.replace(u'],"'.encode('utf8'),u'],\n"'.encode('utf8')) # 一个item占一行便于手工编辑
		self.cfg.set('account','animallist',animallist)

		self.cfg.set('account','getgranaryinfo',unicode(self.bGetGranaryInfo))

		self.cfg.write(codecs.open(self.inifile,'w','utf-8-sig'))

	def getSleepTime(self,n):
		d,h,m,s=None,None,None,None
		if len(n)==3: # 小时 分 秒
			h,m,s=n[0],n[1],n[2]
		elif len(n)==4: # 天 小时 分 秒
			d,h,m,s=n[0],n[1],n[2],n[3]
		elif len(n)==2: # 分 秒
			m,s=n[0],n[1]
		else:
			logging.exception(u"!!!未知格式 %s",n)

		if d:
			d=int(''.join([i for i in d if i<unichr(127)]))
		else:
			d=0
		if h:
			h=int(''.join([i for i in h if i<unichr(127)]))
		else:
			h=0
		if m:
			m=int(''.join([i for i in m if i<unichr(127)]))
		else:
			m=0
		if s:
			s=int(''.join([i for i in s if i<unichr(127)]))
		else:
			s=0

		return d*3600*24+h*3600+m*60+s

	def task_ranch(self,i_fuid,i_skey,i_typetext,task_key):
		if task_key in self.tasklist:
			del self.tasklist[task_key]
		logging.info(u"任务 %s 检查 %s(%s) (%s,%s,%s)... ",task_key,self.friends[i_fuid],i_fuid,i_fuid,i_skey,i_typetext)
		r = self.getResponse('http://www.kaixin001.com/house/ranch/getconf.php',
			{'verify':self.verify,'fuid':i_fuid})
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!=u'succ':
			logging.error(u"===>%s 获取牧场信息失败!!! ret=%s (%s)",task_key,ret,etree.tostring(tree,encoding='gbk'))
			return

		p=re.compile(ur'剩余数量：(?P<left>\d+)')
		items=tree.xpath('product2/item')
#			logging.debug("total %d product2 items in this garden",len(items))
		for i in items:
			try:
				skey=i.xpath('skey')[0].text # skey
				if skey!=i_skey:
					continue
				fuidtext=i.xpath('uid')[0].text # fuid
				num=int(i.xpath('num')[0].text)
				stealnum=int(i.xpath('stealnum')[0].text)
				pname=i.xpath('pname')[0].text
				tips=i.xpath('tips')[0].text
				typetext=i.xpath('type')[0].text # type
				#oa=i.xpath('oa')[0].text

				m=re.search(p,tips)
				if m:
					left_from_tips=m.group('left')
					if tips.find(u'距下次可收获还有')!=-1:
						logging.info(u"%s %s 已偷过! (%s)",task_key,pname,tips)
						return
					n=re.search(ur'再过(\d+小时)?(\d+分)?(\d+秒)?好友可收获',tips)
					if n:
						logging.info(u"%s %s 在防偷期! (%s)",task_key,pname,tips)

						scd=self.getSleepTime(n.groups())
						if scd<60:
							#scd+=0.02
							logging.info(u"%s 等待 %.2f 秒 ...",task_key,scd)
							time.sleep(scd)
						else:
							logging.info(u"%s scd=%d !!! (%s)",task_key,scd,etree.tostring(i,encoding='gbk'))
							return
			except Exception,e:
				logging.error(u"%s 解析product2失败! (%s)",task_key,etree.tostring(i,encoding='gbk'))
				return

			#logging.debug(u"(可偷) %d/%d (%s--%d--%d--%s--%s)",num-stealnum,num,pname,num,stealnum,oa,tips)
			scd=0.1
			trycnt=5
			if skey in self.antisteal:
				scd=0.05
				#trycnt=10
			for i in range(trycnt):
				reslt=self.stealRanchProduct(fuidtext,skey,typetext,task_key)
				#if i>4: scd*=2
				if reslt==False:
					if i!=trycnt-1:
						logging.info(u"第 %d 次偷取失败, %.2f 秒后再次尝试偷取(%s,%s,%s)...",i+1,scd,fuidtext,skey,typetext)
					else:
						logging.info(u"第 %d 次偷取失败, 停止尝试",i+1)
						break
					time.sleep(scd)
				else:
					break

			return


		pproduct=re.compile(ur'预计产量：(\d+).+?距离可收获还有(\d+分)?(\d+秒)?')
		items=tree.xpath('animals/item')
		for i in items:
			try:
				bproduct=i.xpath('bproduct')[0].text
				if bproduct!='1':
					continue
				skey=i.xpath('skey')[0].text
				if skey!=i_skey:
					continue
				tips=i.xpath('tips')[0].text
				m=re.search(pproduct,tips)
				if m:
					scd=self.getSleepTime(m.groups()[1:])
					rawscd=(m.group(2)!=None and [m.group(2)] or [''])[0]+\
				    (m.group(3)!=None and [m.group(3)] or [''])[0]
					logging.info(u"%s %s 预计产量 %s 距离收获 %d(%s)",task_key,skey,m.group(1),scd,rawscd)

					if scd<60:
						#scd+=0.05
						logging.info(u"%s 等待 %.2f 秒 ...",task_key,scd)
						time.sleep(scd)
					else:
						logging.info(u"%s scd=%d !!! (%s)",task_key,scd,etree.tostring(i,encoding='gbk'))
						return

			except Exception,e:
				logging.exception(u"%s 解析animals失败! (%s)",task_key,etree.tostring(i,encoding='gbk'))
				return

			scd=0.1
			trycnt=5
			if skey in self.antisteal:
				scd=0.05
				trycnt=10
			for i in range(trycnt):
				reslt=self.stealRanchProduct(i_fuid,skey,i_typetext,task_key)
				if reslt==False:
					scd*=2
					if i!=trycnt-1:
						if i==trycnt-2:
							scd=50 # 60 50 succ
						logging.info(u"第 %d 次偷取失败, %.2f 秒后再次尝试偷取(%s,%s,%s)...",i+1,scd,i_fuid,skey,i_typetext)
					else:
						logging.info(u"第 %d 次偷取失败, 停止尝试.",i+1)
						break
					if i==trycnt-2:
						tmpr = self.getResponse('http://www.kaixin001.com/house/ranch/getconf.php',
								{'verify':self.verify,'fuid':i_fuid})
						tmptree = etree.fromstring(tmpr[0])
						tmpret=tmptree.xpath('ret')[0].text
						if tmpret!=u'succ':
							logging.error(u"===>%s (debug)重新获取牧场信息失败!!! ret=%s (%s)",task_key,tmpret,etree.tostring(tmptree,encoding='gbk'))
					time.sleep(scd)
				else:
					break

			return

		return

	def task_garden(self,i_farmnum,i_seedid,i_fuid,task_key):
		u"""地块	1,2, 3, 9,13
							4,5, 8,11,14
							6,7,10,12,15
		"""
		if task_key in self.tasklist:
			del self.tasklist[task_key]

		p=re.compile(ur'(?:已产|产量)?：(?P<all>\d+)<br />剩余：(?P<left>\d+)')

		logging.info(u"%s 检查 %s(%s) 地块 %s 的 %s(%s)  ... ",task_key,self.friends[i_fuid],i_fuid,i_farmnum,filter(lambda x: x[1]==i_seedid,self.seedlist)[0][2],i_seedid)
		r = self.getResponse('http://www.kaixin001.com/house/garden/getconf.php',
			{'verify':self.verify,'fuid':i_fuid})
		tree = etree.fromstring(r[0])

		items=tree.xpath('garden/item')
#			logging.debug("total %d farms in this garden",len(items))
		for i in items:
			farmnum=i.xpath('farmnum')[0].text
			if farmnum!=i_farmnum:
				continue

			try:
				name=i.xpath('name')[0].text
			except IndexError:
				logging.debug(u"%s 地块 %s is empty",task_key,farmnum)
				return

			try:
				crops=i.xpath('crops')[0].text
			except IndexError:
				logging.debug(u"%s 地块 %s is %s(摇钱树 or 枯死的植物)!",task_key,farmnum,name)
				return

			farm=i.xpath('farm')[0].text
			if farm.find(u'爱心地')!=-1:
				friendname=farm=i.xpath('friendname')[0].text
				logging.debug(u"%s 地块 %s is %s 的爱心地!",task_key,farmnum,friendname)
				return

			seedid=i.xpath('seedid')[0].text
			if seedid!=i_seedid:
				logging.exception(u"%s 与预期的seedid不符! (%s!=%s)",task_key,seedid,i_seedid)

			# 检查seedid是否是未知的
			if seedid not in [x[1] for x in self.seedlist]: # 未知
				self.seedlist.append([4321,seedid,name])
				logging.info(u"%s 发现未知作物:\n\t[4321,\"%s\",\"%s\"],\n",task_key,seedid,name)

			m=re.match(p,crops)
			if m:
				all=m.group('all')
				left=int(m.group('left'))
				if crops.find(u'已摘过')==-1 and crops.find(u'已枯死')==-1 and left>1:

					n=re.search(ur'再过(\d+小时)?(\d+分)?(\d+秒)?好友可摘',crops)
					if n:
						logging.info(u"%s (%s)%s 在防偷期! (%s)",task_key,seedid,name,crops)

						scd=self.getSleepTime(n.groups())
						if scd<60:
							scd+=0.1
							logging.info(u"%s 等待 %.1f 秒 ...",task_key,scd)
							time.sleep(scd)
						else:
							logging.exception(u"%s scd=%d !!!",task_key,scd)
							return

						#logging.info(u"(可偷) %d/%s (%s--%s--%s--%s)",left,all,farmnum,seedid,name,crops)
						rslt=self.stealOneCrop(farmnum,seedid,i_fuid,task_key)
			return

	def getRanchFruitInfo(self,i_type,i_id):
		u"""获取动物产品的具体信息"""
		if not self.signed_in:
			self.signin()

		if self.signed_in:
			if not self.verify:
				r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
				m = re.search('var g_verify = "(.+)";', r[0])
				self.verify = m.group(1)
				logging.info(u"verify=%s",self.verify)

			logging.debug(u"获取动物产品 %s 具体信息 ... ",i_id)
			r = self.getResponse('http://www.kaixin001.com/!house/!ranch/myfruitinfo.php',
				{'verify':self.verify,'type':i_type,'id':i_id})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!=u'succ':
				logging.debug(u"===> 获取动物产品 %s 具体信息失败! (%s)\n%s",i_id,ret,etree.tostring(tree,encoding='gbk'))
				return False

			try:
				num=tree.xpath('num')[0].text
				selfnum=tree.xpath('selfnum')[0].text
				furid0=tree.xpath('furid0')[0].text
				furid1=tree.xpath('furid1')[0].text
				furid2=tree.xpath('furid2')[0].text
				rank=tree.xpath('rank')[0].text
				name=tree.xpath('name')[0].text
				price=tree.xpath('price')[0].text
				bpresent=tree.xpath('bpresent')[0].text
				units=tree.xpath('units')[0].text
				yili=tree.xpath('yili')[0].text
				advanced=tree.xpath('advanced')[0].text # 1: 幼仔
				logging.debug(u"name=%s,num=%s,selfnum=%s,furid0,1,2=%s,%s,%s,rank=%s,price=%s,bpresent=%s,units=%s,yili=%s,advanced=%s",
				  name,num,selfnum,furid0,furid1,furid2,rank,price,bpresent,units,yili,advanced)

				try:
					k=filter(lambda x:self.animallist[x][0]==int(i_id),self.animallist.keys())[0]
					if k:
						pass
						#old_name=self.animallist[k][1]
						#if old_name!=name:
							#logging.info(u"更新动物产品信息 %s=[%s,%s] 到 %s=[%s,%s].",k,self.animallist[k][0],old_name,k,self.animallist[k][0],self.animallist[k][1])
							#self.animallist[k][1]=name
				except IndexError:
					try:
						k=filter(lambda x:self.animallist[x][1]==name,self.animallist.keys())[0]
						old=self.animallist[k][0]
						self.animallist[k][0]=int(i_id)
						logging.info(u"更新动物产品信息 key=%s [%d,%s] => [%d,%s]!",k,old,name,self.animallist[k][0],name)
					except IndexError:
						logging.info(u"未知动物产品 [%s,%s]!",i_id,name)
				except Exception,e:
					logging.error(u"===>更新动物产品信息失败!!! \n%s",e)
			except IndexError:
				logging.error(u"===>解析仓库动物产品信息失败!!! \n%s",etree.tostring(tree,encoding='gbk'))

		return True


	def stealHoney(self,fuid):
		u"""偷蜂蜜"""
		logging.info(u"<=== 从 %s(%s) 偷取蜂蜜 ...",self.friends[fuid],fuid)
		r = self.getResponse('http://www.kaixin001.com/!house/!garden/stealhoney.php',
			{'verify':self.verify,'fuid':fuid})
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!=u'succ':
			reason=tree.xpath('reason')[0].text
			logging.info(u"===> !!! 偷取失败! (%s,%s)",ret,reason)
			return False

		try:
			count=tree.xpath('count')[0].text
			logging.info(u"===> *** 成功偷取 %s(%s)的 %s 蜂蜜~ (%s)",self.friends[fuid],fuid,count,etree.tostring(tree,encoding='gbk'))
		except IndexError:
			logging.error(u"===> 解析结果失败!!! \n%s",etree.tostring(tree,encoding='gbk'))

		return True

	def getResponse(self,url,data=None):
		u"""获得请求url的响应"""
		res,rurl=None,None
		for i in range(3): # 尝试3次
			if i!=0:
				logging.info(u"第 %d 次尝试...",i+1)
			try:
				r = self.opener.open(
					urllib2.Request(url,urllib.urlencode(data) if data else None),
					timeout=30)
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

if __name__=='__main__':
	import logging
	from lxml import etree
	import re, time#, thread, webbrowser
	from pprint import pprint
	from cStringIO import StringIO
	from random import uniform, random
	import urllib, urllib2, cookielib, json
	import ConfigParser
	import codecs
	import os
	import copy
	from threading import Timer
	import datetime
	import socket
	import sys
	import shelve

	#i=Kaixin(ur'd:\kaixin.ini')
	#i.run()
	import cProfile,pstats
	cProfile.run('''Kaixin(ur'd:\kaixin.ini').run()''',ur'd:\kaixin-profile.txt')
	#p=pstats.Stats(ur'd:\kaixin-profile.txt')
	#p.sort_stats('time', 'cum').print_stats('kaixin')
