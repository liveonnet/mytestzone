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

def htmlentitydecode(s):
	"""http://snipplr.com/view/15261/python-decode-and-strip-html-entites-to-unicode/"""
	# First convert alpha entities (such as &eacute;)
	# (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
	def entity2char(m):
		entity = m.group(1)
		if entity in name2codepoint:
			return chr(name2codepoint[entity])
		return " "  # Unknown entity: We replace with a space.
	t = re.sub('&(%s);' % '|'.join(name2codepoint), entity2char, s)

	# Then convert numerical entities (such as &#233;)
	t = re.sub('&#(\d+);', lambda x: chr(int(x.group(1))), t)

	# Then convert hexa entities (such as &#x00E9;)
	return re.sub('&#x(\w+);', lambda x: chr(int(x.group(1),16)), t)

class Kaixin(object):
	def __init__(self,inifile='kaixin.ini'):
		imp.reload(sys)
		sys.setdefaultencoding('utf-8')
		self.curdir=os.path.abspath('.')

		self.inifile=inifile
		if not os.path.isabs(inifile):
			self.inifile=os.path.join(self.curdir,self.inifile)

		self.cfg=configparser.SafeConfigParser()
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
			logging.info("log file: %s",self.logfile)
		else: # 为空则认为是log不写入文件，只输出到stdout
			logging.basicConfig(level=logging.INFO,
				format='%(thread)d %(message)s')
			logging.info("=== log不写入文件.===")

		logging.info("\n\n%s\n%s start %s %s\n%s\n 脚本最后更新: %s",'='*75,'='*((75-8-len(sys.argv[0]))//2),sys.argv[0],'='*((75-8-len(sys.argv[0]))//2),'='*75,time.strftime('%Y%m%d %H:%M:%S',time.localtime(os.stat(sys.argv[0]).st_mtime)))
		logging.info("ini file: %s",self.inifile)

		self.email=self.cfg.get('account','email')
		self.pwd=self.cfg.get('account','pwd')
		self.cookiefile=self.cfg.get('account','cookiefile')
		logging.info("cookie file: %s",self.cookiefile)

		self.signed_in = False
		self.cj = http.cookiejar.LWPCookieJar()
		try:
			self.cj.revert(self.cookiefile)
		except:
			None
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
		urllib.request.install_opener(self.opener)
		self.opener.handle_open['http'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息

		seedlist=self.cfg.get('account','seedlist')
		self.seedlist=json.JSONDecoder().decode(seedlist)
		logging.info("已知作物数 %d",len(self.seedlist))
		#self.seedlist.sort(cmp=lambda x,y: cmp(x[0], y[0]),reverse=True)

		animallist=self.cfg.get('account','animallist')
		self.animallist=json.JSONDecoder().decode(animallist)
		logging.info("已知牧场产品数 %d",len(self.animallist))

		ignoreseeds=self.cfg.get('account','ignoreseeds')
		self.ignoreseeds=json.JSONDecoder().decode(ignoreseeds) # 忽略不处理的作物

		forcestealseeds=self.cfg.get('account','forcestealseeds')
		self.forcestealseeds=json.JSONDecoder().decode(forcestealseeds) # 强制偷取的作物(不考虑其价值)

		antisteal=self.cfg.get('account','antisteal')
		self.antisteal=json.JSONDecoder().decode(antisteal) # 有防偷期的动物
		#pprint(self.antisteal)

		self.internal=self.cfg.getint('account','internal') # 轮询间隔
		self.internal4cafeDoEvent=self.cfg.getint('account','internal4cafeDoEvent') # 餐厅时间轮询间隔
		logging.info("轮询间隔 %d",self.internal)
		self.bStealCrop=self.cfg.getboolean('account','StealCrop') # 偷农场作物
		self.bStealRanch=self.cfg.getboolean('account','StealRanch') # 偷牧场副产品
		self.bGetGranaryInfo=self.cfg.getboolean('account','GetGranaryInfo') # 获取仓库信息(据此更新seedlist的价格)
		self.bDoCafeEvent=self.cfg.getboolean('account','DoCafeEvent') # 查看餐厅事件
		self.bCheckCafe=self.cfg.getboolean('account','CheckCafe') # 做餐厅服务

		friends=self.cfg.get('account','friends')
		self.friends=json.JSONDecoder().decode(friends) # 好友列表
		logging.info("已知好友数 %d",len(self.friends))

		# 打印忽略作物
		s=StringIO()
		for i,j in [(x[1],x[2]) for x in self.seedlist if x[1] in self.ignoreseeds]:
			s.write("%s(%s) "%(j,i))
		logging.info("忽略作物: %s",s.getvalue())
		s.close()

		# 打印强制偷取的作物
		s=StringIO()
		for i,j in [(x[1],x[2]) for x in self.seedlist if x[1] in self.forcestealseeds]:
			s.write("%s(%s) "%(j,i))
		logging.info("强制偷取的作物: %s",s.getvalue())
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

		# 检查的地块
		self.FarmBlock2Check=['1','2','3','9','13','4','5','8','11','14']

		self.verify=''
		self.dish2cook='5' # 自动做的菜

		logging.info("%s 初始化完成.",self.__class__.__name__)

	def signin(self):
		"""登录"""
		r = self.getResponse('http://www.kaixin001.com/home/')
		if r[1] == 'http://www.kaixin001.com/?flag=1&url=%2Fhome%2F':
			logging.debug("需要登录!")
			params = {'email':self.email, 'password':self.pwd, 'remember':1,'invisible_mode':0,'url':'/home/'}
			r = self.getResponse('http://www.kaixin001.com/login/login.php',params)

			m=re.match(r'http://www.kaixin001.com/home/\?uid=(\d{7,}|)',r[1])
			if m:
				logging.debug("登录成功! uid=%s .",m.group(1))
				self.cj.save(self.cookiefile)
				self.signed_in = True
			else:
				logging.info("登录失败! %s",r[1])
				#logging.info("%s",r.read())

				for i in range(3):
					# 帐号被认为使用了外挂要输入验证码 下面提取验证码图片
					rcode='%.16f_%d'%(random(),time.time()*1000) # 保存生成的随机数，用于需要验证码的登录请求
					randimgurl='http://www.kaixin001.com/interface/regcreatepng.php?randnum='+ rcode + '&norect=1'
					import webbrowser
					webbrowser.open(randimgurl)
					#r=urllib2.urlopen(randimgurl)
					#with open(ur'd:\img.gif','wb') as f:
						#f.write(r.read())
					#r.close()

					#logging.info("image file is d:\\img.gif")
					input('(%d)input the code to d:\\img.txt: '%(i,))
					with open(r'd:\img.txt') as f:
						code=f.read()
						code.strip()
						logging.info("you input code: "+code)

					params = {'email':self.email, 'password':self.pwd,
						'remember':1,'invisible_mode':0,'url':'/home/',
						'rcode':rcode,'rpkey':'','diarykey':'',
						'code':code}
					req = urllib.request.Request(
						'http://www.kaixin001.com/login/login.php',
						urllib.parse.urlencode(params)
					)
					r = self.opener.open(req)
					logging.info("r.geturl()=%s",r.geturl())
					if re.match(r'http://www.kaixin001.com/home/',r.geturl()):
						logging.info("logging in ! %s",r.geturl())
						self.signed_in=True
						break
					else:
						logging.info("logging in failed!(code error?) %s\n%s",r.geturl(),r.read())
						r.close()

				if not self.signed_in:
					sys.exit(1)
		else:
			logging.debug("无需登录!")
			self.signed_in = True

	def getFriends4garden(self):
		"""获取可偷取花园作物的好友列表"""
		if not self.signed_in:
			self.signin()
		if self.signed_in:
			del self.friends4garden[:]
			r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
			m = re.search('var g_verify = "(.+)";', r[0].decode())
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

			data = json.loads(r[0].decode())
			#pprint(data)

			for f in data:
				#if f.get('harvest',None):
				if f.get('antiharvest',None):
					pass
					#logging.info(u"%s(%s) 有防偷!",f['real_name'],f['uid'])
				fname,fuid=f['real_name'],str(f['uid'])
				if (fname,fuid) not in self.friends4garden:
##					if f.get('harvest',None)==1:
					self.friends4garden.append((fname,fuid))
				if fuid not in self.friends:
					self.friends[fuid]=fname

			#logging.info(u"self.friends4garden=%s",self.friends4garden)
			#logging.info(u"self.friends=%s",self.friends)
			#raw_input()


	def checkGarden(self):
		"""地块		1,2, 3, 9,13
							4,5, 8,11,14
							6,7,10,12,15
		"""
		logging.info("共检查%d个好友的花园.",len(self.friends4garden))

		p=re.compile(r'(?:已产|产量)?：(?P<all>\d+)<br />剩余：(?P<left>\d+)')
		pgrow=re.compile(r'生长阶段：(\d+)%.+?距离收获：(\d+天)?(\d+小时)?(\d+分)?(\d+秒)?')

		cnt=0
		del self.crops2steal[:]
		for fname,fuid in self.friends4garden:
##		for fuid,fname in self.friends.items():
			cnt+=1
			logging.info(" %02d) 检查 %s(%s)... ",cnt,fname,fuid)
##			r = self.getResponse('http://www.kaixin001.com/house/garden/getconf.php',
##				{'verify':self.verify,'fuid':fuid})
			r = self.getResponse('http://www.kaixin001.com/!house/!garden//getconf.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'fuid':fuid,'r':"%.16f"%(random(),)}),),
				None)
			tree = etree.fromstring(r[0])

			items=tree.xpath('garden/item')
#			logging.debug("total %d farms in this garden",len(items))
			for i in items:
				farmnum=i.xpath('farmnum')[0].text
				if not farmnum in self.FarmBlock2Check:
					continue

				# -1=枯死 1=生长中 2=成熟 3=采光未犁地
				try:
					cropsstatus=i.xpath('cropsstatus')[0].text
				except IndexError:
##					logging.debug("地块 %s 为空",farmnum)
					continue

				if cropsstatus=='-1':
##					logging.debug("地块 %s 为枯死的作物",farmnum)
					continue
				if cropsstatus=='3':
##					logging.debug("地块 %s 已经收获光未犁地",farmnum)
					continue

##				logging.debug("地块 %s cropsstatus=%s",farmnum,cropsstatus)

				name=i.xpath('name')[0].text
				crops=i.xpath('crops')[0].text
				seedid=i.xpath('seedid')[0].text

				if seedid in self.ignoreseeds:
##					logging.debug("忽略地块 %s 的 %s(%s)",farmnum,name,seedid)
					continue

				if seedid=='102': # 是摇钱树
					if crops.find('点击可摇钱')!=-1: # 可摇钱
						yaoqianr=self.getResponse('http://www.kaixin001.com/!house/!garden/yaoqianshu.php',
							{'verify':self.verify,'fuid':fuid})
						yaoqiantree = etree.fromstring(yaoqianr[0])
						yaoqianret=yaoqiantree.xpath('ret')[0].text
						if yaoqianret!='succ':
							reason=yaoqiantree.xpath('reason')[0].text
							logging.info("===> !!! 摇钱失败! (%s,%s)",yaoqianret,reason)
						else:
							yaoqiantip=yaoqiantree.xpath('tip')[0].text
							logging.info("===> *** 摇钱成功 %s(%s) (%s)",fname,fuid,yaoqiantip)

				if seedid=='198': # 阳光果粒橙
					logging.info("阳光果粒橙! (%s)",crops)
					if crops.find('点击可摇奖')!=-1: # 可摇奖
						cropsid=i.xpath('cropsid')[0].text
						yaojiangr=self.getResponse('http://www.kaixin001.com/!house/!garden//guolicheng/yj.php',
							{'verify':self.verify,'fuid':fuid,'cropsid':cropsid})
						yaojiangtree=etree.fromstring(yaojiangr[0])
						yaojiangret=yaojiangtree.xpath('ret')[0].text
						if yaojiangret!='succ':
							reason=yaojiangtree.xpath('reason')[0].text
							logging.info("===> !!! 摇奖失败!(%s,%s)",yaojiangret,reason)
						else:
							reason=yaojiangtree.xpath('reason')[0].text
							logging.info("===> *** 摇奖完成!(%s,%s)",yaojiangret,reason)


				# 检查seedid是否是未知的
				if seedid not in [x[1] for x in self.seedlist]: # 未知
					self.seedlist.append([4321,seedid,name])
					logging.info("发现未知作物:\n\t[4321,\"%s\",\"%s\"],\n",seedid,name)

				m=re.match(p,crops)
				if m:
					all=m.group('all')
					left=int(m.group('left'))
					if crops.find('已摘过')==-1:

						n=re.search(r'再过(\d+小时)?(\d+分)?(\d+秒)?好友可摘',crops)
						if n:
							logging.info("地块 %s %s(%s) 在防偷期! (%s)",farmnum,name,seedid,crops)

							scd=self.getSleepTime(n.groups())
							if scd<self.internal+10: # 下次轮询前不需执行则不加入定时任务
								k='crop-%s-%s-%s'%(fuid,farmnum,seedid)
								if k not in self.tasklist: # 相同的任务不存在
									# 判断是否存在同一块地不同seedid的任务，如果存在则先删除
									samek='crop-%s-%s-'%(fuid,farmnum)
									for i in self.tasklist.keys():
										if i.startswith(samek):
											logging.info("终止并删除对同一块地的定时任务 key=%s",samek)
											self.tasklist[i].cancel()
											del self.tasklist[i]
								else:
									logging.info("更新前删除相同的定时任务")
									self.tasklist[k].cancel()
									del self.tasklist[k]

								logging.info("加入定时执行队列 key=%s %d (%s,%s,%s)",k,scd,farmnum,seedid,fuid)
								if scd<60:
									t=Timer(scd+0.1, self.stealOneCrop,(farmnum,seedid,fuid,k))
								else:
									t=Timer(scd, self.task_garden,(farmnum,seedid,fuid,k))
								t.start()
								self.tasklist[k]=t

						elif left>1:
							logging.info("(可偷) %d/%s (地块%s--%s(%s)--%s)",left,all,farmnum,name,seedid,crops)
							self.crops2steal.append((farmnum,seedid,fuid))
					else:
##						logging.debug(u"地块 %s %s(%s) 已摘过(%s)",farmnum,name,seedid,crops)
						pass
				else:
					pass
##					m=re.search(pgrow,crops)
##					if m:
##						precent=m.group(1)
##						scd=self.getSleepTime(m.groups()[1:])
##						rawscd=(m.group(2) and [m.group(2)] or [''])[0]\
##							+(m.group(3) and [m.group(3)] or [''])[0]\
##							+(m.group(4) and [m.group(4)] or [''])[0]\
##							+(m.group(5) and [m.group(5)] or [''])[0]
##						logging.debug("地块 %s %s(%s) 处于生长期 %s%% 距离收获 %s 秒(%s)",farmnum,name,seedid,precent,scd,rawscd)
##					else:
####						logging.debug("地块 %s %s(%s) 处于生长期 (%s)",farmnum,name,seedid,crops)
##						raise Exception("无法判断地块 %s %s(%s) 的收获时间(%s)",farmnum,name,seedid,crops)

			# 查看有没有蜂蜜可偷
			items=tree.xpath('account/yh_honey')
			if items:
				count=items[0].xpath('count')[0].text
				count_a=items[0].xpath('count_a')[0].text # 洋槐蜂蜜
				count_b=items[0].xpath('count_b')[0].text # 枸杞蜂蜜
				count_c=items[0].xpath('count_c')[0].text # 党参蜂蜜
				total=items[0].xpath('total')[0].text
				sumtext=items[0].xpath('sum')[0].text
##				logging.debug("洋槐蜂蜜 %s, 枸杞蜂蜜 %s, 党参蜂蜜 %s, count/total/sum=%s/%s/%s",
##					count_a,count_b,count_c,count,total,sumtext)

				items=tree.xpath('account/yh_stealinfo')
				if items:
					stealinfo=items[0].text
					if stealinfo.find('已摘过')!=-1:
						logging.info("蜂蜜 已摘过! (%s)",stealinfo)
				else:
					logging.info("(可偷) 洋槐蜂蜜 %s, 枸杞蜂蜜 %s, 党参蜂蜜 %s, count/total/sum=%s/%s/%s",
						count_a,count_b,count_c,count,total,sumtext)
					self.stealHoney(fuid)


	def stealCrop(self):
		"""依次尝试偷取值得偷的作物"""
		# 只偷贵的
		tosteal=self.getValueItems(1000)
		logging.info("根据作物价值偷%d个.",len(tosteal))
		if tosteal==0:
			return True

		# 将 crops2steal 打乱顺序
		s=StringIO()
		pprint(tosteal,s)
		logging.info("original\n%s",s.getvalue())
		s.close()
		tosteal=self.__class__.OutOfOrder(tosteal,1)
		t=StringIO()
		pprint(tosteal,t)
		logging.info("processed\n%s",t.getvalue())
		t.close()

		# 看是否有曼陀罗，如果有则放到最后偷
		foundStramonium=False
		seednamelist=[x[1] for x in self.seedlist if x[2].find("曼陀罗")!=-1] # 叫曼陀罗的植物的seedid列表
		toend=[] # 存放需要后移的曼陀罗
		for farmnum,seedid,fuid in tosteal:
			if seedid in seednamelist:
				foundStramonium=True
				logging.info("发现有曼陀罗 (%s,%s,%s)",farmnum,seedid,fuid)
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
				logging.debug("延迟%f秒以逃避反外挂检测...",sleeptime)
				time.sleep(sleeptime)

		return True

	def stealOneCrop(self,farmnum,seedid,fuid,taskkey=''):
		"""偷取单一作物"""
		tasklogstring=''
		if taskkey!='':
			tasklogstring='[任务 %s]'%(taskkey,)
			logging.info("执行定时任务 %s ...",taskkey)
			# 从tasklist中删除任务
			if taskkey in self.tasklist:
				del self.tasklist[taskkey]

		logging.debug("<=== %s 从 %s(%s) 偷取 %s(farmnum=%s) ... ",tasklogstring,self.friends[fuid],fuid,[x for x in self.seedlist if x[1]==seedid][0][2],farmnum)
##		r = self.getResponse('http://www.kaixin001.com/house/garden/havest.php',
##			{'verify':self.verify,'farmnum':farmnum,'seedid':seedid,'fuid':fuid})
		r = self.getResponse('http://www.kaixin001.com/!house/!garden//havest.php?%s'%
			(urllib.parse.urlencode(
			{'farmnum':farmnum,'seedid':seedid,'fuid':fuid,'r':"%.16f"%(random(),),'confirm':'0'}),),
			None)
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			reason=tree.xpath('reason')[0].text
			logging.info("===> %s !!! 偷取失败! (%s,%s)",tasklogstring,ret,reason)
			if reason.find('正在麻醉中')!=-1:
				logging.info("麻醉中，不能偷植物产品.")
				return False
			#return False
			return True

		anti=tree.xpath('anti')[0].text
		if anti=='1':
			logging.error("===> %s anti=1!!! 被反外挂检测到了 \n%s",tasklogstring,etree.tostring(tree,encoding='gbk').decode('gbk'))
##			print (chr(7)*5)
			return False

		try:
			leftnum=tree.xpath('leftnum')[0].text
			stealnum=tree.xpath('stealnum')[0].text
			num=tree.xpath('num')[0].text
			seedname=tree.xpath('seedname')[0].text
			logging.debug("%s anti=%s,leftnum=%s,stealnum=%s,num=%s,seedname=%s",tasklogstring,anti,leftnum,stealnum,num,seedname)
			logging.info("===> %s *** 成功偷取 %s(%s)的 %s %s",tasklogstring,self.friends[fuid],fuid,stealnum,seedname)
			self.statistics[seedname]=self.statistics.get(seedname,0)+int(stealnum)
		except IndexError:
			logging.error("===> %s 解析结果失败!!! \n%s",tasklogstring,etree.tostring(tree,encoding='gbk').decode('gbk'))

		return True

	def getFriends4ranch(self):
		"""获取可偷取牧场产品的好友列表"""
		if not self.signed_in:
			self.signin()
		if self.signed_in:
			del self.friends4ranch[:]
			r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=ranch/index.php')
			m = re.search('var g_verify = "(.+)";', r[0].decode())
			self.verify = m.group(1)
			#logging.info(u"verify=%s",self.verify)

			r = self.getResponse('http://www.kaixin001.com/!house/!ranch/friendlist.php')
			data = json.loads(r[0].decode())

			for f in data:
				#logging.debug(u"%s  %s",f['real_name'],f['uid'])
				fname,fuid=f['real_name'],str(f['uid'])
				if f.get('antiharvest',None):
					pass
					#logging.info(u"%s(%s) 有防偷!",fname,fuid)
##				if f.get('harvest',None)==1:
				self.friends4ranch.append((fname,fuid))
				if fuid not in self.friends:
					self.friends[fuid]=fname


	def checkRanch(self):
		logging.info("共检查%d个好友的牧场.",len(self.friends4ranch))
		p=re.compile(r'剩余数量：(?P<left>\d+)')

		cnt=0
		for fname,fuid in self.friends4ranch:
			cnt+=1
			logging.info(" %02d) 检查 %s(%s)... ",cnt,fname,fuid)
##			r = self.getResponse('http://www.kaixin001.com/house/ranch/getconf.php',
##				{'verify':self.verify,'fuid':fuid})
			r = self.getResponse('http://www.kaixin001.com/!house/!ranch//getconf.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'fuid':fuid,'r':"%.16f"%(random(),),
				'dragon_shake':'move'}),),
				None)
			tree = etree.fromstring(r[0])

			# 检查是否有在工作的狗狗
			try:
				dogs_name=tree.xpath('dogs_name')[0].text
				dogs_tips=tree.xpath('dogs_tips')[0].text
				if dogs_tips.find('距饥饿还有')!=-1:
					logging.info("跳过！%s 在工作中(%s)!",dogs_name,dogs_tips)
					continue
				elif dogs_tips.find('挨饿中')!=-1:
					logging.debug("%s 在挨饿中(%s).",dogs_name,dogs_tips)
				else:
					logging.info("%s 在未知状态(%s)!",dogs_name,dogs_tips)
			except IndexError:
				pass
##				logging.info("没有发现在工作的狗狗!")

			# 检查是否有在工作的巡查员
			try:
				policeurl=tree.xpath('policeurl')[0].text
				policeetime=tree.xpath('policeetime')[0].text
				if policeetime.find('距这位巡查员工作结束')!=-1:
					logging.info("跳过！巡查员 在工作中(%s)",policeetime)
					continue
				else:
					logging.info("巡查员在未知状态(%s)!",policeetime)
			except IndexError:
				pass
##				logging.info("没有发现在工作的巡查员")


			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.error("===>获取牧场信息失败!!! ret=%s (%s)",ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
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
						logging.info("添加未知牧场品种 %s(%s)",skey,pname)
						self.animallist[skey]=[int(typetext),pname]
					if self.animallist[skey][1]!=pname:
						logging.info("牧场品种名称不符 %s(now=%s,should=%s)",skey,self.animallist[skey][1],pname)


					m=re.search(p,tips)
					if m:
						left_from_tips=m.group('left')
						if tips.find('距下次可收获还有')!=-1:
							logging.debug("%s 已收获过! (%s)",pname,tips)
							continue
						n=re.search(r'再过(\d+小时)?(\d+分)?(\d+秒)?好友可收获',tips)
						if n:
							rawscd=(n.group(1) and [n.group(1)] or [''])[0]\
								+(n.group(2) and [n.group(2)] or [''])[0]\
								+(n.group(3) and [n.group(3)] or [''])[0]

							logging.info("%s 在防偷期, 再过 %s 可收获! (%s)",pname,rawscd,tips)

							scd=self.getSleepTime(n.groups())
							if scd<self.internal: # 下次轮询前不需要执行则不加入定时任务
								k='ranch-%s-%s-%s'%(fuidtext,skey,typetext)
								if k in self.tasklist: # 相同的任务已经存在
									logging.info("更新前删除相同任务")
									self.tasklist[k].cancel()
									del self.tasklist[k]
								logging.info("加入定时执行队列 key=%s %d (%s,%s,%s)",k,scd,fuidtext,skey,typetext)
								if scd<60:
									t=Timer(scd+0.15, self.stealRanchProduct,(fuidtext,skey,typetext,k))
								else:
									t=Timer(scd,self.task_ranch,(fuidtext,skey,typetext,k))
								t.start()
								self.tasklist[k]=t

							continue
				except Exception as e:
					logging.error("解析product2/item失败! (%s)(%s)",e,etree.tostring(i,encoding='gbk').decode('gbk'))

				logging.debug("(可偷) %d/%d (%s--%d--%d--%s)",num-stealnum,num,pname,num,stealnum,tips)
				reslt=self.stealRanchProduct(fuidtext,skey,typetext)

			pproduct=re.compile(r'预计产量：(\d+).+?距离可收获还有(\d+分)?(\d+秒)?')
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
							logging.info("添加未知牧场品种 %s(%s)",skey,aname)
						except Exception:
							logging.info("未知牧场品种 %s(%s)",skey,etree.tostring(i,encoding='gbk').decode('gbk'))
							continue # 因为不知道名字，所以不处理

					tips=i.xpath('tips')[0].text
					m=re.search(pproduct,tips)
					if m:
						scd=self.getSleepTime(m.groups()[1:])
						rawscd=(m.group(2)!=None and [m.group(2)] or [''])[0]+\
						  (m.group(3)!=None and [m.group(3)] or [''])[0]
						logging.info("%s 预计产量 %s 距离收获 %d(%s)",skey,m.group(1),scd,rawscd)

						if skey in self.antisteal:
							logging.info("%s 有防偷期，不追踪.",skey)
							continue

						if scd<self.internal:
							k='ranch-p-%s-%s-%s'%(fuid,skey,'0')
							if k in self.tasklist: # 相同的任务已经存在
								if getattr(self.tasklist[k],'sleeptime',0)<scd: # 已存在的相同任务的等待时间更长,则替换为等待时间短的
									logging.info("更新前删除相同任务")
									self.tasklist[k].cancel()
									del self.tasklist[k]
								else: # 已存在的相同任务的等待时间已经是最长的，不必更新
									logging.info("相同任务已经存在%s(%d>=%d)，略过",k,getattr(self.tasklist[k],'sleeptime',0),scd)
									continue # 不更新
							logging.info("加入定时执行队列 key=%s %d (%s,%s,%s)",k,scd,fuid,skey,'0')
							if scd<60:
								t=Timer(scd+0.15, self.stealRanchProduct,(fuid,skey,'0',k))
								t.sleeptime=scd
							else:
								t=Timer(scd,self.task_ranch,(fuid,skey,'0',k))
								t.sleeptime=scd
							t.start()
							self.tasklist[k]=t

				except Exception as e:
					logging.info("解析animals/item失败! (%s)",etree.tostring(i,encoding='gbk').decode('gbk'))

	def stealRanchProduct(self,fuid,skey,typetext,taskkey=''):
		"""steal one item 偷取一个牧场产品"""
		tasklogstring=''
		if taskkey!='':
			tasklogstring='%s'%(taskkey,)
			#logging.info(u"%s (%s,%s,%s)...",tasklogstring,fuid,skey,typetext)
			# 从tasklist中删除任务
			if taskkey in self.tasklist:
				del self.tasklist[taskkey]


		logging.debug("<=== %s (%s,%s,%s) 偷取 %s(%s) 的 %s ... ",tasklogstring,fuid,skey,typetext,self.friends[fuid],fuid,self.animallist[skey][1])
		r = self.getResponse('http://www.kaixin001.com/!house/!ranch/havest.php',
			{'verify':self.verify,'fuid':fuid,'skey':skey,'seedid':'0','id':'0','type':typetext,'foodnum':'1'})
		if not r[0]:
			return False
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			reason=tree.xpath('reason')[0].text
			logging.info("===> %s !!! 偷取 %s(%s) 的 %s 失败! (%s,%s)",tasklogstring,self.friends[fuid],fuid,self.animallist[skey][1],ret,reason)
			return False

		try:
			res_ptype=tree.xpath('ptype')[0].text
			res_action=tree.xpath('action')[0].text
			res_num=tree.xpath('num')[0].text
			res_skey=tree.xpath('skey')[0].text
			logging.debug("%s action=%s,num=%s,skey=%s,ptype=%s",tasklogstring,res_action,res_num,res_skey,res_ptype)
			logging.info("===> %s *** 成功偷取 %s %s~",tasklogstring,res_num,self.animallist[res_skey][1])
			self.statistics[self.animallist[res_skey][1]]=self.statistics.get(self.animallist[res_skey][1],0)+int(res_num)
		except IndexError:
			logging.error("===> %s 解析结果失败!!! \n%s",tasklogstring,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return False

		return True

	def run(self):
		try:
##			self.cafe_getDishlist()

			if self.bDoCafeEvent:
				self.cafe_doEvent()

			while True:
				if self.bCheckCafe:
					self.cafe_checkStatus()

				if self.bGetGranaryInfo:
					self.getGranaryInfo()
					#self.saveCfg()
					self.bGetGranaryInfo=False
					logging.info("重新设置 getgranaryinfo=False")
					break

				if self.bStealCrop:
					self.getFriends4garden()
					self.checkGarden()
					self.stealCrop()

				if self.bStealRanch:
					self.getFriends4ranch()
					self.checkRanch()


				logging.info("\n%s\n%s %d 秒后再次执行(%s) ...  %s\n%s\n",'='*75,'='*15,self.internal,
					(datetime.datetime.now()+datetime.timedelta(seconds=self.internal)).strftime("%Y-%m-%d %H:%M:%S"),
					'='*15,'='*75)
				time.sleep(self.internal)
		except KeyboardInterrupt:
			logging.info("用户中断执行.")

		self.saveCfg()
		for k,v in self.tasklist.items():
			logging.info("删除定时任务 %s",k)
			v.cancel()
		self.tasklist.clear()

		if len(self.statistics)!=0:
			stat=StringIO()
			for k,v in self.statistics.items():
				stat.write("%s: %d\t"%(k,v))
			logging.info("统计: %s",stat.getvalue())
			stat.close()
			self.statistics.close()

		logging.info("执行完毕.")
		time.sleep(1)

	@staticmethod
	def OutOfOrder(l,n=4):
		"""返回一个乱序后的list。返回的list是将list中item的顺序打乱以尽量保证列表中
		不出现连续n个item都是一个好友的情况
		"""
		def pickone(cur,sorted_key):
			"""根据情况选择出排在cur之后的k，返回k对应的value(是个列表)中的一个值"""
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
		sorted_key= sorted([(len(tmp[k]),k) for k in tmp.keys()],reverse=True)
	#	pprint(sorted_key)

		try:
			puzzled_list=[]
			while len(tmp)!=0:
				cur=max([(len(tmp[k]),k) for k in tmp.keys()])[1] # 找出当前可偷作物最多的好友的id
				while n<len(tmp[cur]):
					puzzled_list+=tmp[cur][:n]
					tmp[cur]=tmp[cur][n:]
					x=pickone(cur,sorted_key) # 每隔n个就插入第二多的k中的一个value
					if x:
						puzzled_list+=[x]

				puzzled_list+=tmp[cur]
				del tmp[cur]

			assert len(l)==len(puzzled_list)
		except Exception as e:
			logging.error("异常 (%s) ",e)
			pprint(l,console)

		return puzzled_list

	def getValueItems(self,threshold_value):
		"""从l挑出价值大于 threshold_value 或者是强制偷取的 的 item 以列表形式返回"""
		ret=[]
		# 从seedlist中选出价值不低于threshold的seedid的列表
		threshold_list=[i[1] for i in self.seedlist if i[0]>=threshold_value]
		# 将强制要偷的seedid加入
		for i in self.forcestealseeds:
			if i not in threshold_list:
				threshold_list.append(i)

		# 从上一步结果中选出包含在可偷列表中的seed
		threshold_list=[x for x in threshold_list if x in [i[1] for i in self.crops2steal]]

		for i in threshold_list:
			t=[item for item in self.crops2steal if item[1]==i]
			ret+=t
		return ret

	def getGranaryInfo(self):
		"""get seed/product info from granary 获取仓库中作物信息"""
		if not self.signed_in:
			self.signin()

		if self.signed_in:
			if not self.verify:
				r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
				m = re.search('var g_verify = "(.+)";', r[0].decode())
				self.verify = m.group(1)
				logging.info("verify=%s",self.verify)

			logging.debug("获取仓库植物产品信息 ... ")
			r = self.getResponse('http://www.kaixin001.com/!house/!garden/mygranary.php',
				{'verify':self.verify})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.debug("===> 获取仓库植物产品信息失败! (%s)\n%s",ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				return False

			totalprice=tree.xpath('totalprice')[0].text
			logging.info("仓库中植物产品总价值 %s",totalprice)

			items=tree.xpath('fruit/item')
			for i in items:
				try:
					seedid=i.xpath('seedid')[0].text
					num=i.xpath('num')[0].text
					name=i.xpath('name')[0].text
					logging.debug("seedid=%s,name=%s,num=%s",seedid,name,num)
					self.getGardenFruitInfo(seedid)
				except IndexError:
					logging.error("===>解析植物产品信息失败!!! \n%s",etree.tostring(i,encoding='gbk').decode('gbk'))



			logging.debug("获取仓库动物产品信息 ... ")
			r = self.getResponse('http://www.kaixin001.com/!house/!ranch/mygranary.php',
				{'verify':self.verify})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.debug("===> 获取仓库动物产品信息失败! (%s)\n%s",ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				return False

			totalprice=tree.xpath('totalprice')[0].text
			logging.info("仓库中动物产品总价值 %s",totalprice)

			items=tree.xpath('fruit/item')
			for i in items:
				try:
					aid=i.xpath('aid')[0].text
					num=i.xpath('num')[0].text
					name=i.xpath('name')[0].text
					typetext=i.xpath('type')[0].text # 0: 普通 1: 精品(精羊毛) 2: 成年
					logging.debug("aid=%s,name=%s,num=%s,type=%s",aid,name,num,typetext)
					self.getRanchFruitInfo(typetext,aid)
				except IndexError:
					logging.error("===>解析仓库动物产品信息失败!!! \n%s",etree.tostring(i,encoding='gbk').decode('gbk'))

		return True


	def getGardenFruitInfo(self,seedid):
		"""获取植物产品的具体信息"""
		if not self.signed_in:
			self.signin()

		if self.signed_in:
			if not self.verify:
				r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
				m = re.search('var g_verify = "(.+)";', r[0])
				self.verify = m.group(1)
				logging.info("verify=%s",self.verify)

			logging.debug("获取作物 %s 具体信息 ... ",seedid)
			r = self.getResponse('http://www.kaixin001.com/house/garden/myfruitinfo.php',
				{'verify':self.verify,'seedid':seedid,'word':''})
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.debug("===> 获取作物 %s 具体信息失败! (%s)\n%s",seedid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
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
					logging.debug("name=%s,fruitnum=%s,fruitprice=%s,jtitle=%s,lohas=%s,jprice=%s,jratio=%s",name,fruitnum,fruitprice,jtitle,lohas,jprice,jratio)
				else:
					logging.debug("name=%s,fruitnum=%s,fruitprice=%s",name,fruitnum,fruitprice)

				try:
					old=[x for x in self.seedlist if x[1]==seedid][0]
					if old:
						oldprice=old[0]
						if oldprice!=int(fruitprice):
							old[0]=int(fruitprice)
							logging.info("更新作物信息 [%d,%s,%s] 到 [%d,%s,%s].",oldprice,old[1],old[2],old[0],old[1],old[2])
				except IndexError:
					logging.info("添加未知作物 [%s,%s,%s]!",fruitprice,seedid,name)
					self.seedlist.append([int(fruitprice),seedid,name])
				except Exception as e:
					logging.error("===>更新作物信息失败!!! \n%s",e)
			except IndexError:
				logging.error("===>解析仓库信息失败!!! \n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

		return True

	def saveCfg(self):
		"""更新配置文件"""
		logging.info("更新配置文件")
		seedlist=copy.copy(self.seedlist)
		seedlist.sort(key=lambda x:int(x[1]))
		seedlist=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(seedlist)
		seedlist=seedlist.replace(',[',',\n[') # 一个item占一行便于手工编辑
		self.cfg.set('account','seedlist',seedlist)

		antisteal=copy.copy(self.antisteal)
		antisteal.sort()
		antisteal=json.JSONEncoder(ensure_ascii=False,separators=(',', ':')).encode(antisteal)
		antisteal=antisteal.replace(',"',',\n"') # 一个item占一行便于手工编辑
		self.cfg.set('account','antisteal',antisteal)

		friends=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.friends)
		self.cfg.set('account','friends',friends)

		animallist=copy.copy(self.animallist)
		animallist=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(animallist)
		animallist=animallist.replace('],"','],\n"') # 一个item占一行便于手工编辑
		self.cfg.set('account','animallist',animallist)

		self.cfg.set('account','getgranaryinfo',str(self.bGetGranaryInfo))

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
			logging.exception("!!!未知格式 %s",n)

		if d:
			d=int(''.join([i for i in d if i<chr(127)]))
		else:
			d=0
		if h:
			h=int(''.join([i for i in h if i<chr(127)]))
		else:
			h=0
		if m:
			m=int(''.join([i for i in m if i<chr(127)]))
		else:
			m=0
		if s:
			s=int(''.join([i for i in s if i<chr(127)]))
		else:
			s=0

		return d*3600*24+h*3600+m*60+s

	def task_ranch(self,i_fuid,i_skey,i_typetext,task_key):
		if task_key in self.tasklist:
			del self.tasklist[task_key]
		logging.info("任务 %s 检查 %s(%s) (%s,%s,%s)... ",task_key,self.friends[i_fuid],i_fuid,i_fuid,i_skey,i_typetext)
##		r = self.getResponse('http://www.kaixin001.com/house/ranch/getconf.php',
##			{'verify':self.verify,'fuid':i_fuid})
		r = self.getResponse('http://www.kaixin001.com/!house/!ranch//getconf.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'fuid':i_fuid,'r':"%.16f"%(random(),),
				'dragon_shake':'move'}),),
				None)
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			logging.error("===>%s 获取牧场信息失败!!! ret=%s (%s)",task_key,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return

		p=re.compile(r'剩余数量：(?P<left>\d+)')
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
					if tips.find('距下次可收获还有')!=-1:
						logging.info("%s %s 已偷过! (%s)",task_key,pname,tips)
						return
					n=re.search(r'再过(\d+小时)?(\d+分)?(\d+秒)?好友可收获',tips)
					if n:
						logging.info("%s %s 在防偷期! (%s)",task_key,pname,tips)

						scd=self.getSleepTime(n.groups())
						if scd<60:
							#scd+=0.02
							logging.info("%s 等待 %.2f 秒 ...",task_key,scd)
							time.sleep(scd)
						else:
							logging.info("%s scd=%d !!! (%s)",task_key,scd,etree.tostring(i,encoding='gbk').decode('gbk'))
							return
			except Exception as e:
				logging.error("%s 解析product2失败! (%s)",task_key,etree.tostring(i,encoding='gbk').decode('gbk'))
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
						logging.info("第 %d 次偷取失败, %.2f 秒后再次尝试偷取(%s,%s,%s)...",i+1,scd,fuidtext,skey,typetext)
					else:
						logging.info("第 %d 次偷取失败, 停止尝试",i+1)
						break
					time.sleep(scd)
				else:
					break

			return


		pproduct=re.compile(r'预计产量：(\d+).+?距离可收获还有(\d+分)?(\d+秒)?')
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
					logging.info("%s %s 预计产量 %s 距离收获 %d(%s)",task_key,skey,m.group(1),scd,rawscd)

					if scd<60:
						#scd+=0.05
						logging.info("%s 等待 %.2f 秒 ...",task_key,scd)
						time.sleep(scd)
					else:
						logging.info("%s scd=%d !!! (%s)",task_key,scd,etree.tostring(i,encoding='gbk').decode('gbk'))
						return

			except Exception as e:
				logging.exception("%s 解析animals失败! (%s)",task_key,etree.tostring(i,encoding='gbk').decode('gbk'))
				return

			scd=0.1
			trycnt=5
			if skey in self.antisteal:
				scd=0.05
				trycnt=10
			for i in range(trycnt):
				if i==trycnt-1:
##					tmpr = self.getResponse('http://www.kaixin001.com/!house/!ranch//getconf.php',
##				      {'verify':self.verify,'fuid':i_fuid})
					tmpr = self.getResponse('http://www.kaixin001.com/!house/!ranch//getconf.php?%s'%
						(urllib.parse.urlencode(
						{'verify':self.verify,'fuid':i_fuid,'r':"%.16f"%(random(),),
						'dragon_shake':'move'}),),
						None)
					tmptree = etree.fromstring(tmpr[0])
					tmpret=tmptree.xpath('ret')[0].text
					if tmpret!='succ':
						logging.error("===>%s (debug)重新获取牧场信息失败!!! ret=%s (%s)",task_key,tmpret,etree.tostring(tmptree,encoding='gbk').decode('gbk'))
					else:
						logging.info("重新获取牧场信息成功.")

				reslt=self.stealRanchProduct(i_fuid,skey,i_typetext,task_key)
				if reslt==False:
					scd*=2
					if i!=trycnt-1:
						if i==trycnt-2:
							scd=60 # 60 50 succ
						logging.info("第 %d 次偷取失败, %.2f 秒后再次尝试偷取(%s,%s,%s)...",i+1,scd,i_fuid,skey,i_typetext)
					else:
						logging.info("第 %d 次偷取失败, 停止尝试.",i+1)
						break
					time.sleep(scd)
				else:
					break

			return

		return

	def task_garden(self,i_farmnum,i_seedid,i_fuid,task_key):
		"""地块	1,2, 3, 9,13
							4,5, 8,11,14
							6,7,10,12,15
		"""
		if task_key in self.tasklist:
			del self.tasklist[task_key]

		p=re.compile(r'(?:已产|产量)?：(?P<all>\d+)<br />剩余：(?P<left>\d+)')

		logging.info("%s 检查 %s(%s) 地块 %s 的 %s(%s)  ... ",task_key,self.friends[i_fuid],i_fuid,i_farmnum,list(filter(lambda x: x[1]==i_seedid,self.seedlist))[0][2],i_seedid)
##		r = self.getResponse('http://www.kaixin001.com/house/garden/getconf.php',
##			{'verify':self.verify,'fuid':i_fuid})
		r = self.getResponse('http://www.kaixin001.com/!house/!garden//getconf.php?%s'%
			(urllib.parse.urlencode(
			{'verify':self.verify,'fuid':i_fuid,'r':"%.16f"%(random(),)}),),
			None)
		tree = etree.fromstring(r[0])

		items=tree.xpath('garden/item')
#			logging.debug("total %d farms in this garden",len(items))
		for i in items:
			farmnum=i.xpath('farmnum')[0].text
			if farmnum!=i_farmnum:
				continue

			# -1=枯死 1=生长中 2=成熟 3=采光未犁地
			try:
				cropsstatus=i.xpath('cropsstatus')[0].text
			except IndexError:
##				logging.debug("地块 %s 为空",farmnum)
				continue

##			if cropsstatus=='-1':
##				logging.debug("地块 %s 为枯死的作物",farmnum)
##				continue
			if cropsstatus=='3':
##				logging.debug("地块 %s 已经收获光未犁地",farmnum)
				continue

			logging.info("地块 %s cropsstatus=%s",farmnum,cropsstatus)

			name=i.xpath('name')[0].text
			crops=i.xpath('crops')[0].text
			seedid=i.xpath('seedid')[0].text
			if seedid!=i_seedid:
				logging.exception("%s 与预期的seedid不符! (%s!=%s)",task_key,seedid,i_seedid)

			# 检查seedid是否是未知的
			if seedid not in [x[1] for x in self.seedlist]: # 未知
				self.seedlist.append([4321,seedid,name])
				logging.info("%s 发现未知作物:\n\t[4321,\"%s\",\"%s\"],\n",task_key,seedid,name)

			m=re.match(p,crops)
			if m:
				all=m.group('all')
				left=int(m.group('left'))
				if crops.find('已摘过')==-1 and crops.find('已枯死')==-1 and left>1:

					n=re.search(r'再过(\d+小时)?(\d+分)?(\d+秒)?好友可摘',crops)
					if n:
						logging.info("%s (%s)%s 在防偷期! (%s)",task_key,seedid,name,crops)

						scd=self.getSleepTime(n.groups())
						if scd<60:
							scd+=0.1
							logging.info("%s 等待 %.1f 秒 ...",task_key,scd)
							time.sleep(scd)
						else:
							logging.exception("%s scd=%d !!!",task_key,scd)
							return

						#logging.info(u"(可偷) %d/%s (%s--%s--%s--%s)",left,all,farmnum,seedid,name,crops)
						rslt=self.stealOneCrop(farmnum,seedid,i_fuid,task_key)
			return

	def getRanchFruitInfo(self,i_type,i_id):
		"""获取动物产品的具体信息"""
		if not self.signed_in:
			self.signin()

		if self.signed_in:
			if not self.verify:
				r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=ranch/index.php')
				m = re.search('var g_verify = "(.+)";', r[0].decode('utf8'))
				self.verify = m.group(1)
				logging.info("verify=%s",self.verify)

			logging.debug("获取动物产品 %s 具体信息 ... ",i_id)
			r = self.getResponse('http://www.kaixin001.com/!house/!ranch/myfruitinfo.php',
				{'verify':self.verify,'type':i_type,'id':i_id})
			logging.debug("%s %s myfruitinfo:%s",i_type,i_id,r[0].decode('utf8'))
			time.sleep(1)
			tree = etree.fromstring(r[0])

			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.debug("===> 获取动物产品 %s 具体信息失败! (%s)\n%s",i_id,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
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
				logging.debug("name=%s,num=%s,selfnum=%s,furid0,1,2=%s,%s,%s,rank=%s,price=%s,bpresent=%s,units=%s,yili=%s,advanced=%s",
				  name,num,selfnum,furid0,furid1,furid2,rank,price,bpresent,units,yili,advanced)

				try:
					k=[x for x in self.animallist.keys() if self.animallist[x][0]==int(i_id)][0]
					if k:
						pass
						#old_name=self.animallist[k][1]
						#if old_name!=name:
							#logging.info(u"更新动物产品信息 %s=[%s,%s] 到 %s=[%s,%s].",k,self.animallist[k][0],old_name,k,self.animallist[k][0],self.animallist[k][1])
							#self.animallist[k][1]=name
				except IndexError:
					try:
						k=[x for x in self.animallist.keys() if self.animallist[x][1]==name][0]
						old=self.animallist[k][0]
						self.animallist[k][0]=int(i_id)
						logging.info("更新动物产品信息 key=%s [%d,%s] => [%d,%s]!",k,old,name,self.animallist[k][0],name)
					except IndexError:
						logging.info("未知动物产品 [%s,%s]!",i_id,name)
				except Exception as e:
					logging.error("===>更新动物产品信息失败!!! \n%s",e)
			except IndexError:
				logging.error("===>解析仓库动物产品信息失败!!! \n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

		return True


	def stealHoney(self,fuid):
		"""偷蜂蜜"""
		logging.info("<=== 从 %s(%s) 偷取蜂蜜 ...",self.friends[fuid],fuid)
		r = self.getResponse('http://www.kaixin001.com/!house/!garden/stealhoney.php',
			{'verify':self.verify,'fuid':fuid})
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			reason=tree.xpath('reason')[0].text
			logging.info("===> !!! 偷取失败! (%s,%s)",ret,reason)
			return False

		try:
			count=tree.xpath('count')[0].text
			logging.info("===> *** 成功偷取 %s(%s)的 %s 蜂蜜~ (%s)",self.friends[fuid],fuid,count,etree.tostring(tree,encoding='gbk').decode('gbk'))
		except IndexError:
			logging.error("===> 解析结果失败!!! \n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

		return True

	def getResponse(self,url,data=None):
		"""获得请求url的响应"""
		res,rurl=None,None
		for i in range(3): # 尝试3次
			if i!=0:
				logging.info("第 %d 次尝试...",i+1)
			try:
				r = self.opener.open(
					urllib.request.Request(url,urllib.parse.urlencode(data) if data else None),
					timeout=30)
				res=r.read()
				rurl=r.geturl()
				break
			except urllib.error.HTTPError as e:
				logging.exception("请求出错！ %s",e)
			except urllib.error.URLError as e:
				logging.exception("访问地址失败! %s",e)
			except IOError as e:
				logging.info("IO错误! %s",e)
			except Exception as e:
				logging.info("未知错误! %s",e)
				raise

		return (res,rurl)

	def yaoqian(self):
		"""地块		1,2, 3, 9,13
							4,5, 8,11,14
							6,7,10,12,15
		"""
		if not self.signed_in:
			self.signin()
		if self.signed_in:
			del self.friends4garden[:]
			r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=garden/index.php')
			m = re.search('var g_verify = "(.+)";', r[0].decode())
			self.verify = m.group(1)
		else:
			return False
		logging.info("共检查%d个好友的花园有没有摇钱树.",len(self.friends))

		cnt=0
		for fuid, fname in self.friends.items():
			cnt+=1
			logging.info(" %02d) 检查 %s(%s)... ",cnt,fname,fuid)
##			r = self.getResponse('http://www.kaixin001.com/house/garden/getconf.php',
##				{'verify':self.verify,'fuid':fuid})
			r = self.getResponse('http://www.kaixin001.com/!house/!garden//getconf.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'fuid':fuid,'r':"%.16f"%(random(),)}),),
				None)
			tree = etree.fromstring(r[0])

			items=tree.xpath('garden/item')
#			logging.debug("total %d farms in this garden",len(items))
			for i in items:
				farmnum=i.xpath('farmnum')[0].text

				# -1=枯死 1=生长中 2=成熟 3=采光未犁地
				try:
					cropsstatus=i.xpath('cropsstatus')[0].text
				except IndexError:
##					logging.debug("地块 %s 为空",farmnum)
					continue

				if cropsstatus=='-1':
##					logging.debug("地块 %s 为枯死的作物",farmnum)
					continue
				if cropsstatus=='3':
##					logging.debug("地块 %s 已经收获光未犁地",farmnum)
					continue

##				logging.debug("地块 %s cropsstatus=%s",farmnum,cropsstatus)

##				name=i.xpath('name')[0].text
				crops=i.xpath('crops')[0].text
				seedid=i.xpath('seedid')[0].text

				if seedid=='198': # 阳光果粒橙
					logging.info("阳光果粒橙! (%s)",crops)
##				if seedid=='102': # 是摇钱树
##					logging.info("有摇钱树!")
##					if crops.find('点击可摇钱')!=-1: # 可摇钱
##						r=self.getResponse('http://www.kaixin001.com/!house/!garden/yaoqianshu.php',
##							{'verify':self.verify,'fuid':fuid})
##						tree = etree.fromstring(r[0])
##						ret=tree.xpath('ret')[0].text
##						if ret!='succ':
##							reason=tree.xpath('reason')[0].text
##							logging.info("===> !!! 摇钱失败! (%s,%s)",ret,reason)
##						else:
##							tip=tree.xpath('tip')[0].text
##							logging.info("===> *** 摇钱成功 %s(%s) (%s)",fname,fuid,tip)
##
		return True


	def getFishinfo(self):
		if not self.signed_in:
			self.signin()

		if self.signed_in:
			if not self.verify:
				r = self.getResponse('http://www.kaixin001.com/!fish/index.php?t=62')
				m = re.search('var g_verify = "(.+)";', r[0].decode())
				self.verify = m.group(1)
				logging.info("verify=%s",self.verify)
		else:
			logging.info("未登录!")
			return

		r=self.getResponse('http://www.kaixin001.com/!fish/!fishlist.php',
			{'verify':self.verify})
		tree=etree.fromstring(r[0])
		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			reason=tree.xpath('reason')[0].text
			logging.info("获取鱼苗店信息失败! (%s,%s)",ret,reason)
			return
		fishs=tree.xpath('fish/item')
		for item in fishs:
			fid=item.xpath('fid')[0].text
			name=item.xpath('name')[0].text
			price=item.xpath('price')[0].text
			mprice=item.xpath('mprice')[0].text # 价格需要×10
			maxweight=item.xpath('maxweight')[0].text # 重量需要%10
##			logging.info("%s(%s) 买价 %.1f 卖价 %.1f 最大 %.1f 斤",name,fid,float(price)*10,float(mprice)*10,float(maxweight)/10)
			if float(mprice)*10>5000:
				logging.info("%s(%s) 买价 %.1f 卖价 %.1f 最大 %.1f 斤",name,fid,float(price)*10,float(mprice)*10,float(maxweight)/10)

	def cafe_doEvent(self):
		task_key= 'cafe-doevent'
		if task_key in self.tasklist:
			del self.tasklist[task_key]

		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False

		logging.info("%s 查看餐厅是否需要帮助...",task_key)
		r=self.getResponse('http://www.kaixin001.com/!cafe/index.php')
		m = re.search('verify=(.+?)&', r[0].decode())
##		logging.info("verify=%s",m.group(1))
		self.verify = m.group(1)

		r = self.getResponse('http://www.kaixin001.com/cafe/api_friendlist.php?%s'%
			(urllib.parse.urlencode(
			{'verify':self.verify,'rand':"%.16f"%(random(),)}),),
			None)
		tree = etree.fromstring(r[0])

		items=tree.xpath('item')
		logging.info("%s items=%d",task_key,len(items))
		for item in items:
			fname=item.xpath('real_name')[0].text
			fuid=item.xpath('uid')[0].text
			try:
				needhelp=item.xpath('help')[0].text
			except IndexError:
				continue

			if needhelp=='1':
				logging.info("%s 发现 %s(%s) 需要帮助...",task_key,fname,fuid)
				r = self.getResponse('http://www.kaixin001.com/cafe/api_userevent.php?%s'%
					(urllib.parse.urlencode(
					{'verify':self.verify,'uid':fuid,'r':"%.16f"%(random(),)}),),
					None)
				tree = etree.fromstring(r[0])
##				logging.debug("===> api_userevent返回: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
				title=tree.xpath('title')[0].text
				logging.info("%s %s(%s) 需要帮助: %s",task_key,fname,fuid,title)

				r = self.getResponse('http://www.kaixin001.com/cafe/api_doevent.php?%s'%
					(urllib.parse.urlencode(
					{'verify':self.verify,'uid':fuid,'ret':1}),),
					None)
				tree = etree.fromstring(r[0])
##				logging.debug("===> api_doevent返回: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
				addmycash=tree.xpath('addmycash')[0].text
				addmyevalue=tree.xpath('addmyevalue')[0].text
				logging.info("===> %s 因为帮助 %s(%s)，现金+%s 经验+%s",task_key,fname,fuid,addmycash,addmyevalue)

		# 自己添加到任务列表中
		t=Timer(self.internal4cafeDoEvent, self.cafe_doEvent)
		t.start()
		self.tasklist[task_key]=t

	def cafe_stoveclean(self,cafeid,orderid,task_key=''):
		logging.info("%s 灶台 %s 需要清洁",task_key,orderid)
		# 清洗灶台
		r = self.getResponse('http://www.kaixin001.com/cafe/api_stoveclean.php?%s'%
	    (urllib.parse.urlencode(
	    {'verify':self.verify,'cafeid':cafeid,'orderid':orderid,'rand':"%.16f"%(random(),)}),),
	    None)
		tree=etree.fromstring(r[0])
##		logging.debug("===> %s api_stoveclean返回: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))
		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			logging.info("===> %s 清洁灶台 %s 失败!\n%s",task_key,orderid,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return False

		addcash=tree.xpath('addcash')[0].text
		addevalue=tree.xpath('addevalue')[0].text
		logging.info("===> %s 清洁灶台 %s 成功, 现金 %s  经验 +%s",task_key,orderid,addcash,addevalue)
		return True

	def cafe_dish2counter(self,cafeid,orderid,name,task_key=''):
		logging.info("%s 将 灶台 %s 的 %s 端到餐台...",task_key,orderid,name)
		# 端到餐台
		r = self.getResponse('http://www.kaixin001.com/cafe/api_dish2counter.php?%s'%
	    (urllib.parse.urlencode(
	    {'verify':self.verify,'cafeid':cafeid,'orderid':orderid,'rand':"%.16f"%(random(),)}),),
	    None)
		tree = etree.fromstring(r[0])
##		logging.debug("===> %s api_dish2counter 返回: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))

		ret=tree.xpath('ret')[0].text
		if ret=='succ':
			orderid=tree.xpath('orderid')[0].text
			torderid=tree.xpath('torderid')[0].text
			addevalue=tree.xpath('addevalue')[0].text
			foodnum=tree.xpath('foodnum')[0].text
			evalue=tree.xpath('account/evalue')[0].text
			logging.info("===> %s 成功将 %s 从灶台 %s -->餐台 %s, 数量 %s 经验 %s(+%s)",
				task_key,name,orderid,torderid,foodnum,evalue,addevalue)
			self.cafe_dish2customer(cafeid,torderid,name,foodnum,5)
		else:
			logging.error("===> %s 灶台 %s 端到餐台失败!!! ret=%s (%s)",
				task_key,orderid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return False

		return True

	def cafe_checkStatus(self):
		logging.info("查看餐厅状态...")
		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False


		r=self.getResponse('http://www.kaixin001.com/!cafe/index.php')
		m = re.search('verify=(.+?)&', r[0].decode())
##		logging.info("verify=%s",m.group(1))
		self.verify = m.group(1)

		r = self.getResponse('http://www.kaixin001.com/cafe/api_getconf.php?%s'%
			(urllib.parse.urlencode(
			{'verify':self.verify,'rand':"%.16f"%(random(),),'loading':1}),),
			None)
		tree=etree.fromstring(r[0])

		cash=tree.xpath('account/cash')[0].text
		goldnum=tree.xpath('account/goldnum')[0].text
		evalue=tree.xpath('account/evalue')[0].text
		logging.info("现金/金币/经验: %s/%s/%s",cash,goldnum,evalue)
		cafeid=tree.xpath('cafe/cafeid')[0].text
		pvalue=tree.xpath('cafe/pvalue')[0].text
		cafewidth=tree.xpath('cafe/cafewidth')[0].text
		cafeheight=tree.xpath('cafe/cafeheight')[0].text
		logging.info("餐厅id=%s 魅力=%.1f 面积=%s×%s",cafeid,int(pvalue)/100.0,cafewidth,cafeheight)

		# 灶台
		logging.info("查看灶台...")
		cookings=tree.xpath('cooking/item')
		for i,item in enumerate(cookings):
			orderid=item.xpath('orderid')[0].text
			logging.info("%d/%d) 灶台 %s ...",i+1,len(cookings),orderid)
			try:
				stage=item.xpath('stage')[0].text
			except IndexError:
				logging.info("灶台 %s 是空的",orderid)
				self.cafe_cooking(cafeid,orderid,self.dish2cook)
				continue

			if stage=='-1': # 需要清洁?
				# 清洁灶台
				if self.cafe_stoveclean(cafeid,orderid):
					self.cafe_cooking(cafeid,orderid,self.dish2cook)
				continue

			try:
				dishid=item.xpath('dishid')[0].text
				name=item.xpath('name')[0].text
				step=item.xpath('step')[0].text
			except IndexError:
				logging.info("===> 解析dishid/name/step时失败！\n%s",etree.tostring(item,encoding='gbk').decode('gbk'))
				continue

			if stage=='0': # 在做
				tips=item.xpath('tips/tips')[0].text
				logging.info("灶台 %s 在做 %s(%s), %s.%s, 下一步需要 %s",orderid,name,dishid,stage,step,tips)
				# 继续做
				self.cafe_cooking(cafeid,orderid,dishid)

			elif stage=='1': # 耗时操作中
				autotime=item.xpath('autotime')[0].text
				timeleft=-int(autotime)
				strCur=''
				try:
					autoitems=item.xpath('auto/item')
					for item in autoitems:
						a_stage=item.xpath('stage')[0].text
						a_step=item.xpath('step')[0].text
						a_name=item.xpath('name')[0].text
						a_htime=item.xpath('htime')[0].text
						timeleft+=int(a_htime)
						if timeleft>0 and strCur=='':
							strCur="当前: %s.%s: %s(%ss)"%(a_stage,a_step,a_name,a_htime)
##						logging.info("灶台 %s 后续: %s.%s: %s(%ss)",orderid,a_stage,a_step,a_name,a_htime)
					logging.info("灶台 %s 在做 %s(%s)(%s.%s), %s 剩余时间%ds",
						orderid,name,dishid,stage,step,strCur,timeleft)
					if timeleft<self.internal:
						k='cafe-%s'%(orderid,)
						if k in self.tasklist:
							logging.info("删除相同的任务...")
							self.tasklist[k].cancel()
							del self.tasklist[k]
						logging.info("加入定时执行队列 key=%s %d (%s,%s,%s)",
							k,timeleft+1,cafeid,orderid,k)
						t=Timer(timeleft+1, self.task_cafe,(cafeid,orderid,k))
						t.start()
						self.tasklist[k]=t

				except IndexError:
					logging.info("不包含 auto/item 信息或者解析失败! ")
			elif stage=='2': # 做好了
				logging.info("灶台 %s 的 %s 做好了?",orderid,name)
				if self.cafe_dish2counter(cafeid,orderid,name): # 端到餐台
					if self.cafe_stoveclean(cafeid,orderid): # 清洁灶台
						self.cafe_cooking(cafeid,orderid,self.dish2cook) # 做


		# 餐台
		logging.info("查看餐台...")
		dishs=tree.xpath('dish/item')
		for i,item in enumerate(dishs):
			orderid=item.xpath('orderid')[0].text
			logging.info("%d/%d) 餐台 %s ...",i+1,len(dishs),orderid)
			try:
				name=item.xpath('name')[0].text
				dishid=item.xpath('dishid')[0].text
				foodnum=item.xpath('foodnum')[0].text
				num=item.xpath('num')[0].text
			except IndexError:
				logging.info("餐台 %s 是空的？",orderid)
				continue
			logging.info("餐厅 %s 有 %s/%s %s(%s)",orderid,num,foodnum,name,dishid)
##			logging.debug("餐台信息: %s\n",etree.tostring(item,encoding='gbk').decode('gbk'))
			self.cafe_dish2customer(cafeid,orderid,name,num,5)

	def cafe_dish2customer(self,cafeid,orderid,dishname,num,pernum,task_key=''):
		logging.info("%s 消费餐台 %s 上的 %s, 总共 %s, 每次 %d ...",
			task_key,orderid,dishname,num,pernum)
		numleft=int(num)
		if pernum>numleft:
			pernum=numleft

		while numleft:
			r = self.getResponse('http://www.kaixin001.com/cafe/api_dish2customer.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'cafeid':cafeid,'orderid':orderid,'num':pernum,'rand':"%.16f"%(random(),)}),),
				None)
			tree=etree.fromstring(r[0])
##			logging.debug("===> api_dish2customer 返回: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.info("%s 消费餐台 %s 的 %s 出错(%s)\n%s",
					task_key,orderid,dishname,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				return False
			oid=tree.xpath('orderid')[0].text
			assert oid==orderid
			pvalue=tree.xpath('pvalue')[0].text
			cash=tree.xpath('account/cash')[0].text
			addcash=tree.xpath('addcash')[0].text
			foodnum=tree.xpath('foodnum')[0].text
			leftnum=tree.xpath('leftnum')[0].text
##			customernum=tree.xpath('customernum')[0].text
			numleft=int(leftnum)
			if pernum>numleft:
				pernum=numleft
			customernum=tree.xpath('customernum')[0].text
			logging.info("===> %s 成功消费了餐台 %s 上的 %s, %s->%s, 现金 %s(+%s), 魅力 %.1f, next %d",
				task_key,orderid,dishname,foodnum,leftnum,cash,addcash,int(pvalue)/100.0,pernum)

		return True


	def task_cafe(self,cafeid,orderid,task_key):
		if task_key in self.tasklist:
			del self.tasklist[task_key]

##		if not self.signed_in:
##			self.signin()
##			if not self.signed_in:
##				return False
		logging.info("%s 检查灶台 %s ... ",task_key,orderid)

		r = self.getResponse('http://www.kaixin001.com/cafe/api_checkfood.php?%s'%
			(urllib.parse.urlencode(
			{'verify':self.verify,'cafeid':cafeid,'orderid':orderid,'rand':"%.16f"%(random(),)}),),
			None)
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			logging.error("===> %s 获取灶台 %s 信息失败!!! ret=%s (%s)",
				task_key,orderid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return False
		stage=tree.xpath('stage')[0].text
		oid=tree.xpath('orderid')[0].text
		assert orderid==oid
		if stage=='0': # 在做
			logging.error("%s 灶台 %s 准备下一步(%s)\n%s",task_key,orderid,stage,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return False
		if stage=='-1': # 需要清洁
			logging.info("%s 灶台 %s 需要清洁(%s)",task_key,orderid,stage)
			if self.cafe_stoveclean(cafeid,orderid,task_key):
				self.cafe_cooking(cafeid,orderid,self.dish2cook,task_key)
		elif stage=='1': # 耗时操作中
			logging.info("%s 灶台 %s 还在做(%s)",task_key,orderid,stage)
		elif stage=='2': # 做好了
			logging.info("%s 灶台 %s 做好了(%s)",task_key,orderid,stage)
			if self.cafe_dish2counter(cafeid,orderid,'xxxx',task_key):
				if self.cafe_stoveclean(cafeid,orderid,task_key):
					self.cafe_cooking(cafeid,orderid,self.dish2cook,task_key)
		else:
			logging.error("===>%s 灶台 %s 的状态未知(%s)!!! ret=%s (%s)",task_key,orderid,stage,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return False

		return True

	def cafe_cooking(self,cafeid,orderid,dishid,task_key=''):
		'''做菜 cafeid=餐厅id orderid=灶台id dishid=菜名id'''
		logging.info("%s 尝试在灶台 %s 上做 %s ...",task_key,orderid,dishid)
		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False

		for i in range(5):
##			logging.info("第 %d 次 ...",i+1)
			r = self.getResponse('http://www.kaixin001.com/cafe/api_cooking.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'cafeid':cafeid,'orderid':orderid,'dishid':dishid,'rand':"%.16f"%(random(),)}),),
				None)
			tree=etree.fromstring(r[0])
##			logging.debug("===> %s api_cooking: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))
			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.info("===> %s 灶台 %s 上做菜失败(%s)!\n%s",
					task_key,orderid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				return False
			dish_name=tree.xpath('dish/name')[0].text
			stage=tree.xpath('dish/stage')[0].text
			if stage!='1':
				step_name=tree.xpath('dish/stepname')[0].text
				tips=tree.xpath('dish/tips/tips')[0].text
				logging.info("%s 灶台 %s %s/%s, 下一步: %s",task_key,orderid,step_name,dish_name,tips)
				continue

##			logging.debug("%s 灶台 %s 菜名 %s 进入耗时阶段(%s) \n%s",
##				task_key,orderid,dish_name,stage,etree.tostring(tree,encoding='gbk').decode('gbk'))

			autotime=tree.xpath('dish/autotime')[0].text # 进入自动阶段,开始计时
			timeleft=-int(autotime)
			strCur=''
			try:
				autoitems=tree.xpath('dish/auto/item')
				for item in autoitems:
					a_stage=item.xpath('stage')[0].text
					a_step=item.xpath('step')[0].text
					a_name=item.xpath('name')[0].text
					a_htime=item.xpath('htime')[0].text
					timeleft+=int(a_htime)
					if timeleft>0 and strCur=='':
						strCur="当前: %s.%s: %s(%ss)"%(a_stage,a_step,a_name,a_htime)
##					logging.info("灶台 %s 后续: %s.%s: %s(%ss)",orderid,a_stage,a_step,a_name,a_htime)
				logging.info("%s 灶台 %s 在做 %s(%s), %s 剩余时间%ds",task_key,orderid,dish_name,dishid,strCur,timeleft)
				if timeleft<self.internal:
					k='cafe-%s'%(orderid,)
					if k in self.tasklist:
						logging.info("%s 删除相同的任务...",task_key)
						self.tasklist[k].cancel()
						del self.tasklist[k]
					logging.info("%s 加入定时执行队列 key=%s %d (%s,%s,%s)",
						task_key,k,timeleft+1,cafeid,orderid,k)
					t=Timer(timeleft+1, self.task_cafe,(cafeid,orderid,k))
					t.start()
					self.tasklist[k]=t
			except IndexError:
				logging.info("%s 不包含 auto/item 信息或者解析失败! ",task_key)

			break


	def cafe_getDishlist(self):
		logging.info("获取菜谱 ... ")
		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False

		ptag=re.compile('(<.*?>)',re.M|re.U|re.S) # 过滤html的tag

		r=self.getResponse('http://www.kaixin001.com/!cafe/index.php')
		m = re.search('verify=(.+?)&', r[0].decode())
##		logging.info("verify=%s",m.group(1))
		self.verify = m.group(1)

		s=StringIO()
		pageno=0
		bnext='1'
		while bnext=='1':
			r = self.getResponse('http://www.kaixin001.com/cafe/api_dishlist.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'page':pageno,'r':"%.16f"%(random(),)}),),
				None)
			tree=etree.fromstring(r[0])
##			logging.debug("===> api_dishlist: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
			bnext=tree.xpath('bnext')[0].text
			pageno+=1

			dishs=tree.xpath('dish/item')
			for item in dishs:
				dishid=item.xpath('dishid')[0].text
				title=item.xpath('title')[0].text
				tag=item.xpath('tag')[0].text
				taglist=[i for i in tag.split('<br>') if i!='']
				tag2=item.xpath('tag2')[0].text
				tag2list=[i for i in tag2.split('<br>') if i!='']
				val=item.xpath('val')[0].text
				vallist=[i for i in val.split('<br>') if i!='']
				val2=item.xpath('val2')[0].text
				val2list=[i for i in val2.split('<br>') if i!='']
				val2list=[ptag.sub('',i) for i in val2list]
				dishinfo=dict(zip(taglist+tag2list,vallist+val2list))
				for k,v in dishinfo.items():
					s.write('%s%s, '%(k,v))
				bbuy=item.xpath('bbuy')[0].text
				buyable=item.xpath('buyable')[0].text
				tips=item.xpath('tips')[0].text
				price=item.xpath('price')[0].text

				logging.info("%s(%s) bbuy/buyable/price/tips:%s/%s/%s/%s, \n%s",title,dishid,bbuy,buyable,price,tips,s.getvalue())
				s.seek(0)
				s.truncate()

		s.close()



if __name__=='__main__':
	import logging
	from lxml import etree
	import re, time#, thread, webbrowser
	from pprint import pprint
	from io import StringIO
	from random import uniform, random
	import urllib, urllib.request, urllib.error, urllib.parse, http.cookiejar, json
	import configparser
	import codecs
	import os
	import copy
	from threading import Timer
	import datetime
	import socket
	import sys
	import shelve
	import imp
	from html.entities import name2codepoint

	i=Kaixin(r'd:\kaixin.ini')
##	i.getFishinfo()
	i.run()
##	import cProfile,pstats
##	cProfile.run('''Kaixin(r'd:\kaixin.ini').run()''',r'd:\kaixin-profile.txt')
	#p=pstats.Stats(ur'd:\kaixin-profile.txt')
	#p.sort_stats('time', 'cum').print_stats('kaixin')
