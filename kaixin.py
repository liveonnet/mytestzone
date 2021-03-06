#!/usr/bin/env python
#coding=utf-8
from threading import Thread

doagainevent=None # 目前没有用
exitevent=None
# 信号处理程序
def SignalHandler(sig,id):
	global doagainevent,exitevent
	if sig==signal.SIGUSR1:
		print('received signal USR1')
		if doagainevent:
			doagainevent.set()
	if sig==signal.SIGTERM:
		print('received signal TERM, exit app...')
		if exitevent:
			exitevent.set()

# 装饰器
# 将对 Kaixin.getResponse() 的调用转为对 ThreadPool4Kaixin.getResponse() 的调用
def threadpool_wrapfunc(func):
	assert func.__name__=='getResponse' # 只用于 Kaixin.getResponse()
	def wrappedFunc(*args,**kwargs):
#		if len(kwargs)!=0: # 带额外参数
#			logging.debug("args=%s, kwargs=%s",args,kwargs)
		return args[0].pool.getResponse(func,*args,**kwargs)
	return wrappedFunc


class Worker(Thread):
	'''工作线程，配合线程池工作，发送 (-1,None,None,None) 到任务队列可触发接受此任务的
	线程退出'''
	def __init__(self,pool,name=''):
		Thread.__init__(self)
		self.__pool=pool
		self.daemon=True
		if name:
			self.name=name
		self.start()

	def run(self):
##		logging.info("isDaemon=%s",self.isDaemon())
		get=self.__pool.getTask
		r=None
		while True:
			k,func,args,kwargs=get()
##			k,func,args,kwargs=self.__pool.getTask()
			if k==-1:
				logging.info("工作线程 %s 退出.",self.name)
				break
##			logging.info("工作 %s 获取任务 k=%s func=%s args=%s kwargs=%s",self.name,k,func.__name__,args,kwargs)
			try:
				r=func(*args,**kwargs)
			except Exception as e:
				logging.info("工作线程 %s 执行func发生异常: k=%s func=%s args=%s kwargs=%s\n%s",self.name,k,func.__name__,args,kwargs,e)
			finally:
				self.__pool.putResult(k,r)

class ThreadPool4Kaixin(object):
	'''简单的限速线程池，不支持动态改变工作线程数量，不支持动态改变限速'''
	def __init__(self,workernum,speedlimit):
		'''workernum指定工作线程的数量，speedlimit指定每个任务之间的间隔，=0 则不限速'''
		self.__workers=[]
		self.__tasks=Queue(0) # 工作线程访问的任务队列
		self.__faketasks=Queue(0) # 外部对象发送请求时插入的任务队列
##		self.__workernum=workernum
		self.__speedlimit=speedlimit

		self.__taskresult={} # 存放返回的结果
		self.__lock4result=Lock() # 修改self.__taskresult时需要
		self.__condition4result=Condition(self.__lock4result) # 唤醒查看self.__taskresult的线程时需要
		# 初始化工作线程
		for i in range(workernum):
			self.__workers.append(Worker(self,'worker-%02d'%(i+1,)))

		self.thread2controlspeed=None
		self.exitevent=Event() # 触发速度控制线程退出
		if speedlimit==0: # 不限速
			self.__faketasks=self.__tasks
		else:
			self.thread2controlspeed=Timer(0,self.limitSpeedThread,()) # 创建速度控制线程
			self.thread2controlspeed.start()
##			_thread.start_new_thread(self.limitSpeedThread,()) # 启动速度控制线程


	def getTask(self):
		'''工作线程调用，获取待执行请求'''
		return self.__tasks.get()

	def putResult(self,k,rslt):
		'''工作线程调用，放入返回结果rslt'''
		self.__tasks.task_done() # 与 self.__tasks.get() 匹配
		# 放入结果, 唤醒等待者
		with self.__condition4result:
			self.__taskresult[k]=rslt
			self.__condition4result.notify_all()

	def getResponse(self,func,*args,**kwargs):
		'''线程池使用者调用，放入请求并获取相应结果'''
		# 生成k，以区分出自己的返回数据
##		k=datetime.datetime.now().strftime('%M%S%f')
		k="%.16f"%(random(),)

		# 放入请求数据(函数和参数)
		if kwargs.get('nolimitspeed',False)==True: # 不限速
			self.__tasks.put((k,func,args,kwargs))
		else:
			self.__faketasks.put((k,func,args,kwargs))

		# 等待结果
		while True:
			with self.__condition4result:
				self.__condition4result.wait()
				if k in self.__taskresult: # 是自己要的数据
					return self.__taskresult.pop(k)

	def exit(self):
		'''退出线程池，结束所有工作线程'''
		if self.thread2controlspeed: # 控制速度线程存在
			self.exitevent.set()
			self.thread2controlspeed.join()

		logging.info("等待任务队列被处理完...")
		self.__tasks.join()

		for i in range(3):
			if len(self.__taskresult)!=0:
				logging.info("等待 任务结果全被取走...%02ds",(i+1)*2)
				time.sleep((i+1)*2)
		if len(self.__taskresult)!=0:
			logging.info("丢弃未取走的任务结果!\n%s",'\n'.join(('%s=%s'%(v[1],v[0].decode('utf8')) for v in self.__taskresult.values())))
			self.__taskresult.clear()

		logging.info("触发工作线程退出...")
		for _ in range(len(self.__workers)):
			self.__tasks.put((-1,None,None,None))
		for t in self.__workers:
			t.join()

		logging.info("线程池退出")

	def limitSpeedThread(self):
		'''控制速度的线程，通过控制请求进入任务队列的速度来控制任务执行频率
		目前不区分请求的来源'''
		logging.info("速度控制线程启动, 速度限制为 %.2f秒.",self.__speedlimit)
		maxfaketasks=0
		while True:
			time.sleep(self.__speedlimit)
			try:
				x=self.__faketasks.get_nowait()
				self.__tasks.put(x)
##				logging.debug("控制速度线程 队列长度 %d",self.__faketasks.qsize())
				if maxfaketasks<self.__faketasks.qsize():
					maxfaketasks=self.__faketasks.qsize()
			except Empty:
				if self.exitevent.is_set():
					logging.info("控制速度线程退出, 最大队列长度 %d",maxfaketasks)
					break


class Kaixin(object):
	def __init__(self,inifile='kaixin.ini'):
		global doagainevent,exitevent
		imp.reload(sys)
		sys.setdefaultencoding('utf-8')
		self.cfgData={}
		self.curdir=os.path.abspath('.')

		self.inifile=inifile
		if not os.path.isabs(inifile):
			self.inifile=os.path.join(self.curdir,self.inifile)

		self.cfg=configparser.SafeConfigParser()
		self.cfg.readfp(codecs.open(self.inifile,'r','utf-8-sig'))

		self.rundate=time.strftime('%Y%m%d') # 记录执行日期

		# logging to file
		self.cfgData['logdir']=self.cfg.get('account','logdir',self.curdir)
		self.cfgData['logsuffix']=self.cfg.get('account','logsuffix','%d'%(os.getpid(),))
		if self.cfgData['logdir']:
			if not os.path.isabs(self.cfgData['logdir']):
				if os.path.expanduser(self.cfgData['logdir']) == self.cfgData['logdir']:
					self.cfgData['logdir']=os.path.join(self.curdir,self.cfgData['logdir'])
				else:
					self.cfgData['logdir']=os.path.expanduser(self.cfgData['logdir'])
			self.logfile=os.path.join(self.cfgData['logdir'],'kaixin-%s-%s.log'%(self.rundate,self.cfgData['logsuffix']))
			logging.basicConfig(level=logging.DEBUG,
		#			format="%(asctime)s %(levelname)s %(funcName)s | %(message)s",
				  format='%(asctime)s %(thread)d %(levelname)s %(funcName)s %(lineno)d | %(message)s',
				  datefmt='%H:%M:%S',
				  filename=self.logfile,
				  filemode='a')
			# loggin to console
			if __name__=='__main__':
				console=logging.StreamHandler()
				console.setLevel(logging.INFO)
				console.setFormatter(logging.Formatter('%(asctime)s %(message)s','%H:%M:%S'))
				logging.getLogger('').addHandler(console)
			logging.info("log file: %s",self.logfile)
		else: # 为空则认为是log不写入文件，只输出到stdout
			logging.basicConfig(level=logging.INFO,
				format='%(thread)d %(message)s')
			logging.info("=== log不写入文件.===")

		logging.info("\n\n%s\n%s start %s %s\n%s\n 脚本最后更新: %s",'='*75,'='*((75-8-len(sys.argv[0]))//2),sys.argv[0],'='*((75-8-len(sys.argv[0]))//2),'='*75,time.strftime('%Y%m%d %H:%M:%S',time.localtime(os.stat(sys.argv[0]).st_mtime)))
		logging.info("ini file: %s",self.inifile)

		self.cfgData['email']=self.cfg.get('account','email')
		self.cfgData['pwd']=self.cfg.get('account','pwd')
		self.cfgData['cookiefile']=self.cfg.get('account','cookiefile')
		if self.cfgData['cookiefile']!=os.path.expanduser(self.cfgData['cookiefile']):
			self.cfgData['cookiefile']=os.path.expanduser(self.cfgData['cookiefile'])
		logging.info("cookie file: %s",self.cfgData['cookiefile'])

		self.signed_in = False
		self.cj = http.cookiejar.LWPCookieJar()
		try:
			self.cj.revert(self.cfgData['cookiefile'])
		except:
			None
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
		urllib.request.install_opener(self.opener)
##		self.opener.handle_open['http'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息

		seedlist=self.cfg.get('account','seedlist')
		self.cfgData['seedlist']=json.JSONDecoder().decode(seedlist)
		logging.info("已知作物数 %d",len(self.cfgData['seedlist']))
		#self.cfgData['seedlist'].sort(cmp=lambda x,y: cmp(x[0], y[0]),reverse=True)

		self.cfgData['autofarm']=json.JSONDecoder().decode(self.cfg.get('account','autofarm'))

		animallist=self.cfg.get('account','animallist')
		self.cfgData['animallist']=json.JSONDecoder().decode(animallist)
		logging.info("已知牧场产品数 %d",len(self.cfgData['animallist']))

		ignoreseeds=self.cfg.get('account','ignoreseeds')
		self.cfgData['ignoreseeds']=json.JSONDecoder().decode(ignoreseeds) # 忽略不处理的作物

		gardenignorefriends=self.cfg.get('account','gardenignorefriends')
		self.cfgData['gardenignorefriends']=json.JSONDecoder().decode(gardenignorefriends)# 忽略不查看的花园

		ranchignorefriends=self.cfg.get('account','ranchignorefriends')
		self.cfgData['ranchignorefriends']=json.JSONDecoder().decode(ranchignorefriends)# 忽略不查看的牧场

		forcestealseeds=self.cfg.get('account','forcestealseeds')
		self.cfgData['forcestealseeds']=json.JSONDecoder().decode(forcestealseeds) # 强制偷取的作物(不考虑其价值)

		antisteal=self.cfg.get('account','antisteal')
		self.cfgData['antisteal']=json.JSONDecoder().decode(antisteal) # 有防偷期的动物
		#pprint(self.cfgData['antisteal'])

		self.cfgData['internal']=self.cfg.getint('account','internal') # 轮询间隔
		self.cfgData['internal4cafeDoEvent']=self.cfg.getint('account','internal4cafeDoEvent') # 餐厅时间轮询间隔
		logging.info("轮询间隔 %d",self.cfgData['internal'])
		self.cfgData['bStealCrop']=self.cfg.getboolean('account','StealCrop') # 偷农场作物
		self.cfgData['bStealRanch']=self.cfg.getboolean('account','StealRanch') # 偷牧场副产品
		self.cfgData['bGetGranaryInfo']=self.cfg.getboolean('account','GetGranaryInfo') # 获取仓库信息(据此更新seedlist的价格)
		self.cfgData['bDoCafeEvent']=self.cfg.getboolean('account','DoCafeEvent') # 查看餐厅事件
		self.cfgData['bCheckCafe']=self.cfg.getboolean('account','CheckCafe') # 做餐厅服务
		self.cfgData['bDoCooking']=self.cfg.getboolean('account','DoCooking') # 做菜

		friends=self.cfg.get('account','friends')
		self.cfgData['friends']=json.JSONDecoder().decode(friends) # 好友列表
		logging.info("已知好友数 %d",len(self.cfgData['friends']))

		# 打印忽略作物
		logging.info("忽略作物: %s",
			' '.join( ( "%s(%s)"%(j,i) for i,j in ( (x[1],x[2]) for x in self.cfgData['seedlist'] if x[1] in self.cfgData['ignoreseeds'] ) ) )
		)

		# 打印强制偷取的作物
		logging.info("强制偷取的作物: %s",
			' '.join(	( "%s(%s)"%(j,i) for i,j in ( (x[1],x[2]) for x in self.cfgData['seedlist'] if x[1] in self.cfgData['forcestealseeds'] ) ) )
		)

		# 打印自动播种作物
		logging.info("自动播种作物: %s",
			' '.join( ( "%s=%s(%s)"%(k,[x for x in self.cfgData['seedlist'] if x[1]==v][0][2],v) for k,v in self.cfgData['autofarm'].items() ) )
		)


		self.friends4garden=[] # 待检查garden的用户
		self.friends4ranch=[] # 待检查ranch的用户
		self.crops2steal=[] # 待偷的作物列表

		self.tasklist={} # 定时任务

		# 统计收获
		if self.cfgData['logdir']:
			self.statistics=shelve.open(os.path.join(self.cfgData['logdir'],'kaixin-%s.statistics'%(self.cfgData['logsuffix'],)))
		else:
			self.statistics=shelve.open(os.path.join(self.curdir,'kaixin-%s.statistics'%(self.cfgData['logsuffix'],)))

		# 检查的地块
		self.FarmBlock2Check=['1','2','3','9','13','4','5','8','11','14','20','21','22','23','24']

		self.verify=''

		self.uid='' # 自己的uid
		self.cafeid='' # cafe的id
		self.cafeverify='' # 餐厅专用verify
		#
		#  < webaccess_normal 正常  &&
		#  < webaccess_lowfrq 低频  &&
		#  被F5
		self.COOKMODE_UNKNOWN,self.COOKMODE_NORMAL,self.COOKMODE_LOWFRQ,self.COOKMODE_F5,self.COOKMODE_NIGHT=range(5) # 定义餐厅模式
		self.curcookmode=self.COOKMODE_UNKNOWN # 初始状态未知
		self.cfgData['dish2cook']=-1 # 初始做的菜id为-1(无效值)
		self.cfgData['webaccess_normal']=self.cfg.getint('account','webaccess_normal') # 访问计数低于此值属于正常情况
		self.cfgData['dish2cook_normal']=self.cfg.get('account','dish2cook_normal') # 正常情况下做的菜

		self.cfgData['webaccess_lowfrq']=self.cfg.getint('account','webaccess_lowfrq') # 访问计数到达此值进入低频模式
		self.cfgData['dish2cook_lowfrq']=self.cfg.get('account','dish2cook_lowfrq') # 低频模式下做的菜

		self.cfgData['dish2cook_bfrnight']=self.cfg.get('account','dish2cook_bfrnight') # 接近被F5前做的菜的列表

		self.cfgData['dish2cook_night']=self.cfg.get('account','dish2cook_night') # 夜晚做的菜

		# X世界相关配置
		self.cfgData['bDoSpidermanFight']=self.cfg.getboolean('account','DoSpidermanFight') # 是否战斗
		self.cfgData['internal4spidermanfight']=self.cfg.getint('account','internal4spidermanfight') # 餐厅时间轮询间隔


		self.consumepertime=500 # 餐台上积累多少菜时才开始给客人送菜
		self.consumeerrcnt=50 # 送菜出错超过这个次数则停止送菜
		self.event4cafe={} # 存放对应消费线程的事件信号
		self.cafemana=0 # 大厨体力
		self.semaphore4cafemana=Semaphore() # 同步对大厨体力值的访问

		self.doagainevent=Event() # 等待触发X战斗的信号 目前没用
		doagainevent=self.doagainevent

		self.exitevent=Event() # 标识退出整个程序的事件信号
		exitevent=self.exitevent
		# 标识监视文件线程退出等待状态的win32信号
		self.monitorThreadExitEventHandle=None

		try:
			self.cfgData['file2monitor']=self.cfg.get('account','file2monitor')
		except configparser.NoOptionError:
			pass
		else:
			# 创建监控线程
			try:
				import win32api
				import win32event
			except ImportError:
				logging.info("没有win32模块，监控线程不启动")
			else:
				self.monitorThreadExitEventHandle=win32event.CreateEvent(None,True,False,None)
				_thread.start_new_thread(self.monitorExitFlag,())

		self.semaphore4accessCnt=Semaphore() # 控制对统计变量的访问
		# 具体记录访问不同组件的次数
		statistics4WebAccessData=None
		try:
			statistics4WebAccessData=self.cfg.get('stat-%s'%(self.rundate,),'statisticswebaccess')
		except configparser.NoSectionError:
			self.cfg.add_section('stat-%s'%(self.rundate,))
		except configparser.NoOptionError:
			pass
		if statistics4WebAccessData:
			logging.info("在原有 %s 统计数据基础上继续统计.",self.rundate)
			self.cfgData['statistics4WebAccessData']=json.JSONDecoder().decode(statistics4WebAccessData)
		else:
			logging.info("无 %s 统计数据, 开始全新统计.",self.rundate)
			self.cfgData['statistics4WebAccessData']={}


		try:
			self.cfgData['limitspeed']=self.cfg.getfloat('account','limitspeed')
		except configparser.NoOptionError:
			self.cfgData['limitspeed']=2.0 # 默认访问间隔为2.0秒
		self.pool=ThreadPool4Kaixin(10,self.cfgData['limitspeed']) # 建立线程池

		if sys.platform=='linux2':
			# 注册信号处理程序
			signal.signal(signal.SIGUSR1,SignalHandler)
			signal.signal(signal.SIGTERM,SignalHandler)

		logging.info("%s 初始化完成.",self.__class__.__name__)

	def signin(self):
		"""登录"""
		r = self.getResponse('http://www.kaixin001.com/home/')
		if not r:
			return
		if r[1] == 'http://www.kaixin001.com/?flag=1&url=%2Fhome%2F':
			logging.debug("需要登录!")
			params = {'email':self.cfgData['email'], 'password':self.cfgData['pwd'], 'remember':1,'invisible_mode':0,'url':'/home/'}
			r = self.getResponse('http://www.kaixin001.com/login/login.php',params)

			m=re.match(r'http://www.kaixin001.com/home/\?uid=(\d{7,}|)',r[1])
			if m:
				logging.debug("登录成功! uid=%s .",m.group(1))
				self.uid=m.group(1)
				if self.uid not in self.cfgData['friends']:
					self.cfgData['friends'][self.uid]='～自己～'
				self.cj.save(self.cfgData['cookiefile'])
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

					params = {'email':self.cfgData['email'], 'password':self.cfgData['pwd'],
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
					self.exitevent.set()
					#sys.exit(1)
		else:
			logging.debug("无需登录! %s",r[1])
			self.signed_in = True
			m=re.search(r'"我的开心网ID:(\d{5,10})"',r[0].decode())
			if m:
				self.uid=m.group(1)
				if self.uid not in self.cfgData['friends']:
					self.cfgData['friends'][self.uid]='～自己～'
				logging.info("uid = %s",self.uid)

	def getFriends4garden(self):
		"""获取可偷取花园作物的好友列表"""
		if not self.signed_in:
			self.signin()
		if self.signed_in:
			del self.friends4garden[:]
			if not self.house_updateVerify(
					'http://www.kaixin001.com/!house/garden/index.php',
					'var g_verify = "(.+)";',False):
				return

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
				if (fname,fuid) not in self.friends4garden and fuid not in self.cfgData['gardenignorefriends']:
##					if f.get('harvest',None)==1:
					self.friends4garden.append((fname,fuid))
				if fuid not in self.cfgData['friends']:
					self.cfgData['friends'][fuid]=fname

			self.friends4garden.append(('～自己～',self.uid))
			#logging.info(u"self.friends4garden=%s",self.friends4garden)
			#logging.info(u"self.cfgData['friends']=%s",self.cfgData['friends'])
			#raw_input()


	def checkGarden(self):
		"""地块
							20 21 22 23 24
							1  2  3  9  13
							4  5  8  11 14
							6  7  10 12 15
		"""
		logging.info("共检查%d个好友的花园.",len(self.friends4garden))

		p=re.compile(r'(?:已产|产量)?：(?P<all>\d+)<br />剩余：(?P<left>\d+)')
		pgrow=re.compile(r'生长阶段：(\d+)%.+?距离收获：(\d+天)?(\d+小时)?(\d+分)?(\d+秒)?')

		cnt=0
		del self.crops2steal[:]
		for fname,fuid in self.friends4garden:
			if self.exitevent.is_set():
				logging.info("检测到退出信号.")
				break
##		for fuid,fname in self.cfgData['friends'].items():
			cnt+=1
			logging.info("花园检查 %02d) %s(%s)... ",cnt,fname,fuid)
##			r = self.getResponse('http://www.kaixin001.com/house/garden/getconf.php',
##				{'verify':self.verify,'fuid':fuid})
			if fuid==self.uid: # 是自己
				r = self.getResponse('http://www.kaixin001.com/!house/!garden//getconf.php?%s'%
					(urllib.parse.urlencode(
					{'verify':self.verify,'fuid':'0','r':"%.16f"%(random(),)}),),
					None)
			else:
				r = self.getResponse('http://www.kaixin001.com/!house/!garden//getconf.php?%s'%
					(urllib.parse.urlencode(
					{'verify':self.verify,'fuid':fuid,'r':"%.16f"%(random(),)}),),
					None)

			try:
				tree = etree.fromstring(r[0])
			except etree.XMLSyntaxError as e:
				if r[0].decode().find('还没有添加本组件!')!=-1:
					logging.info("%s(%s) 没有添加本组件!",fname,fuid)
					continue
				else:
					logging.info("%s(%s) tree = etree.fromstring(r[0]) 出错!\n%s\n%s",fname,fuid,e,r[0].decode('utf8'))



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
					status=i.xpath('status')[0].text
					if status=='0':
						pass
##						logging.debug("地块 %s 尚未开发",farmnum)
					elif fuid==self.uid: # 自己的地
						self.garden_plan(farmnum)
					continue

				if cropsstatus=='-1':
##					logging.debug("地块 %s 为枯死的作物",farmnum)
					continue
				if cropsstatus=='3':
##					logging.debug("地块 %s 已经收获光未犁地",farmnum)
					if fuid==self.uid: # 是自己
						if self.garden_plough(farmnum):
							self.garden_plan(farmnum)
					continue

##				logging.debug("地块 %s cropsstatus=%s",farmnum,cropsstatus)

				name=i.xpath('name')[0].text
				crops=i.xpath('crops')[0].text
				seedid=i.xpath('seedid')[0].text # 变异后的种类
				oriseedid=i.xpath('oriseedid')[0].text # 原种类

				if fuid!=self.uid and (oriseedid in self.cfgData['ignoreseeds']): # 不是自己且属于被忽略作物则略过
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
				if seedid not in [x[1] for x in self.cfgData['seedlist']]: # 未知
					self.cfgData['seedlist'].append([4321,seedid,name])
					logging.info("发现未知作物:\n\t[4321,\"%s\",\"%s\"],\n",seedid,name)

				m=re.match(p,crops)
				if m:
					all=m.group('all')
					left=int(m.group('left'))
					if crops.find('已摘过')==-1:

						n=re.search(r'再过(\d+小时)?(\d+分)?(\d+秒)?好友可摘',crops)
						if n:
							logging.info("%s(%s) 地块 %s %s(%s) 在防偷期! (%s)",fname,fuid,farmnum,name,seedid,crops)

							scd=self.getSleepTime(n.groups())
							if scd<self.cfgData['internal']+10: # 下次轮询前不需执行则不加入定时任务
								k='crop-%s-%s-%s'%(fuid,farmnum,seedid)
								if k not in self.tasklist: # 相同的任务不存在
									# 判断是否存在同一块地不同seedid的任务，如果存在则先删除
									samek='crop-%s-%s-'%(fuid,farmnum)
									for i in self.tasklist:
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
									t=Timer(scd+0.1, self.stealOneCrop,(farmnum,seedid,oriseedid,fuid,k))
								else:
									t=Timer(scd, self.task_garden,(farmnum,seedid,fuid,k))
								t.start()
								self.tasklist[k]=t

						elif left>1:
							logging.info("%s(%s) (可偷) %d/%s (地块%s--%s(%s)--%s)",fname,fuid,left,all,farmnum,name,seedid,crops)
							self.crops2steal.append((farmnum,seedid,oriseedid,fuid))
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
					logging.info("%s(%s) (可偷) 洋槐蜂蜜 %s, 枸杞蜂蜜 %s, 党参蜂蜜 %s, count/total/sum=%s/%s/%s",
						fname,fuid,count_a,count_b,count_c,count,total,sumtext)
					self.stealHoney(fuid)


	def stealCrop(self):
		"""依次尝试偷取值得偷的作物"""
		# 只偷贵的
		tosteal=self.getValueItems(1000)
		logging.info("根据作物价值偷%d个.",len(tosteal))
		if tosteal==0:
			return True


		# 看是否有曼陀罗，如果有则放到最后偷
		foundStramonium=False
		seednamelist=[x[1] for x in self.cfgData['seedlist'] if x[2].find("曼陀罗")!=-1] # 叫曼陀罗的植物的seedid列表
		toend=[] # 存放需要后移的曼陀罗
		for farmnum,seedid,oriseedid,fuid in tosteal:
			if oriseedid in seednamelist:
				foundStramonium=True
				logging.info("发现有曼陀罗 (%s,%s<-%s,%s)",farmnum,seedid,oriseedid,fuid)
				toend.append((farmnum,seedid,oriseedid,fuid))
		if foundStramonium:
			for i in toend:	tosteal.remove(i)
			#for i in toend:	tosteal.append(i) # 注释掉以避免偷取曼陀罗类作物
			#t=StringIO()
			#pprint(tosteal,t)
			#logging.info(u"found Stramonium\n%s",t.getvalue())
			#t.close()

		for idx,(farmnum,seedid,oriseedid,fuid) in enumerate(tosteal):
			rslt=self.stealOneCrop(farmnum,seedid,oriseedid,fuid)
			if rslt==False: # 被反外挂检测到
				break
##			if idx!=len(tosteal)-1:
##				sleeptime=uniform(3,7)
##				logging.debug("延迟%f秒以逃避反外挂检测...",sleeptime)
##				time.sleep(sleeptime)

		return True

	def stealOneCrop(self,farmnum,seedid,oriseedid,fuid,taskkey='',**kwargs):
		"""偷取单一作物"""
		tasklogstring=''
		if taskkey!='':
			tasklogstring='[任务 %s]'%(taskkey,)
			logging.info("执行定时任务 %s ...",taskkey)
			# 从tasklist中删除任务
			if taskkey in self.tasklist:
				del self.tasklist[taskkey]

		for _ in range(2):
			logging.debug("<=== %s 从 %s(%s) 偷取 %s(farmnum=%s) ... ",tasklogstring,self.cfgData['friends'][fuid],fuid,[x for x in self.cfgData['seedlist'] if x[1]==seedid][0][2],farmnum)
			if fuid==self.uid: # 是自己的花园
				r = self.getResponse('http://www.kaixin001.com/!house/!garden//havest.php?%s'%
					(urllib.parse.urlencode(
					{'farmnum':farmnum,'seedid':'0','fuid':'0','r':"%.16f"%(random(),),'confirm':'0'}),),
					None,**kwargs)
			else:
				r = self.getResponse('http://www.kaixin001.com/!house/!garden//havest.php?%s'%
					(urllib.parse.urlencode(
					{'farmnum':farmnum,'seedid':seedid,'fuid':fuid,'r':"%.16f"%(random(),),'confirm':'0'}),),
					None,**kwargs)
			tree = etree.fromstring(r[0])

			try:
				ret=tree.xpath('ret')[0].text
			except IndexError:
				if self.checkLimitTip(r[0]):
					return False
			else:
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
					logging.info("===> %s anti=1!!! 出现花园精灵! \n%s",tasklogstring,etree.tostring(tree,encoding='gbk').decode('gbk'))
					if self.getGardenSpiritInfo(taskkey,fuid,**kwargs):
						logging.info("%s 回答花园精灵问题成功, 再次尝试偷取...",tasklogstring)
						continue
					else:
						return False
		##			print (chr(7)*5)
					#return False

				try:
					leftnum=tree.xpath('leftnum')[0].text
					stealnum=tree.xpath('stealnum')[0].text
					num=tree.xpath('num')[0].text
					seedname=tree.xpath('seedname')[0].text
					#logging.debug("%s anti=%s,leftnum=%s,stealnum=%s,num=%s,seedname=%s",tasklogstring,anti,leftnum,stealnum,num,seedname)
					if int(stealnum)!=0:
						logging.info("===> %s *** 成功偷取 %s(%s)的 %s %s",tasklogstring,self.cfgData['friends'][fuid],fuid,stealnum,seedname)
						self.statistics[seedname]=self.statistics.get(seedname,0)+int(stealnum)
					elif fuid!=self.uid:
						logging.error("%s 只偷取 %s 个 %s",tasklogstring,stealnum,seedname)

					if fuid==self.uid: # 自己的花园
						try:
							havestnum=tree.xpath('havestnum')[0].text
						except IndexError:
							logging.info("%s havestnum not found!",tasklogstring)
							pass
						else:
							logging.info("%s 自家地块 %s 收获 %s %s",tasklogstring,farmnum,havestnum,seedname)
							if int(leftnum)==0 and oriseedid!='248': # 硬编码世博花 糟糕但省事的实现 :)
								if self.garden_plough(farmnum,taskkey):
									self.garden_plan(farmnum,taskkey)

				except IndexError:
					logging.error("===> %s 解析结果失败!!! \n%s",tasklogstring,etree.tostring(tree,encoding='gbk').decode('gbk'))
					break
				else:
					return True


		return False

	def getFriends4ranch(self):
		"""获取可偷取牧场产品的好友列表"""
		if not self.signed_in:
			self.signin()
		if self.signed_in:
			del self.friends4ranch[:]
			if not self.house_updateVerify(
				'http://www.kaixin001.com/!house/ranch/index.php',
				'var g_verify = "(.+)";',False):
				return

			r = self.getResponse('http://www.kaixin001.com/!house/!ranch/friendlist.php')
			data = json.loads(r[0].decode())

			for f in data:
				#logging.debug(u"%s  %s",f['real_name'],f['uid'])
				fname,fuid=f['real_name'],str(f['uid'])
				if f.get('antiharvest',None):
					pass
					#logging.info(u"%s(%s) 有防偷!",fname,fuid)
##				if f.get('harvest',None)==1:
				if fuid not in self.cfgData['ranchignorefriends']:
					self.friends4ranch.append((fname,fuid))
				if fuid not in self.cfgData['friends']:
					self.cfgData['friends'][fuid]=fname


	def checkRanch(self):
		logging.info("共检查%d个好友的牧场.",len(self.friends4ranch))
		p=re.compile(r'剩余数量：(?P<left>\d+)')

		cnt=0
		for fname,fuid in self.friends4ranch:
			if self.exitevent.is_set():
				logging.info("检测到退出事件")
				break

			cnt+=1
			logging.info("牧场检查 %02d) %s(%s)... ",cnt,fname,fuid)
##			r = self.getResponse('http://www.kaixin001.com/house/ranch/getconf.php',
##				{'verify':self.verify,'fuid':fuid})
			r = self.getResponse('http://www.kaixin001.com/!house/!ranch//getconf.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'fuid':fuid,'r':"%.16f"%(random(),),
				'dragon_shake':'move'}),),
				None)
			try:
				tree = etree.fromstring(r[0])
			except etree.XMLSyntaxError as e:
				logging.info("牧场 %s(%s) tree = etree.fromstring(r[0]) 出错!\n%s\n%s",fname,fuid,e,r[0].decode('utf8'))

			# 检查是否有在工作的狗狗
			try:
				dogs_name=tree.xpath('account/dogs_name')[0].text
				dogs_tips=tree.xpath('account/dogs_tips')[0].text
				if dogs_tips.find('距饥饿还有')!=-1:
					logging.info("牧场 跳过 %s(%s)！%s 在工作中(%s)!",fname,fuid,dogs_name,dogs_tips)
					continue
				elif dogs_tips.find('挨饿中')!=-1:
					logging.debug("牧场 %s(%s) %s 在挨饿中(%s).",fname,fuid,dogs_name,dogs_tips)
				else:
					logging.info("牧场 %s(%s) %s 在未知状态(%s)!",fname,fuid,dogs_name,dogs_tips)
			except IndexError:
				pass
##				logging.info("没有发现在工作的狗狗!")

			# 检查是否有在工作的巡查员
			policeetime=tree.xpath('account/policeetime')[0].text
			if policeetime:
				if policeetime.find('距这位巡查员工作结束')!=-1:
					logging.info("跳过 %s(%s)! 巡查员 在工作中(%s)",fname,fuid,policeetime)
					continue
				else:
					logging.info(" %s(%s) 巡查员在未知状态(%s)!",fname,fuid,policeetime)

			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.error("===> %s(%s) 获取牧场信息失败!!! ret=%s (%s)",fname,fuid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
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

					if skey not in self.cfgData['animallist']: # 未知副产品
						logging.info("添加未知牧场品种 %s(%s)",skey,pname)
						self.cfgData['animallist'][skey]=[int(typetext),pname]
					if self.cfgData['animallist'][skey][1]!=pname:
						logging.info("牧场品种名称不符 %s(now=%s,should=%s)",skey,self.cfgData['animallist'][skey][1],pname)


					m=re.search(p,tips)
					if m:
						left_from_tips=m.group('left')
						if tips.find('距下次可收获还有')!=-1:
							logging.debug("%s(%s) %s 已收获过! (%s)",fname,fuid,pname,tips)
							continue
						elif tips.find('好友不可收获')!=-1:
							logging.debug("%s(%s) %s 好友不可收获! (%s)",fname,fuid,pname,tips)
							continue
						n=re.search(r'再过(\d+小时)?(\d+分)?(\d+秒)?好友可收获',tips)
						if n:
							rawscd=(n.group(1) and [n.group(1)] or [''])[0]\
								+(n.group(2) and [n.group(2)] or [''])[0]\
								+(n.group(3) and [n.group(3)] or [''])[0]

							logging.info("%s(%s) %s 在防偷期, 再过 %s 可收获! (%s)",fname,fuid,pname,rawscd,tips)

							scd=self.getSleepTime(n.groups())
							if scd<self.cfgData['internal']: # 下次轮询前不需要执行则不加入定时任务
								k='ranch-%s-%s-%s'%(fuidtext,skey,typetext)
								if k in self.tasklist: # 相同的任务已经存在
									logging.info("更新前删除相同任务")
									self.tasklist[k].cancel()
									del self.tasklist[k]
								logging.info("%s(%s) 加入定时执行队列 key=%s %d (%s,%s,%s)",fname,fuid,k,scd,fuidtext,skey,typetext)
								if scd<60:
									t=Timer(scd+0.15, self.stealRanchProduct,(fuidtext,skey,typetext,k),{'nolimitspeed':True})
								else:
									t=Timer(scd,self.task_ranch,(fuidtext,skey,typetext,k))
								t.start()
								self.tasklist[k]=t

							continue
				except Exception as e:
					logging.error("%s(%s) 解析product2/item失败! (%s)(%s)",fname,fuid,e,etree.tostring(i,encoding='gbk').decode('gbk'))

				logging.debug("%s(%s) (可偷) %d/%d (%s--%d--%d--%s)",fname,fuid,num-stealnum,num,pname,num,stealnum,tips)
				reslt=self.stealRanchProduct(fuidtext,skey,typetext)

			pproduct=re.compile(r'预计产量：(\d+).+?距离可收获还有(\d+分)?(\d+秒)?')
			items=tree.xpath('animals/item')
			for i in items:
				try:
					bproduct=i.xpath('bproduct')[0].text
					if bproduct!='1':
						continue
					skey=i.xpath('skey')[0].text
					if skey not in self.cfgData['animallist']: # 未知副产品
						try:
							aname=i.xpath('aname')[0].text
							self.cfgData['animallist'][skey]=[0,aname]
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

						if skey in self.cfgData['antisteal']:
							logging.info("%s 有防偷期，不追踪.",skey)
							continue

						if scd<self.cfgData['internal']:
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
								t=Timer(scd+0.15, self.stealRanchProduct,(fuid,skey,'0',k),{'nolimitspeed':True})
								t.sleeptime=scd
							else:
								t=Timer(scd,self.task_ranch,(fuid,skey,'0',k))
								t.sleeptime=scd
							t.start()
							self.tasklist[k]=t

				except Exception as e:
					logging.info("%s(%s) 解析animals/item失败! (%s)",fname,fuid,etree.tostring(i,encoding='gbk').decode('gbk'))

	def stealRanchProduct(self,fuid,skey,typetext,taskkey='',**kwargs):
		"""steal one item 偷取一个牧场产品"""
		tasklogstring=''
		if taskkey!='':
			tasklogstring='%s'%(taskkey,)
			#logging.info(u"%s (%s,%s,%s)...",tasklogstring,fuid,skey,typetext)
			# 从tasklist中删除任务
			if taskkey in self.tasklist:
				del self.tasklist[taskkey]


		logging.debug("<=== %s (%s,%s,%s) 偷取 %s(%s) 的 %s ... ",tasklogstring,fuid,skey,typetext,self.cfgData['friends'][fuid],fuid,self.cfgData['animallist'][skey][1])
		r = self.getResponse('http://www.kaixin001.com/!house/!ranch/havest.php',
			{'verify':self.verify,'fuid':fuid,'skey':skey,'seedid':'0','id':'0','type':typetext,'foodnum':'1'},**kwargs)
		if not r[0]:
			return False
		tree = etree.fromstring(r[0])

		ret=tree.xpath('ret')[0].text
		if ret!='succ':
			reason=tree.xpath('reason')[0].text
			logging.info("===> %s !!! 偷取 %s(%s) 的 %s 失败! (%s,%s)",tasklogstring,self.cfgData['friends'][fuid],fuid,self.cfgData['animallist'][skey][1],ret,reason)
			return False

		try:
			res_ptype=tree.xpath('ptype')[0].text
			res_action=tree.xpath('action')[0].text
			res_num=tree.xpath('num')[0].text
			res_skey=tree.xpath('skey')[0].text
			logging.debug("%s action=%s,num=%s,skey=%s,ptype=%s",tasklogstring,res_action,res_num,res_skey,res_ptype)
			logging.info("===> %s *** 成功偷取 %s(%s)的 %s %s",tasklogstring,self.cfgData['friends'][fuid],fuid,res_num,self.cfgData['animallist'][res_skey][1])
			self.statistics[self.cfgData['animallist'][res_skey][1]]=self.statistics.get(self.cfgData['animallist'][res_skey][1],0)+int(res_num)
		except IndexError:
			logging.error("===> %s 解析结果失败!!! \n%s",tasklogstring,etree.tostring(tree,encoding='gbk').decode('gbk'))
			return False

		return True

	def run(self):
		try:
			#self.cafe_getDishlist()
			#input("按任意键继续...")

			# 就启动时偷一次作物
#			self.getFriends4garden()
#			self.checkGarden()
#			self.stealCrop()

			if self.cfgData['bGetGranaryInfo']:
				self.getGranaryInfo()
				#self.saveCfg()
				self.cfgData['bGetGranaryInfo']=False
				logging.info("重新设置 getgranaryinfo=False")
				input("按任意键继续...")

			if self.cfgData['bDoCafeEvent']:
				_thread.start_new_thread(self.cafe_doEvent,())

			if self.cfgData['bCheckCafe']:
				self.cafe_checkStatus()

			if self.cfgData['bStealCrop']:
				_thread.start_new_thread(self.garden_stealCrop,())

			if self.cfgData['bStealRanch']:
				_thread.start_new_thread(self.ranch_stealProduct,())

			if self.cfgData['bDoSpidermanFight']:
				_thread.start_new_thread(self.spiderman_doFight,())

			while True:
				logging.info("\n%s\n%s %d 秒后再次执行(%s) ...  %s\n%s\n",'='*75,'='*15,self.cfgData['internal'],
					(datetime.datetime.now()+datetime.timedelta(seconds=self.cfgData['internal'])).strftime("%Y-%m-%d %H:%M:%S"),
					'='*15,'='*75)
				if self.exitevent.wait(self.cfgData['internal']):
					logging.info("等待中检测到退出信号")
					if self.monitorThreadExitEventHandle is not None:
						win32event.SetEvent(self.monitorThreadExitEventHandle)
					break
				self.cafe_getChef(self.cafeid)
##				time.sleep(self.cfgData['internal'])
		except KeyboardInterrupt:
			logging.info("用户中断执行.")
			if self.monitorThreadExitEventHandle is not None:
				win32event.SetEvent(self.monitorThreadExitEventHandle)
			self.exitevent.set()

		self.saveCfg()
		self.cj.save(self.cfgData['cookiefile'])
		for k,v in self.tasklist.items():
			logging.info("删除定时任务 %s",k)
			v.cancel()
			v.join()
		self.tasklist.clear()

		for k,v in self.event4cafe.copy().items():
			logging.info("触发消费 %s 线程退出",k)
			v['exit'].set()
			v['consume'].set()
		scd=1
		while len(self.event4cafe)!=0:
			logging.info("等待 %d 秒 ...",scd)
			time.sleep(scd)
			scd+=1
			if scd>6:break

		self.pool.exit()

		logging.info("网络访问次数: %d",sum(self.cfgData['statistics4WebAccessData'].values()))
		if len(self.cfgData['statistics4WebAccessData'])!=0:
			logging.info("访问分类统计:\n%s",'\n'.join( ("%s: %d"%(k,v) for k,v in self.cfgData['statistics4WebAccessData'].items() ) ) )

		if len(self.statistics)!=0:
			logging.info("统计: %s",'\t'.join( ("%s: %d"%(k,v) for k,v in self.statistics.items() ) ) )
			self.statistics.close()

		logging.info("执行完毕.")
		if __name__=='__main__':
			time.sleep(1)

	def getValueItems(self,threshold_value):
		"""从l挑出价值大于 threshold_value 或者是强制偷取的 的 item 以列表形式返回。
		对自己的花园作物不做处理。以oriseed为基准比较（即只比较原种类而不比较变异后的种类）
		"""
		ret=[]
		# 自己的花园作物不参与比较，先取出
		my_crops2steal=[i for i in self.crops2steal if i[3]==self.uid ]
		if my_crops2steal:
			logging.info("自己的：%s",my_crops2steal)
			self.crops2steal=[i for i in self.crops2steal if i[3]!=self.uid]
			logging.info("其他的：%s",self.crops2steal)



		# 从seedlist中选出价值不低于threshold的seedid的列表
		threshold_list=[i[1] for i in self.cfgData['seedlist'] if i[0]>=threshold_value]
		# 将强制要偷的seedid加入
		for i in self.cfgData['forcestealseeds']:
			if i not in threshold_list:
				threshold_list.append(i)

		# 从上一步结果中选出包含在可偷列表中的seed
		threshold_list=[x for x in threshold_list if x in [i[2] for i in self.crops2steal]]

		for i in threshold_list:
			t=[item for item in self.crops2steal if item[2]==i]
			ret+=t

		# 将自己的花园作物原样放入结果
		if my_crops2steal:
			ret+=my_crops2steal
			logging.info("过滤并合并后的：%s",ret)

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
##				time.sleep(1)
				try:
					seedid=i.xpath('seedid')[0].text
					num=i.xpath('num')[0].text
					name=i.xpath('name')[0].text
					logging.debug("seedid=%s,name=%s,num=%s",seedid,name,num)
					self.getGardenFruitInfo(seedid)
				except IndexError:
					logging.error("===>解析植物产品信息失败!!! \n%s",etree.tostring(i,encoding='gbk').decode('gbk'))


			r = self.getResponse('http://www.kaixin001.com/app/app.php?aid=1062&url=ranch/index.php')
			m = re.search('var g_verify = "(.+)";', r[0].decode())
			self.verify = m.group(1)
			logging.info("verify=%s",self.verify)

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
##				time.sleep(1)
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
				try:
					jtitle=tree.xpath('jtitle')[0].text
					if jtitle:
						lohas=tree.xpath('lohas')[0].text
						jprice=tree.xpath('jprice')[0].text
						jratio=tree.xpath('jratio')[0].text
						logging.debug("name=%s,fruitnum=%s,fruitprice=%s,jtitle=%s,lohas=%s,jprice=%s,jratio=%s",name,fruitnum,fruitprice,jtitle,lohas,jprice,jratio)
					else:
						logging.debug("name=%s,fruitnum=%s,fruitprice=%s",name,fruitnum,fruitprice)
				except IndexError:
					pass

				try:
					old=[x for x in self.cfgData['seedlist'] if x[1]==seedid][0]
					if old:
						oldprice=old[0]
						if oldprice!=int(fruitprice):
							old[0]=int(fruitprice)
							logging.info("更新作物信息 [%d,%s,%s] 到 [%d,%s,%s].",oldprice,old[1],old[2],old[0],old[1],old[2])
				except IndexError:
					logging.info("添加未知作物 [%s,%s,%s]!",fruitprice,seedid,name)
					self.cfgData['seedlist'].append([int(fruitprice),seedid,name])
				except Exception as e:
					logging.error("===>更新作物信息失败!!! \n%s",e)
			except IndexError:
				logging.error("===>解析仓库信息失败!!! \n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

		return True

	def saveCfg(self):
		"""更新配置文件"""
		logging.info("更新配置文件")
		seedlist=copy.copy(self.cfgData['seedlist'])
		seedlist.sort(key=lambda x:int(x[1]))
		seedlist=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(seedlist)
		seedlist=seedlist.replace(',[',',\n[') # 一个item占一行便于手工编辑
		self.cfg.set('account','seedlist',seedlist)

		antisteal=copy.copy(self.cfgData['antisteal'])
		antisteal.sort()
		antisteal=json.JSONEncoder(ensure_ascii=False,separators=(',', ':')).encode(antisteal)
		antisteal=antisteal.replace(',"',',\n"') # 一个item占一行便于手工编辑
		self.cfg.set('account','antisteal',antisteal)

		friends=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.cfgData['friends'])
		self.cfg.set('account','friends',friends)

		animallist=copy.copy(self.cfgData['animallist'])
		animallist=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(animallist)
		animallist=animallist.replace('],"','],\n"') # 一个item占一行便于手工编辑
		self.cfg.set('account','animallist',animallist)

		self.cfg.set('account','getgranaryinfo',str(self.cfgData['bGetGranaryInfo']))

		statistics4WebAccessData=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.cfgData['statistics4WebAccessData'])
		statistics4WebAccessData=statistics4WebAccessData.replace(',"',',\n"')
		self.cfg.set('stat-%s'%(self.rundate,),'statisticswebaccess',statistics4WebAccessData)
		self.cfg.set('stat-%s'%(self.rundate,),'webaccesscnt',str(sum(self.cfgData['statistics4WebAccessData'].values())))

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
		logging.info("任务 %s 检查 %s(%s) (%s,%s,%s)... ",task_key,self.cfgData['friends'][i_fuid],i_fuid,i_fuid,i_skey,i_typetext)
##		r = self.getResponse('http://www.kaixin001.com/house/ranch/getconf.php',
##			{'verify':self.verify,'fuid':i_fuid})
		r = self.getResponse('http://www.kaixin001.com/!house/!ranch//getconf.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.verify,'fuid':i_fuid,'r':"%.16f"%(random(),),
				'dragon_shake':'move'}),),
				None,nolimitspeed=True)
		try:
			tree = etree.fromstring(r[0])
		except etree.XMLSyntaxError as e:
			logging.debug("任务 %s 文档化返回数据时发生异常: %s\n%s",task_key,e,r[0].decode('utf-8'))
			return

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
			if skey in self.cfgData['antisteal']:
				scd=0.05
				#trycnt=10
			for i in range(trycnt):
				reslt=self.stealRanchProduct(fuidtext,skey,typetext,task_key,nolimitspeed=True)
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
			if skey in self.cfgData['antisteal']:
				scd=0.05
				trycnt=10
			for i in range(trycnt):
				reslt=self.stealRanchProduct(i_fuid,skey,i_typetext,task_key,nolimitspeed=True)
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

		logging.info("%s 检查 %s(%s) 地块 %s 的 %s(%s)  ... ",task_key,self.cfgData['friends'][i_fuid],i_fuid,i_farmnum,list(filter(lambda x: x[1]==i_seedid,self.cfgData['seedlist']))[0][2],i_seedid)
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
#				logging.debug("地块 %s 已经收获光未犁地",farmnum)
				continue

			logging.info("地块 %s cropsstatus=%s",farmnum,cropsstatus)

			name=i.xpath('name')[0].text
			crops=i.xpath('crops')[0].text
			seedid=i.xpath('seedid')[0].text
			if seedid!=i_seedid:
				logging.exception("%s 与预期的seedid不符! (%s!=%s)",task_key,seedid,i_seedid)
			oriseedid=i.xpath('oriseedid')[0].text

			# 检查seedid是否是未知的
			if seedid not in [x[1] for x in self.cfgData['seedlist']]: # 未知
				self.cfgData['seedlist'].append([4321,seedid,name])
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
						rslt=self.stealOneCrop(farmnum,seedid,oriseedid,i_fuid,task_key,nolimitspeed=True)
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
			for trycnt in range(3):
				r = self.getResponse('http://www.kaixin001.com/!house/!ranch/myfruitinfo.php',
					{'verify':self.verify,'type':i_type,'id':i_id})
				logging.debug("%s %s myfruitinfo:%s",i_type,i_id,r[0].decode('utf8'))
				try:
					tree = etree.fromstring(r[0])
				except etree.XMLSyntaxError as e:
					logging.info("tree = etree.fromstring(r[0]) 出错!\n%s",e)
					continue
				else:
					break

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
					k=[x for x in self.cfgData['animallist'] if self.cfgData['animallist'][x][0]==int(i_id)][0]
					if k:
						pass
						#old_name=self.cfgData['animallist'][k][1]
						#if old_name!=name:
							#logging.info(u"更新动物产品信息 %s=[%s,%s] 到 %s=[%s,%s].",k,self.cfgData['animallist'][k][0],old_name,k,self.cfgData['animallist'][k][0],self.cfgData['animallist'][k][1])
							#self.cfgData['animallist'][k][1]=name
				except IndexError:
					try:
						k=[x for x in self.cfgData['animallist'] if self.cfgData['animallist'][x][1]==name][0]
						old=self.cfgData['animallist'][k][0]
						self.cfgData['animallist'][k][0]=int(i_id)
						logging.info("更新动物产品信息 key=%s [%d,%s] => [%d,%s]!",k,old,name,self.cfgData['animallist'][k][0],name)
					except IndexError:
						logging.info("未知动物产品 [%s,%s]!",i_id,name)
				except Exception as e:
					logging.error("===>更新动物产品信息失败!!! \n%s",e)
			except IndexError:
				logging.error("===>解析仓库动物产品信息失败!!! \n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

		return True


	def stealHoney(self,fuid):
		"""偷蜂蜜"""
		logging.info("<=== 从 %s(%s) 偷取蜂蜜 ...",self.cfgData['friends'][fuid],fuid)
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
			logging.info("===> *** 成功偷取 %s(%s)的 %s 蜂蜜~ (%s)",self.cfgData['friends'][fuid],fuid,count,etree.tostring(tree,encoding='gbk').decode('gbk'))
		except IndexError:
			logging.error("===> 解析结果失败!!! \n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

		return True

	def statisticsWebAccess(self,url):
		"""根据url统计访问数据"""
		k=url.replace('http://www.kaixin001.com/','')
		idx=k.find('?')
		if idx!=-1: # 有?，说明有GET参数，需要去掉
			k=k[:idx]

		with self.semaphore4accessCnt:
			if self.rundate!=time.strftime('%Y%m%d'): # 新的一天
				logging.info("%s 新的一天!",time.strftime('%Y%m%d'))
				# 现有数据保存做为上一天的数据
				statistics4WebAccessData=json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.cfgData['statistics4WebAccessData'])
				statistics4WebAccessData=statistics4WebAccessData.replace(',"',',\n"')
				self.cfg.set('stat-%s'%(self.rundate,),'statisticswebaccess',statistics4WebAccessData)
				self.cfg.set('stat-%s'%(self.rundate,),'webaccesscnt',str(sum(self.cfgData['statistics4WebAccessData'].values())))
				# 更新日期
				self.rundate=time.strftime('%Y%m%d')
				# 取可能已有的数据
				statistics4WebAccessData=None
				try:
					statistics4WebAccessData=self.cfg.get('stat-%s'%(self.rundate,),'statisticswebaccess')
				except configparser.NoSectionError:
					self.cfg.add_section('stat-%s'%(self.rundate,))
				except configparser.NoOptionError:
					pass

				if statistics4WebAccessData:
					logging.info("在原有 %s 统计数据基础上继续统计.",self.rundate)
					self.cfgData['statistics4WebAccessData']=json.JSONDecoder().decode(statistics4WebAccessData)
				else:
					logging.info("无 %s 统计数据, 开始全新统计.",self.rundate)
					self.cfgData['statistics4WebAccessData']={}

				if self.consumeerrcnt<=0:
					self.consumeerrcnt=50
					self.consumepertime=500

			value=self.cfgData['statistics4WebAccessData'].get(k,0)
			self.cfgData['statistics4WebAccessData'][k]=value+1
##			logging.debug("统计: %s=%d",k,self.cfgData['statistics4WebAccessData'][k])

		self.switchModeOperation()

	@threadpool_wrapfunc
	def getResponse(self,url,data=None,**kwargs):
		"""获得请求url的响应"""
		res,rurl=None,None
		for i in range(3): # 尝试3次
			if i!=0:
				logging.info("第 %d 次尝试...",i+1)
			try:
##				logging.debug("访问 %s",url)
				r = self.opener.open(
					urllib.request.Request(url,urllib.parse.urlencode(data) if data else None),
					timeout=30)
				res=r.read()
				rurl=r.geturl()
				self.statisticsWebAccess(url)
				break
			except socket.gaierror as e:
				logging.info("获取地址失败! %s",e)
			except urllib.error.HTTPError as e:
				logging.info("请求出错！ %s",e)
			except urllib.error.URLError as e:
				logging.info("访问地址 %s 失败! %s",url,e)
			except IOError as e:
				logging.info("IO错误! %s",e)
			except Exception as e:
				logging.info("未知错误! %s",e)
				raise

		return (res,rurl)


	def getFishinfo(self):
		'''获取鱼苗信息'''
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
		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False

		if not self.cafe_updateVerify(False):
			return False

		task_key='cafe_doEvent'

		while True:
			logging.info("%s 查看餐厅是否需要帮助...",task_key)

			r = self.getResponse('http://www.kaixin001.com/cafe/api_friendlist.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.cafeverify,'rand':"%.16f"%(random(),)}),),
				None)
			tree = etree.fromstring(r[0])

			items=tree.xpath('item')
	##		logging.debug("%s items=%d",task_key,len(items))
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
						{'verify':self.cafeverify,'uid':fuid,'r':"%.16f"%(random(),)}),),
						None)
					tree = etree.fromstring(r[0])
	##				logging.debug("===> api_userevent返回: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
					title=tree.xpath('title')[0].text
					logging.info("%s %s(%s) 需要帮助: %s",task_key,fname,fuid,title)

					r = self.getResponse('http://www.kaixin001.com/cafe/api_doevent.php?%s'%
						(urllib.parse.urlencode(
						{'verify':self.cafeverify,'uid':fuid,'ret':1}),),
						None)
					tree = etree.fromstring(r[0])
	##				logging.debug("===> api_doevent返回: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
					try:
						addmycash=tree.xpath('addmycash')[0].text
						addmyevalue=tree.xpath('addmyevalue')[0].text
						logging.info("===> %s 因为帮助 %s(%s)，现金+%s 经验+%s",task_key,fname,fuid,addmycash,addmyevalue)
					except IndexError:
						logging.debug("解析帮忙结果失败!\n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

##					time.sleep(3)

			logging.info("%d 秒后再次执行餐厅帮助线程(%s)",self.cfgData['internal4cafeDoEvent'],
				(datetime.datetime.now()+datetime.timedelta(seconds=self.cfgData['internal4cafeDoEvent'])).strftime("%Y-%m-%d %H:%M:%S"))
			if self.exitevent.wait(self.cfgData['internal4cafeDoEvent']):
				logging.info("%s 检测到退出信号",task_key)
				break


	def cafe_stoveclean(self,cafeid,orderid,task_key=''):
		logging.debug("%s 灶台 %s 需要清洁",task_key,orderid)
		for i in range(3):
			if self.exitevent.is_set():
				logging.info("检测到退出事件")
				break
			# 清洗灶台
			r = self.getResponse('http://www.kaixin001.com/cafe/api_stoveclean.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.cafeverify,'cafeid':cafeid,'orderid':orderid,'rand':"%.16f"%(random(),)}),),
				None)
			try:
				tree=etree.fromstring(r[0])
			except etree.XMLSyntaxError as e:
				logging.info("tree=etree.fromstring(r[0]) 出错!\n%s\n%s",e,r[0].decode('utf8'))
				self.cafe_updateVerify()
				continue

	##		logging.debug("===> %s api_stoveclean返回: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))
			try:
				ret=tree.xpath('ret')[0].text
			except IndexError as e:
				logging.info("获取返回信息时发生异常!\n%s\n%s",e,etree.tostring(tree,encoding='gbk').decode('gbk'))
				if self.checkLimitTip(r[0]):
					break
			else:
				if ret!='succ':
					logging.info("===> %s 清洁灶台 %s 失败!\n%s",task_key,orderid,etree.tostring(tree,encoding='gbk').decode('gbk'))
					break

				addcash=tree.xpath('addcash')[0].text
				addevalue=tree.xpath('addevalue')[0].text
##				logging.info("===> %s 清洁灶台 %s 成功, 现金 %s  经验 +%s",task_key,orderid,addcash,addevalue)
				logging.info("===> %s 清洁灶台, 现金 %s  经验 +%s",task_key,addcash,addevalue)
				return True

		return False

	def cafe_dish2counter(self,cafeid,orderid,name,task_key=''):
		logging.debug("%s 将 灶台 %s 的 %s 端到餐台...",task_key,orderid,name)
		# 端到餐台
		r = self.getResponse('http://www.kaixin001.com/cafe/api_dish2counter.php?%s'%
	    (urllib.parse.urlencode(
	    {'verify':self.cafeverify,'cafeid':cafeid,'orderid':orderid,'rand':"%.16f"%(random(),)}),),
	    None)
		tree = etree.fromstring(r[0])
##		logging.debug("===> %s api_dish2counter 返回: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))

		try:
			ret=tree.xpath('ret')[0].text
		except IndexError:
			if self.checkLimitTip(r[0]):
				return False
		else:
			if ret=='succ':
				try:
					orderid=tree.xpath('orderid')[0].text
					torderid=tree.xpath('torderid')[0].text
					addevalue=tree.xpath('addevalue')[0].text
					foodnum=tree.xpath('foodnum')[0].text
					evalue=tree.xpath('account/evalue')[0].text
##					logging.info("===> %s 成功将 %s 从灶台 %s -->餐台 %s, 现在餐台上数量 %s 经验 %s(+%s)",
##						task_key,name,orderid,torderid,foodnum,evalue,addevalue)
					logging.info("===> %s 端菜到餐台 %s (%s), 经验 %s(+%s)",
						task_key,torderid,foodnum,evalue,addevalue)
				except IndexError:
					logging.info("解析 orderid/torderid/addevalue/foodnum/evalue时失败！\n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))
				else:
					if int(foodnum)>=self.consumepertime: # 大于消费阀值才触发消费
						self.event4cafe[torderid]['consume'].set()
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

		if not self.cafe_updateVerify(False):
			return False

		for _ in range(2): # 出错时重试一次
			r = self.getResponse('http://www.kaixin001.com/cafe/api_getconf.php?%s'%
				(urllib.parse.urlencode(
				{'verify':self.cafeverify,'rand':"%.16f"%(random(),),'loading':1}),),
				None)
			try:
				tree=etree.fromstring(r[0])
#				with codecs.open(r'd:\conf-%s.xml'%(self.cfgData['logsuffix'],),'w','utf-8-sig') as f:
#					f.write(r[0].decode())
			except etree.XMLSyntaxError as e:
				logging.info("tree = etree.fromstring(r[0]) 出错!\n%s\n%s",e,r[0].decode('utf8'))
				self.cafe_updateVerify()
				continue
			else:
				cash=tree.xpath('account/cash')[0].text
				goldnum=tree.xpath('account/goldnum')[0].text
				evalue=tree.xpath('account/evalue')[0].text
				logging.info("现金/金币/经验: %s/%s/%s",cash,goldnum,evalue)
				cafeid=tree.xpath('cafe/cafeid')[0].text
				pvalue=tree.xpath('cafe/pvalue')[0].text
				cafewidth=tree.xpath('cafe/cafewidth')[0].text
				cafeheight=tree.xpath('cafe/cafeheight')[0].text
				logging.info("餐厅id=%s 魅力=%.1f 面积=%s×%s",cafeid,int(pvalue)/100.0,cafewidth,cafeheight)
				self.cafeid=cafeid

				self.cafe_getChef(self.cafeid)

				# 餐台
				logging.info("查看餐台...")
				dishs=tree.xpath('dish/item')
				for i,item in enumerate(dishs):
					orderid=item.xpath('orderid')[0].text

					# 建立对应的消费线程
					if orderid not in self.event4cafe:
						self.event4cafe[orderid]=Event()
						self.event4cafe[orderid]={
							'consume':Event(),
							'exit':Event()}
						_thread.start_new_thread(self.cafe_dish2customer,(cafeid,orderid,'table-%02d'%(i+1,)))

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
					if int(num)>self.consumepertime:
						self.event4cafe[orderid]['consume'].set() # 触发消费
		##			logging.debug("餐台信息: %s\n",etree.tostring(item,encoding='gbk').decode('gbk'))


				# 灶台
				if self.cfgData['bDoCooking']:
					logging.info("查看灶台...")
					cookings=tree.xpath('cooking/item')
					waittime=0
					for i,item in enumerate(cookings):
						orderid=item.xpath('orderid')[0].text
						logging.info("%d/%d) 灶台 %s ...",i+1,len(cookings),orderid)
						try:
							stage=item.xpath('stage')[0].text
						except IndexError:
							logging.info("灶台 %s 是空的",orderid)
						else:
							if stage=='1':
								autotime=item.xpath('autotime')[0].text
								timeleft=-int(autotime)
								strCur=''
								try:
									dish_name=item.xpath('name')[0].text
									dishid=item.xpath('dishid')[0].text
									progress=item.xpath('auto/item')
									for ele in progress:
										a_htime=ele.xpath('htime')[0].text
										timeleft+=int(a_htime)
										if timeleft>0 and strCur=='':
											a_stage=ele.xpath('stage')[0].text
											a_step=ele.xpath('step')[0].text
											a_name=ele.xpath('name')[0].text
											strCur="当前: %s.%s: %s(%ss)"%(a_stage,a_step,a_name,a_htime)
									logging.debug("灶台 %s 在做 %s(%s), %s 剩余时间%ds",orderid,dish_name,dishid,strCur,timeleft)
									waittime=int(timeleft)
								except IndexError:
									logging.info("获取灶台 %s 的等待时间时出错! ",orderid)


						k='cafe-%02d-%s'%(i+1,orderid)
						#if k not in self.tasklist:
						logging.info("添加灶台线程 %s, 初始等待时间 %d 秒.",k,waittime)
							#self.tasklist[k]=Timer(waittime, self.task_cafe,(cafeid,orderid,'cafe-%02d'%(i+1,)))
							#self.tasklist[k].setName('灶台-%02d-%s'%(i+1,orderid))
							#self.tasklist[k].start()
						_thread.start_new_thread(self.task_cafe,(cafeid,orderid,'cafe-%02d'%(i+1,),waittime))
						#t=Timer(waittime, self.task_cafe,(cafeid,orderid,'cafe-%02d'%(i+1,)))
						#t.start()
						waittime=0
				else:
					logging.info("根据配置, 不查看灶台不做菜.")

				break

			return True

	def cafe_dish2customer(self,cafeid,orderid,task_key=''):
		logging.info("建立 消费 %s 线程",orderid)
		pernum=self.consumepertime
		pernum=50

		leftnum='0'
		tm=None
		while True:
			if self.event4cafe[orderid]['exit'].is_set():
				logging.info("退出 消费 %s 线程",orderid)
				del self.event4cafe[orderid]
				break
			self.event4cafe[orderid]['consume'].wait(tm)
			if self.event4cafe[orderid]['exit'].is_set():
				logging.info("退出 消费 %s 线程",orderid)
				del self.event4cafe[orderid]
				break

			# 开始消费
			while True:
				r = self.getResponse('http://www.kaixin001.com/cafe/api_dish2customer.php?%s'%
			    (urllib.parse.urlencode(
			    {'verify':self.cafeverify,
						'cafeid':cafeid,
						'orderid':orderid,
						'num':pernum,
						'rand':"%.16f"%(random(),)}),),
			    None)
				tree=etree.fromstring(r[0])
##				logging.debug("===> api_dish2customer 返回: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
				ret=tree.xpath('ret')[0].text
				if ret!='succ':
					logging.info("%s 消费餐台 %s 出错(%s)\n%s",
				    task_key,orderid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))

					try:
						msg=tree.xpath('msg')[0].text
					except IndexError:
						pass
					else:
						if msg.find('超出送菜次数限制')!=-1:
							logging.info("超出送菜次数限制! 停止送菜")
							self.consumepertime=5000000 # 设成大数以避免被灶台线程触发
							tm=None
							break


					self.consumeerrcnt-=1
					if self.consumeerrcnt<=0:
						logging.info("到达送菜最大出错次数,停止送菜!")
						self.consumepertime=5000000 # 设成大数以避免被灶台线程触发
						tm=None
					elif int(leftnum)>pernum:
						leftnum='0'
						tm=120 # 稍后再试


					break
				oid=tree.xpath('orderid')[0].text
				assert oid==orderid
				pvalue=tree.xpath('pvalue')[0].text
				cash=tree.xpath('account/cash')[0].text
				addcash=tree.xpath('addcash')[0].text
				foodnum=tree.xpath('foodnum')[0].text
				leftnum=tree.xpath('leftnum')[0].text
	##			customernum=tree.xpath('customernum')[0].text
				customernum=tree.xpath('customernum')[0].text
##				logging.info("===> %s 餐台 %s, %s->%s, 现金 %s(+%s), 魅力 %.1f",
##			    task_key,orderid,foodnum,leftnum,cash,addcash,int(pvalue)/100.0)
				logging.info("===> %s %s->%s, 现金 %s(+%s), 魅力 %.1f",
			    task_key,foodnum,leftnum,cash,addcash,int(pvalue)/100.0)

				if int(leftnum)<pernum :
					tm=None
##					logging.info("%s 剩余数量<每次最小消费数(%d<%d)",task_key,int(leftnum),pernum)
					break
				if self.event4cafe[orderid]['exit'].is_set():
					break
##				self.exitevent.wait(5)

			self.event4cafe[orderid]['consume'].clear()

		return True

	def task_cafe(self,cafeid,orderid,task_key,initsleeptime=0):
		'''
				-3 需要清洁
				-2 被收购 需要清洁
				-1 坏菜 需要清洁
				0 在做
				1 耗时操作中
				2 做好了
		'''
		logging.debug("%s 灶台线程 %s 创建, 初始等待时间: %d 秒.",task_key,orderid,initsleeptime)
##		if not self.signed_in:
##			self.signin()
##			if not self.signed_in:
##				return False

		waittime=initsleeptime
		while True:
			if self.exitevent.wait(waittime):	# 退出信号有效
				logging.info("%s 检测到退出信号",task_key)
				break
			waittime=30
			logging.debug("%s 检查灶台 %s ... ",task_key,orderid)

			r = self.getResponse('http://www.kaixin001.com/cafe/api_checkfood.php?%s'%
		    (urllib.parse.urlencode(
		    {'verify':self.cafeverify,'cafeid':cafeid,'orderid':orderid,'rand':"%.16f"%(random(),)}),),
		    None)
			try:
				tree = etree.fromstring(r[0])
			except etree.XMLSyntaxError as e:
				logging.info("tree=etree.fromstring(r[0]) 出错!\n%s",e)
				if self.cafe_updateVerify():
					waittime=5
				else:
					waittime=120
			else:
				try:
					ret=tree.xpath('ret')[0].text
				except IndexError:
					logging.debug("获取 ret 值失败!\n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))
					if self.checkLimitTip(r[0]):
						waittime=2
					else:
						waittime=60
				else:
					if ret!='succ':
						logging.debug("===> %s 获取灶台 %s 信息失败!!! ret=%s (%s)",
							task_key,orderid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))

					if ret=='fail':
						msg=tree.xpath('msg')[0].text
						if msg=='准备阶段' or msg=='还没有烹饪':
							logging.debug("%s 灶台 %s 在准备阶段 or 还没有烹饪?",task_key,orderid)
							stage='0'
						else:
							continue
					else:
						stage=tree.xpath('stage')[0].text
						oid=tree.xpath('orderid')[0].text

					#logging.info("获取 ret 值 \n%s",etree.tostring(tree,encoding='gbk').decode('gbk'))

					if stage=='0': # 在做
						logging.debug("%s 灶台 %s 准备下一步(%s)",task_key,orderid,stage)
						ret=self.cafe_cooking(cafeid,orderid,self.cfgData['dish2cook'],task_key)
						if ret[0]==True:
							waittime=ret[1]

					elif stage=='-1' or stage=='-2' or stage=='-3': # 需要清洁
						if stage=='-1': # 尝试恢复坏菜
							if self.cafe_recoverfood(cafeid,orderid,task_key):
								self.cafe_dish2counter(cafeid,orderid,'xxxx',task_key)

						logging.debug("%s 灶台 %s 需要清洁(%s)",task_key,orderid,stage)
						if self.cafe_stoveclean(cafeid,orderid,task_key):
							ret=self.cafe_cooking(cafeid,orderid,self.cfgData['dish2cook'],task_key)
							if ret[0]==True:
								waittime=ret[1]

					elif stage=='1': # 耗时操作中
						logging.debug("%s 灶台 %s 还在做(%s)\n%s",task_key,orderid,stage,etree.tostring(tree,encoding='gbk').decode('gbk'))
						waittime=60

					elif stage=='2': # 做好了
						logging.debug("%s 灶台 %s 做好了(%s)",task_key,orderid,stage)
			##			logging.info("%s 灶台 %s 做好了(%s) %s",task_key,orderid,stage,etree.tostring(tree,encoding='gbk').decode('gbk'))
						if self.cafe_dish2counter(cafeid,orderid,'xxxx',task_key)	and self.cafe_stoveclean(cafeid,orderid,task_key):
							ret=self.cafe_cooking(cafeid,orderid,self.cfgData['dish2cook'],task_key)
							if ret[0]==True:
								waittime=ret[1]
					else:
						logging.info("===>%s 灶台 %s 的状态未知(%s)!!! ret=%s (%s)",task_key,orderid,stage,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
						waittime=300


		return

	def cafe_updateVerify(self,force=True):
		logging.debug("更新cafeverify, force=%s",force)

		if (not force) and self.cafeverify:
			logging.debug("cafeverify已存在，无需更新")
			return True

		r=self.getResponse('http://www.kaixin001.com/!cafe/index.php')
		m = re.search('verify=(.+?)&', r[0].decode())
		if m:
			logging.debug("cafeverify=%s",m.group(1))
			self.cafeverify = m.group(1)
		else:
			logging.info("更新 cafeverify 失败! \n%s",r[0].decode())
			self.checkLimitTip(r[0])
			return False
		return True


	def cafe_cooking(self,cafeid,orderid,dishid,task_key=''):
		'''做菜 cafeid=餐厅id orderid=灶台id dishid=菜名id
		返回值 (True/False,None/\d+)
		第一个值代表是否做菜成功，如果成功则第二个值代表多少秒后菜将做好
		'''
		logging.debug("%s 尝试在灶台 %s 上做 %s ...",task_key,orderid,dishid)
		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False,None

		bUseMana=False # 标识是否使用了大厨
		for i in range(9):
			if self.exitevent.is_set():
				logging.info("检测到退出事件")
				return False,None
##			logging.info("第 %d 次 ...",i+1)

			with self.semaphore4cafemana:
				#logging.debug("%s cafemana=%d",task_key,self.cafemana)
				if self.cafemana>0: # 大厨有体力则自动做菜
					urldata={'verify':self.cafeverify,
						'cafeid':cafeid,
						'orderid':orderid,
						'dishid':dishid,
						'auto':1, # 自动做菜（法国大厨？）
						'rand':"%.16f"%(random(),)}
					bUseMana=True
				else:
					urldata={'verify':self.cafeverify,
						'cafeid':cafeid,
						'orderid':orderid,
						'dishid':dishid,
						'rand':"%.16f"%(random(),)}
					bUseMana=False

			r = self.getResponse('http://www.kaixin001.com/cafe/api_cooking.php?%s'%
				(urllib.parse.urlencode(urldata),),
				None)
			try:
				tree=etree.fromstring(r[0])
			except etree.XMLSyntaxError as e:
				logging.info("tree=etree.fromstring(r[0]) 出错!\n%s",e)
				if self.cafe_updateVerify():
					continue
				else:
					break
##			logging.debug("===> %s api_cooking: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))
			try:
				ret=tree.xpath('ret')[0].text
			except IndexError:
				if self.checkLimitTip(r[0]):
					continue
			else:
				if bUseMana:
					with self.semaphore4cafemana:
						self.cafemana-=1 # 大厨体力减少
						logging.debug("%s cafemana=%d",task_key,self.cafemana)

				if ret!='succ':
##					logging.info("===> %s 灶台 %s 上做菜失败(%s)!\n%s",
##						task_key,orderid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
					logging.info("===> %s 上做菜失败(%s)!\n%s",
						task_key,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
					self.exitevent.wait(60)
					continue

			try:
				dish_name=tree.xpath('dish/name')[0].text
				stage=tree.xpath('dish/stage')[0].text
			except IndexError:
				logging.info("%s 解析dish/name 和 dish/stage时失败!\n%s",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))
##				if not self.cafe_updateVerify():
##					return False
##				continue
				return False,None
			if stage!='1':
				step_name=tree.xpath('dish/stepname')[0].text
				tips=tree.xpath('dish/tips/tips')[0].text
				logging.debug("%s 灶台 %s %s/%s, 下一步: %s",task_key,orderid,step_name,dish_name,tips)
##				self.exitevent.wait(3)
				continue

##			logging.debug("%s 灶台 %s 菜名 %s 进入耗时阶段(%s) \n%s",
##				task_key,orderid,dish_name,stage,etree.tostring(tree,encoding='gbk').decode('gbk'))

			autotime=tree.xpath('dish/autotime')[0].text # 进入自动阶段,开始计时
			timeleft=-int(autotime)
			strCur=''
			try:
				autoitems=tree.xpath('dish/auto/item')
				for item in autoitems:
					a_htime=item.xpath('htime')[0].text
					timeleft+=int(a_htime)
					if timeleft>0 and strCur=='':
						a_stage=item.xpath('stage')[0].text
						a_step=item.xpath('step')[0].text
						a_name=item.xpath('name')[0].text
						strCur="当前: %s.%s: %s(%ss)"%(a_stage,a_step,a_name,a_htime)
##					logging.debug("%s 灶台 %s 后续: %s.%s: %s(%ss)",task_key,orderid,a_stage,a_step,a_name,a_htime)
##				logging.info("===> %s 灶台 %s 在做 %s(%s), %s 剩余时间%ds",task_key,orderid,dish_name,dishid,strCur,timeleft)
				logging.info("===> %s 在做 %s(%s), %s 剩余时间%ds",task_key,dish_name,dishid,strCur,timeleft)
				return True,timeleft+1
			except IndexError:
				logging.info("%s 不包含 auto/item 信息或者解析失败! ",task_key)

			break

		return False,None

	def cafe_recoverfood(self,cafeid,orderid,task_key=''):
		logging.debug("%s 灶台 %s 尝试恢复坏菜",task_key,orderid)
		p=re.compile(r'''<div id="maincontent">\n<\?xml version="1.0" encoding="UTF-8" \?>\n(.+?)<!-- module end --></div>''')

		for i in range(3):
			if self.exitevent.is_set():
				logging.info("检测到退出事件")
				break
			# 恢复坏菜
			r = self.getResponse('http://www.kaixin001.com/!cafe/api_recoverfood.php?%s'%
				(urllib.parse.urlencode(
					{'verify':self.cafeverify,'cafeid':cafeid,'uid': self.uid,'orderid':orderid,'rand':"%.16f"%(random(),)}),),
				None)

			m=p.search(r[0].decode())
			if not m:
				logging.info("获取恢复坏菜的返回信息时失败! %s",r[0].decode('utf8'))
				break

			try:
				tree=etree.fromstring(m.group(1))
			except etree.XMLSyntaxError as e:
				#logging.info("tree=etree.fromstring(r[0]) 出错!\n%s\n%s",e,r[0].decode('utf8'))
				logging.info("tree=etree.fromstring(r[0]) 出错!\n%s\n%s",e,m.group(1))
				self.cafe_updateVerify()
				continue

			#logging.debug("===> %s api_recoverfood返回: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))
			try:
				ret=tree.xpath('ret')[0].text
			except IndexError as e:
				logging.info("获取返回信息时发生异常!\n%s\n%s",e,etree.tostring(tree,encoding='gbk').decode('gbk'))
				if self.checkLimitTip(r[0]):
					break
			else:
				if ret!='succ':
					logging.info("===> %s 恢复坏菜 %s 失败!\n%s",task_key,orderid,etree.tostring(tree,encoding='gbk').decode('gbk'))
					break
				dname=tree.xpath('dish/name')[0].text
				stage=tree.xpath('stage')[0].text
##				logging.info("===> %s 恢复坏菜 %s %s 成功,stage=%s",task_key,orderid,dname,stage)
				logging.info("===> %s 恢复坏菜 %s 成功, stage=%s",task_key,dname,stage)
				return True

		return False

	def cafe_getDishlist(self):
		logging.info("获取菜谱 ... ")
		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False

		ptag=re.compile('(<.*?>)',re.M|re.U|re.S) # 过滤html的tag
		pchinese=re.compile('([\u4e00-\u9fa5]+)+?') # 过滤中文

		if not self.cafe_updateVerify():
			return False

		sortedlist=[]
		s=StringIO()
		pageno=0
		bnext='1'
		while bnext=='1':
			r = self.getResponse('http://www.kaixin001.com/cafe/api_dishlist.php?%s'%
				(urllib.parse.urlencode(
					{'verify':self.cafeverify,'page':pageno,'r':"%.16f"%(random(),),'flag':1}),),
				None)
			tree=etree.fromstring(r[0])
##			logging.debug("===> api_dishlist: %s\n",etree.tostring(tree,encoding='gbk').decode('gbk'))
			bnext=tree.xpath('bnext')[0].text
			pageno+=1

			dishs=tree.xpath('dish/item')
			for item in dishs:
				dishid=item.xpath('dishid')[0].text
				title=item.xpath('title')[0].text
				s.write('%s(%s): '%(title,dishid))

				tag=item.xpath('tag')[0].text
				taglist=[i for i in tag.split('：<br />') if i!='<br />']

				tag2=item.xpath('tag2')[0].text
				tag2list=[i for i in tag2.split('：<br />') if i!='']

				val=item.xpath('val')[0].text
				vallist=[i for i in val.split('<br />') if i!='']

				val2=item.xpath('val2')[0].text
				val2list=[i for i in val2.split('<br />') if i!='']
				val2list=[ptag.sub('',i) for i in val2list]

				dishinfo=dict(zip(taglist+tag2list,vallist+val2list))
				for k,v in dishinfo.items():
					s.write('%s：%s, '%(k,v))
				bbuy=item.xpath('bbuy')[0].text
#				buyable=item.xpath('buyable')[0].text
				evalue=item.xpath('evalue')[0].text # 经验
				if bbuy=='1': # 可做此菜，此时价格才显示
					price=item.xpath('price')[0].text # 材料费

					price=price.lstrip('￥')
					dishinfo['单份收入']=pchinese.sub('',dishinfo['单份收入'])
					# 烹饪时间是分钟的转化为小时
					if dishinfo['烹饪时间'].find('分钟')!=-1:
						dishinfo['烹饪时间']=int(pchinese.sub('',dishinfo['烹饪时间']))/60.0
					else:
						dishinfo['烹饪时间']=int(pchinese.sub('',dishinfo['烹饪时间']))

					# 计算小时收益 小时收益=(烹饪数量*单份收入-清洁灶台费-单次材料费)/烹饪时间(单位是小时)
					cashperhour=( int(dishinfo['烹饪数量']) * int(dishinfo['单份收入'])-15-int(price)) / dishinfo['烹饪时间']
					# 计算小时经验 小时经验=单次烹饪经验/烹饪时间(单位是小时)
					evalueperhour=int(evalue) / dishinfo['烹饪时间']
					s.write("单价：%s, 经验：%s, 小时收益：%d，小时经验：%d\n"%(price,evalue,cashperhour,evalueperhour))
					sortedlist.append([dishinfo['烹饪时间'],evalueperhour,cashperhour,dishid,title])
				else:
					tips=item.xpath('tips')[0].text
					s.write("tips: %s\n"%(tips,))

#				logging.info("%s(%s) bbuy/buyable/price/tips:%s/%s/%s/%s, \n%s",title,dishid,bbuy,buyable,price,tips,s.getvalue())
#				s.seek(0)
#				s.truncate()
		logging.info("菜谱信息:\n%s",s.getvalue())
		sortedlist.sort(key=lambda x:x[0])
		logging.info("按烹饪时间排序后:\n%s",'\n'.join(('时 %.2f, 经 %d, 收 %d, id %s, %s'%(t,eh,ch,did,tt) for t,eh,ch,did,tt in sortedlist )))

		s.close()

	def monitorExitFlag(self):
		''' 监视某文件, 以其最后修改时间的改变来触发程序退出(windows下)
		'''
		if self.cfgData.get('file2monitor',None)==None:
			return

		logging.info("监控线程开始, 监视文件 %s 的最后修改时间, 以其改变做为退出信号.",self.cfgData['file2monitor'])
		dirname=os.path.dirname(self.cfgData['file2monitor'])
		FILE_NOTIFY_CHANGE_LAST_WRITE=0x00000010
		handle=win32api.FindFirstChangeNotification(dirname,False,FILE_NOTIFY_CHANGE_LAST_WRITE)
		try:
			statinfo=os.stat(self.cfgData['file2monitor'])
		except WindowsError:
			old_time,new_time=None,None
		else:
			old_time=new_time=statinfo.st_mtime
		handlelist=[handle,self.monitorThreadExitEventHandle]
		while True:
			reslt=win32event.WaitForMultipleObjects(handlelist,False,win32event.INFINITE)
##			logging.info("WaitForMultipleObjects reslt=%d",reslt)
			if reslt >=win32event.WAIT_ABANDONED_0  and reslt<=(win32event.WAIT_ABANDONED_0 + 1):
				logging.info("WaitForMultipleObjects abandoned %d",reslt-win32event.WAIT_ABANDONED_0)
			elif reslt>=win32event.WAIT_OBJECT_0 and reslt<=(win32event.WAIT_OBJECT_0+1):
				eventidx=reslt-win32event.WAIT_OBJECT_0
				if eventidx==0:
					try:
						statinfo=os.stat(self.cfgData['file2monitor'])
					except WindowsError:
						pass
					else:
						new_time=statinfo.st_mtime
						if new_time!=old_time:
							old_time=new_time
							logging.info("文件 %s 最后修改时间改变: %s,大小 %d",
								self.cfgData['file2monitor'],
								time.strftime('%Y%m%d %H:%M:%S',time.localtime(statinfo.st_mtime)),
								statinfo.st_size)
							self.exitevent.set()
							break
##						else:
##							pass
##							logging.info("文件 %s 未改变!",self.cfgData['file2monitor'])

					win32api.FindNextChangeNotification(handle)
				elif eventidx==1:
					logging.info("检测到退出信号! 监控线程退出 ...")
					break
			elif reslt==win32event.WAIT_TIMEOUT:
				logging.info("WaitForMultipleObjects 超时!") # should never goes here!
			elif reslt==WAIT_FAILED:
				logging.info("调用 WaitForMultipleObjects 失败! 错误代码 %d",win32api.GetLastError())
				break
			else:
				logging.info("WaitForMultipleObjects 返回未知值 %d!",reslt)

		win32api.FindCloseChangeNotification(handle)
		logging.info("监控线程退出.")

	def checkLimitTip(self,r):
		'''检测F5, 如果检测到则设置退出信号使程序主动退出'''
		if r.decode().find('interface/limittip.php')!=-1:
			logging.info("貌似是访问过多, 被F5了, 主动退出程序...")
			self.exitevent.set()
			return True
		return False

	def getGardenSpiritInfo(self,taskkey,fuid,**kwargs):
		'''保存花园精灵信息'''

		# 获取种子id
		r=self.getResponse('http://www.kaixin001.com/!house/!garden//smartc.php?%s'%
				(urllib.parse.urlencode(
					{'verify':self.verify,'fuid':fuid,'r':"%.16f"%(random(),) } ),
				),
				None,**kwargs)
		tree=etree.fromstring(r[0])
		try:
			ret=tree.xpath('ret')[0].text
		except IndexError:
			if self.checkLimitTip(r[0]):
				return False
		else:
			ids=[]
			if ret!='succ':
				logging.info("%s 获取花园精灵种子信息失败! ret=%s (%s)",taskkey,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				return False
			items=tree.xpath('faq/item')
			for i in items:
				id=i.xpath('id')[0].text
				ids.append(id)

			if sys.platform=='linux2':
				ofnamebase='/home/kevin/gardenspirit/%s'%(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f"),)
			else:
				ofnamebase=r'd:\gardenspirit\%s'%(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f"),)
			for i in range(8):
				# 获取问题图片
				tpic=tree.xpath('tpic')[0].text
				r=self.getResponse('%s?%s'%
					  (tpic,urllib.parse.urlencode(
					    {'verify':self.verify,'r':"%.16f"%(random(),) } )
					  ),
					  None,**kwargs)
				ofname='%s-%02d[%s].png'%(ofnamebase,i,','.join(ids))
				with open(ofname,'wb') as f:
					f.write(r[0])
					logging.info("%s 花园精灵的问题图片保存在 %s",taskkey,ofname)

			# 尝试识别
			return self.garden_crackGardenSpirit(ofnamebase,ids)

		return False


	def garden_stealCrop(self):
		'''花园线程'''
		while True:
			self.getFriends4garden()
			if self.exitevent.is_set():
				logging.info("花园线程检测到退出事件")
				break
			self.checkGarden()
			if self.exitevent.is_set():
				logging.info("花园线程检测到退出事件")
				break
			self.stealCrop()

			logging.info("%d 秒后再次执行花园线程(%s)",self.cfgData['internal'],
				(datetime.datetime.now()+datetime.timedelta(seconds=self.cfgData['internal'])).strftime("%Y-%m-%d %H:%M:%S"))
			if self.exitevent.wait(self.cfgData['internal']):
				logging.info("花园线程检测到退出事件")
				break


		logging.info("花园线程退出.")


	def ranch_stealProduct(self):
		'''牧场线程'''
		while True:
			self.getFriends4ranch()
			if self.exitevent.is_set():
				logging.info("牧场线程检测到退出事件")
				break
			self.checkRanch()

			logging.info("%d 秒后再次执行牧场线程(%s)",self.cfgData['internal'],
				(datetime.datetime.now()+datetime.timedelta(seconds=self.cfgData['internal'])).strftime("%Y-%m-%d %H:%M:%S"))
			if self.exitevent.wait(self.cfgData['internal']):
				logging.info("牧场线程检测到退出事件")
				break


		logging.info("牧场线程退出.")


	def garden_crackGardenSpirit(self,ofnamebase,ids):
		'''调用脚本尝试识别花园精灵'''
		logging.info("ofnamebase=%s,ids=%s",ofnamebase,ids)
		datadate,timegroup,seedids=None,None,None
		_,name=os.path.split(ofnamebase)
		datadate,timegroup=name.split('-',1)
		seedids=','.join(ids)
		logging.info("datadate=%s,timegroup=%s,ids=%s",datadate,timegroup,seedids)
		if sys.platform=='linux2':
			subproc = subprocess.Popen(['/usr/bin/python', '/home/kevin/proj/svn/branches/20091224/t.py'], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
		else:
			subproc = subprocess.Popen(['d:\\python26\\python.exe', 'E:\\Proj\\python\\svn\\branches\\20091224\\t.py'], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)

		args2send='%s|%s|%s'%(datadate,timegroup,seedids)
		logging.info("发送 %s ...",args2send)
		rtndata,errdata=subproc.communicate(args2send.encode())
		rtndata=rtndata.decode()
		errdata=errdata.decode()
		logging.info("脚本返回stdout信息: |%s|",rtndata)
		logging.info("脚本返回stderr信息: |%s|",errdata)
		if len(errdata)>6:
			r=self.getResponse('http://www.kaixin001.com/!house/!garden//smarta.php?%s'%
					(urllib.parse.urlencode({'verify':self.verify,'ordernum':errdata})
					),None)
			try:
				tree=etree.fromstring(r[0])
			except etree.XMLSyntaxError as e:
				logging.debug("回答花园精灵 用返回数据构造tree时发生异常: %s\n%s",e,r[0].decode('utf-8'))
				return

			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.info("回答花园精灵失败!(%s)\n%s",ret,r[0].decode('utf-8'))
				return False
			else:
				logging.info("******* 回答花园精灵问题成功! ~~~~ \n%s",r[0].decode('utf-8'))
				return True

		return False


	def house_updateVerify(self,url,pattern,force=True,nolmtspd=True):
		'''访问url用pattern找到verify并更新'''
		logging.debug("更新verify, force=%s",force)

		if (not force) and self.verify:
			logging.debug("verify已存在，无需更新")
			return True

		r=self.getResponse(url,None,nolimitspeed=nolmtspd)
		m = re.search(pattern, r[0].decode())
		if m:
			logging.debug("verify=%s",m.group(1))
			self.verify = m.group(1)
		else:
			logging.info("更新 verify 失败! \n%s",r[0].decode())
			self.checkLimitTip(r[0])
			return False
		return True


	def switchModeOperation(self):
		'''根据访问次数切换餐厅做的菜、改变检查花园和牧场的频率'''
		self.cfgData['dish2cook_night']=self.cfg.get('account','dish2cook_night') # 夜晚做的菜

		cur=sum(self.cfgData['statistics4WebAccessData'].values())

		if cur<= self.cfgData['webaccess_normal'] and self.curcookmode!=self.COOKMODE_NORMAL: # 正常模式
			self.cfgData['dish2cook']=self.cfgData['dish2cook_normal']
			logging.info("正常模式: 做菜id=%s",self.cfgData['dish2cook'])
			self.curcookmode=self.COOKMODE_NORMAL
			return

		if cur> self.cfgData['webaccess_normal'] and cur<= self.cfgData['webaccess_lowfrq'] and self.curcookmode!=self.COOKMODE_LOWFRQ: # 低频模式
			logging.info("接近低频阀值! 设置程序进入 低频模式...")
			self.cfgData['dish2cook']=self.cfgData['dish2cook_lowfrq']  # 切换到做烹饪期稍长的菜的模式, 凉皮经验84收益168十分钟
			self.cfgData['internal']=self.cfgData['internal']*2 # 延长花园和牧场检查时间
			logging.info("低频模式: 做菜id=%s, 花园牧场检查间隔: %d",self.cfgData['dish2cook'],self.cfgData['internal'])
			self.curcookmode=self.COOKMODE_LOWFRQ
			return

		if cur>self.cfgData['webaccess_lowfrq'] : # 接近被F5模式（可能执行多次）
			timebfrngith=24-int(datetime.datetime.now().strftime("%H")) # 计算距离凌晨还有多少小时(向大取整)
			#logging.info("接近被F5阀值! 设置程序进入 接近被F5模式(距凌晨%d小时)...",timebfrngith)
			tmplist=self.cfgData['dish2cook_bfrnight'].split('-')
			if timebfrngith>len(tmplist):
				logging.info("无合适的备选菜id! 可选菜谱长度为 %d",len(tmplist))
			else:
				self.cfgData['dish2cook']=tmplist[timebfrngith-1]
				if self.curcookmode!=self.COOKMODE_F5: # 只延长一次
					self.cfgData['internal']=self.cfgData['internal']*2 # 延长花园和牧场检查时间
					logging.info("接近被F5模式: 做菜id=%s, 花园牧场检查间隔: %d",self.cfgData['dish2cook'],self.cfgData['internal'])
				#longtime=24-int(datetime.datetime.now().strftime("%H"))+8 # 计算明天9点还有多少小时
			self.curcookmode=self.COOKMODE_F5
			return

	def spiderman_doFight(self):
		'''X世界战斗线程'''
		if not self.signed_in:
			self.signin()
			if not self.signed_in:
				return False

		pMyHealth=re.compile(r'''<span id="user_health"\s+>(\d+)</span>''') # 匹配自己的生命值
		pMyEnergy=re.compile(r'''<span   id="user_energy">(\d+)</span>''') # 匹配自己的能量
		pMaxEnergy=re.compile(r'''<span id="user_max_energy">(\d+)</span>''') # 匹配最大的能量
		pMyLevel=re.compile(r'''<span id="user_level">(\d+)</span>''') # 匹配自己的级别
		pMyNumber=re.compile(r'''<b>你团队的战斗值<font style="font-weight:normal;">\(共<span class="c_green">(\d+)</span>人\)''',re.M|re.S) # 自己的队员数
		pStamina=re.compile(r'''<span id="user_stamina" >(\d+)</span>''') # 匹配战斗值
		pMyExperience=re.compile(r'''<span id='user_experience'>(\d+)</span>''') # 匹配自己的经验值
		pNextLevelExperience=re.compile(r'''<span id='next_level_experience'>(\d+)</span>''') # 匹配下一级的经验值
		pFightList=re.compile(r'''<div id="fightcontent">(.+?)</div>''',re.M|re.S) # 定位团伙列表
		pEach=re.compile(r'''<tr id="tr(?P<key>.+?)" height="\d+">.+?"y noline c_yellow">(?P<name>.+?)</a>.+?级别(?P<level>\d+)级.+?<td class="tac">(?P<number>\d+)</td>.+?</tr>''',re.M|re.S) # 定位首领级别和成员数


		task_key='X世界'

		flist=[] # 保存每次从页面获取的可对战的团队
		totalexp=0 # 保存总共获得的经验值
		while True:
			logging.info("%s 刷新战斗页面...",task_key)

			r=self.getResponse('http://www.kaixin001.com/!spiderman/fight.php',None)
			t=r[0].decode()
			try:
				myhealth=int(re.search(pMyHealth,t).group(1))
				myenergy=int(re.search(pMyEnergy,t).group(1))
				maxenergy=int(re.search(pMaxEnergy,t).group(1))
				mylevel=int(re.search(pMyLevel,t).group(1))
				mynumber=int(re.search(pMyNumber,t).group(1))
				stamina=int(re.search(pStamina,t).group(1))
				myexperience=int(re.search(pMyExperience,t).group(1))
				nextlevelexperience=int(re.search(pNextLevelExperience,t).group(1))

				logging.info("%s 生命 %d, 能量 %d/%d, 级别 %d, 队员数 %d, 战斗值 %d, 经验 %d/%d.",task_key,myhealth,myenergy,maxenergy,mylevel,mynumber,stamina,myexperience,nextlevelexperience)
				if stamina>0: # 战斗值不为0
					if myhealth<80: # 生命值加满
						if not self.spiderman_hospital(task_key):
							stopfight=True
							break

					m=re.search(pFightList,t) # 找团队列表
					if m:
						fightlist=re.finditer(pEach,m.group(1))
						for i in fightlist:
							key,name,level,number=i.group('key'),i.group('name'),int(i.group('level')),int(i.group('number'))
							if level<mylevel-1 and number<mynumber-5: # 选比自己差的团队
								flist.append((name,key,level,number))
								logging.debug("%s 可选对战团队 %s(%d-%d)",task_key,name,level,number)

						stopfight=False
						for n,k,_,_ in flist:
							if self.exitevent.is_set():
								logging.info("%s 检测到退出信号",task_key)
								stopfight=True
								break
							if stopfight==True:
								break

							for _ in range(3): # 每个团队战5次
								if self.exitevent.is_set():
									logging.info("%s 检测到退出信号",task_key)
									stopfight=True
									break
								rslt,exp,cash,combat,health=self.spiderman_fight(n,k,task_key)
								if rslt is None: # 出错
									logging.debug("rslt is None")
									break

								myhealth+=int(health)
								totalexp+=int(exp)
								self.statistics['X世界战斗经验']=self.statistics.get('X世界战斗经验',0)+int(exp)

								if (type(rslt)==type(False) and (not rslt) ) or rslt=='e6' or rslt=='e7': # 挑战失败 或者 返回 e6,e7等错误码, 总之就是不再与此团队对战
									if rslt==False:
										#pass
										logging.info("%s 挑战 %s 失败!",task_key,n)
									else:
										#pass
										logging.info("%s 挑战 %s 返回 %s",task_key,n,rslt)
									break
								elif rslt=='e2': # 战斗值不足
									logging.info("%s 战斗值不足, 结束本轮战斗",task_key)
									stopfight=True
									break
								elif rslt=='e13': # 达到升级标准需要刷新页面
									logging.info("%s 达到升级标准, 需要刷新页面",task_key)
									if not self.spiderman_uplevel(task_key):
										stopfight=True
										break

								if myhealth<80:
									logging.info("%s 生命值低于80, 去医疗...",task_key)
									if self.spiderman_hospital(task_key):
										myhealth=100
									else:
										stopfight=True
										break

						if stopfight==False: # 说明还可以再战斗
							#logging.info("%s 可以继续战斗",task_key)
							del flist[:]
							continue


			except AttributeError as e:
				logging.info("%s 解析战斗信息失败, %s \n返回:\n%s",task_key,e,r[0].decode())
				if self.checkLimitTip(r[0]):
					break
			finally:
				del flist[:]

			logging.info("%s 目前为止获得经验值 %d, %d 秒后再次执行战斗线程(%s)",task_key,totalexp,self.cfgData['internal4spidermanfight'],
				(datetime.datetime.now()+datetime.timedelta(seconds=self.cfgData['internal4spidermanfight'])).strftime("%Y-%m-%d %H:%M:%S"))
			if self.exitevent.wait(self.cfgData['internal4spidermanfight']):
				logging.info("%s 检测到退出信号",task_key)
				break

		logging.info("%s 本次执行共获得经验值 %d",task_key,totalexp)

	def spiderman_fight(self,name,key,task_key=''):
		'''和一个团队交战,返回 rslt,exp,cash,combat,health
		rslt 为 True或False 代表挑战成功或者失败，None时表示出错
		rslt 为 str 时代表错误返回值 比如e2代表战斗值为0，e6为频繁挑战，e7为对方逃跑
		exp 表示增加的经验值
		cash 代表获得（0或正）或者失去的现金（负）
		combat 代表战斗值改变（负）
		health 代表生命值改变（0或者负）
		'''
		logging.debug("%s 和 %s 交战...",task_key,name)
		r = self.getResponse('http://www.kaixin001.com/!spiderman/!ajax_fight.php',{'cid':4,'objid':key,'tmp':"%.16f"%(random(),)})

		winorlose,exp,cash,combat,health=None,'0','0','0','0'

		try:
			t=r[0].decode()
		except Exception as e:
			logging.debug("解码返回结果出错：%s",e) # for debug only!!!
		if len(t)==2:
			winorlose=t
		else:
			pTitleArea=re.compile(r'''<ul class="title_area">(.+?)</ul>''',re.S|re.M)
			pWinLose=re.compile(r'''<img src=".+?bg_banner_(.+?).gif"''')
			pExp=re.compile(r'''<li class="exp .+?" >经验 (.+?)</li>''')
			pCash=re.compile(r'''<li class="cash .+?">现金 (.+?)</li>''')
			pCombat=re.compile(r'''<li class="combat .+?">战斗 (.+?)</li>''')
			pHealth=re.compile(r'''<li class="health .+?">生命 (.+?)</li>''')
			try:
				t=re.search(pTitleArea,t).group(1)
				s=re.search(pWinLose,t).group(1)
				if s=='fail':
					winorlose=False
				else:
					winorlose=True
				exp=re.search(pExp,t).group(1)
				cash=re.search(pCash,t).group(1)
				combat=re.search(pCombat,t).group(1)
				health=re.search(pHealth,t).group(1)
				logging.info("%s 和 %s 交战结果: %s 经验 %s 现金 %s 战斗值 %s 生命值 %s",task_key,name,winorlose,exp,cash,combat,health)
			except AttributeError:
				logging.info("%s 解析战斗结果时失败, 返回:\n%s",task_key,r[0].decode())
				if r[0].decode().startswith('e13'):
					winorlose='e13'

		return winorlose,exp,cash,combat,health

	def spiderman_hospital(self,task_key=''):
		'''恢复生命值'''
		logging.debug("%s 恢复生命值...",task_key)
		# 端到餐台
		r = self.getResponse('http://www.kaixin001.com/!spiderman/!hospital.php?%s'%
	    (urllib.parse.urlencode(
	    {'l':'a','cid':2,'tmp':"%.16f"%(random(),)}),),
	    None)

		t=r[0].decode()
		if t.find('1|||')!=-1 or t.find('2|||')!=-1: # 成功
			logging.info("%s 恢复生命值成功",task_key)
			return True

		pContent=re.compile(r'''<div class="f14".*?>(.+?)</div>''',re.S|re.M)
		logging.info("%s 恢复生命值返回:\n%s",task_key,re.search(pContent,t).group(1))

		return False

	def spiderman_uplevel(self,task_key=''):
		'''升级刷新页面'''
		logging.debug("%s 刷新升级页面...",task_key)
		r = self.getResponse('http://www.kaixin001.com/!spiderman/!ajax_uplevel.php?%s'%
	    (urllib.parse.urlencode(
	    {'cid':4,'tmp':"%.16f"%(random(),)}),),
	    None)

		t=r[0].decode()
		logging.info("%s 访问升级页面返回: %s",task_key,t)

		return True


	def cafe_getChef(self,cafeid,task_key=''):
		'''获取大厨体力值'''
		logging.debug("%s 查看餐厅 %s 的大厨状态...",task_key,cafeid)
		for i in range(3):
			if self.exitevent.is_set():
				logging.info("%s 检测到退出事件",task_key)
				break
			# 清洗灶台
			r = self.getResponse('http://www.kaixin001.com/cafe/api_autochef.php?%s'%
				(urllib.parse.urlencode(
					{'verify':self.cafeverify,'act':'0','cafeid':cafeid,'viewuid':self.uid,'rand':"%.16f"%(random(),)}),),
				None)
			try:
				tree=etree.fromstring(r[0])
			except etree.XMLSyntaxError as e:
				logging.info("%s tree=etree.fromstring(r[0]) 出错!\n%s\n%s",task_key,e,r[0].decode('utf8'))
				self.cafe_updateVerify()
				continue

	##		logging.debug("===> %s api_autochef返回: %s\n",task_key,etree.tostring(tree,encoding='gbk').decode('gbk'))
			try:
				orderid=tree.xpath('orderid')[0].text
				leavetime=tree.xpath('leavetime')[0].text
				status=tree.xpath('status')[0].text
				cheftype=tree.xpath('cheftype')[0].text
				mana=tree.xpath('mana')[0].text
			except IndexError as e:
				if r[0].decode().find("找不到大厨")!=-1:
					logging.info("%s 没有大厨？",task_key)
					break
				else:
					logging.info("%s 获取返回信息时发生异常!\n%s\n%s",task_key,e,etree.tostring(tree,encoding='gbk').decode('gbk'))
				if self.checkLimitTip(r[0]):
					break
			else:
				with self.semaphore4cafemana:
					self.cafemana=int(mana)
				logging.info("===> %s 大厨信息: orderid/leavetime/cheftype/status/mana: %s/%s/%s/%s/%s",task_key,orderid,leavetime,cheftype,status,mana)
				return True

		return False


	def garden_plough(self,farmnum,task_key=''):
		'''犁地'''
		logging.debug("%s 在自家地块 %s 犁地...",task_key,farmnum)
		for _ in range(2):
			r = self.getResponse('http://www.kaixin001.com/!house/!garden//plough.php?%s'%
				(urllib.parse.urlencode(
					{'fuid':'0','seedid':0,'farmnum':farmnum,'confirm':0,'r':"%.16f"%(random(),)}),),
				None)

			tree=etree.fromstring(r[0])
			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.info("%s 在自家地块 %s 犁地出错(%s)\n%s",
					task_key,farmnum,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				continue

			try:
				cashtips=tree.xpath('cashtips')[0].text
			except IndexError:
				logging.info("%s 自家地块 %s 犁地成功.",task_key,farmnum)
				return True
			else:
				logging.info("%s 自家地块 %s 犁地成功, %s",task_key,farmnum,cashtips)
				return True

		return False

	def garden_plan(self,farmnum,task_key=''):
		'''播种'''
		logging.debug("%s 在自家地块 %s 播种 ...",task_key,farmnum)
		for _ in range(2):
			r = self.getResponse('http://www.kaixin001.com/!house/!garden//farmseed.php?%s'%
				(urllib.parse.urlencode(
					{'fuid':'0','seedid':self.cfgData['autofarm'][farmnum],'farmnum':farmnum,'confirm':0,'r':"%.16f"%(random(),)}),),
				None)

			tree=etree.fromstring(r[0])
			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.info("%s 自家地块 %s 播种 %s(%s) 出错(%s)\n%s",
					task_key,farmnum,[x for x in self.cfgData['seedlist'] if x[1]==self.cfgData['autofarm'][farmnum]][0][2],self.cfgData['autofarm'][farmnum],ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				if '已没有该种子了' in tree.xpath('reason')[0].text:
					if self.garden_buyseed(self.cfgData['autofarm'][farmnum],1,task_key):
						continue
				else:
					break

			logging.info("%s 自家地块 %s 播种 %s(%s) 成功.",task_key,farmnum,[x for x in self.cfgData['seedlist'] if x[1]==self.cfgData['autofarm'][farmnum]][0][2],self.cfgData['autofarm'][farmnum])
			return True

		return False

	def garden_buyseed(self,seedid,num,task_key=''):
		'''买种子'''
		logging.debug("%s 购买种子 %s 个 %s(%s)...",task_key,num,[x for x in self.cfgData['seedlist'] if x[1]==seedid][0][2],seedid)
		for _ in range(2):
			r = self.getResponse('http://www.kaixin001.com/!house/!garden/buyseed.php',
					{'num':num,'verify':self.verify,'seedid':seedid})

			tree=etree.fromstring(r[0])
			ret=tree.xpath('ret')[0].text
			if ret!='succ':
				logging.info("%s 购买种子 %s 个 %s(%s) 出错(%s)\n%s",
					task_key,num,[x for x in self.cfgData['seedlist'] if x[1]==seedid][0][2],seedid,ret,etree.tostring(tree,encoding='gbk').decode('gbk'))
				continue

			try:
				change_cash_num=tree.xpath('change_cash_num')[0].text
			except IndexError:
				logging.info("%s 购买种子 %s 个 %s(%s) 成功.",task_key,num,[x for x in self.cfgData['seedlist'] if x[1]==seedid][0][2],seedid)
				return True
			else:
				logging.info("%s 购买种子 %s 个 %s(%s) 成功, 现金 %s.",task_key,num,[x for x in self.cfgData['seedlist'] if x[1]==seedid][0][2],seedid,change_cash_num)
				return True

		return False

import logging
from lxml import etree
import re, time#, webbrowser
from pprint import pprint
from io import StringIO
from random import uniform, random
import urllib, urllib.request, urllib.error, urllib.parse, http.cookiejar, json
import configparser
import codecs
import os
import copy
from threading import Timer
from threading import Event
from threading import Semaphore
import _thread
import datetime
import socket
import sys
import shelve
import imp
from html.entities import name2codepoint
try:
	import win32api
	import win32event
except ImportError:
	print('no win32api ?')
import math
try:
	import tkinter
except ImportError:
	print('no tkinter ?')
from queue import Queue
from queue import Empty
from threading import Lock
from threading import Condition
from random import randint
import subprocess
try:
	import wingdbstub # 用于 wingide 调试
except ImportError:
	print('no wingide debug support ?')
import signal
from logging.handlers import RotatingFileHandler
if __name__=='__main__':
##	i=fakeKaixin()
##	i.run()

	i=Kaixin(sys.argv[1])
##	i.getFishinfo()
	try:
		i.run()
	except Exception as e:
		print(e)
##	import cProfile,pstats
##	cProfile.run('''Kaixin(r'd:\kaixin.ini').run()''',r'd:\kaixin-profile.txt')
	#p=pstats.Stats(ur'd:\kaixin-profile.txt')
	#p.sort_stats('time', 'cum').print_stats('kaixin')

