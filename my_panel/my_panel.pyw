import codecs
import tkinter
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import tkinter.ttk as ttk

from util.ToolTip import ToolTip
from util.HyperlinkManager import HyperlinkManager
import util.const as const

import os
import time
import sys
import configparser
import logging
import logging.config
import json
import re

# TODO: 各panel建立自己的菜单,文件输入支持gzip

const.StatPlaying,const.StatStopped,const.StatPaused,const.StatPaused4Hover=range(4)

class WordFile(object):
	def __init__(self,fname):
		try:
			self.wordlist=codecs.open(fname,encoding='gb18030').readlines()
		except UnicodeDecodeError:
			self.wordlist=codecs.open(fname,encoding='utf8').readlines()
		self.wordlist=[ i.strip() for i in self.wordlist if len(i.strip())!=0]
		self.maxidx=len(self.wordlist)-1
		self.curidx=0

	def __iter__(self):
		return self

	def __next__(self):
		if self.curidx<self.maxidx:
			self.curidx+=1
			return self.wordlist[self.curidx-1]
		else:
			raise StopIteration()

	def __len__(self):
		return len(self.wordlist)

	def __getitem__(self,key):
		return self.wordlist[key]

	def setStart(self,idx):
		if idx<self.maxidx:
			self.curidx=idx
		else:
			self.curidx=self.maxidx

	def getIdx(self):
		return self.curidx-1

class Cfg(object):pass

class BasePanel(object):
	def __init__(self,name,section,root):
		self.name=name # 显示的panel名称
		self.section=section # 存取配置默认使用的section
		self.root=root
		self.logger=None # 日志对象
		self.title=None # 日志中的模块名
		self.cur_list_menu=None # 显示当前的 文件/源/字典 列表
		self.recent_list_menu=None # 显示最近的 文件/源/字典 列表
		self.c=Cfg()

		self.tooltiptext=None
		self.curgeometry=None
		self.stat=None


	def loadCfg(self,cfg,section=None):
		if not section:
			section=self.section
		self.c.title=cfg.get(section,'title','unknown')
		self.c.enabled=cfg.getboolean(section,'enabled')
		self.c.file=json.JSONDecoder().decode(cfg.get(section,'file'))
		self.c.alpha=cfg.getfloat(section,'alpha')
		self.c.fg=cfg.get(section,'fg')
		self.c.bg=cfg.get(section,'bg')
		self.c.recent=json.JSONDecoder().decode(cfg.get(section,'recent'))

	def applyCfg(self):
		self.logger=logging.getLogger(self.c.title)
		self.root.attributes("-alpha", self.c.alpha) # use transparency level 0.1 to 1.0 (no transparency)
		self.title=self.c.title


	def saveCfg(self,cfg,section=None):
		if not section:
			section=self.section
		cfg.set(section,'title',self.c.title)
		cfg.set(section,'enabled',str(self.c.enabled))
		cfg.set(section,'file',json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.c.file).replace(',[',',\n['))
		cfg.set(section,'alpha',str(self.c.alpha))
		cfg.set(section,'fg',str(self.c.fg))
		cfg.set(section,'bg',str(self.c.bg))
		cfg.set(section,'recent',json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.c.recent).replace(',[',',\n['))

	def updatePanel(self):
		pass

	def onLeftMouse(self,event):
		if event.type=='7': # Enter
			self.root.attributes("-alpha", 1)
		elif event.type=='8': # Leave
			self.root.attributes("-alpha", self.c.alpha)

	def createMenu(self,mainmenu):
		pass


class RecitePanel(BasePanel):
	def __init__(self,name,section,root):
		BasePanel.__init__(self,name,section,root)
		self.content=None
		self.timerid=None
		self.sText=tkinter.StringVar() # label显示的内容
		self.vFile=tkinter.StringVar() # 当前显示的文件
		self.sText.set('MyRecite v0.1 powered by Python~')
		ft = tkFont.Font(family = 'Fixdsys',size = 20,weight = tkFont.BOLD)
		self.label=tkinter.Label(self.root,font=ft,relief='ridge',anchor='center',textvariable=self.sText)
		self.label.pack(expand='yes',fill=tkinter.BOTH)

		# 设置tooltip
		self.tooltiptext=tkinter.StringVar()
		ft = tkFont.Font(family = 'Fixdsys',size = 12,weight = tkFont.BOLD)
		self.tt=ToolTip(self.label,follow_mouse=0,font=ft,wraplength=self.root.winfo_screenwidth()/3,textvariable=self.tooltiptext)

		self.label.bind('<Leave>',self.onLeftMouse,'+')
		self.label.bind('<Enter>',self.onLeftMouse,'+')


	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.interval=cfg.getint(section,'interval')
		self.c.cur=cfg.getint(section,'cur')

	def applyCfg(self):
		BasePanel.applyCfg(self)
		self.label.configure(bg=self.c.bg)
		self.label.configure(fg=self.c.fg)
##		if self.stat==const.StatPlaying:
##			self.pausePanel()
##			self.content=WordFile(self.c.file[self.c.cur][0])
##			self.content.setStart(self.c.file[self.c.cur][1])
##			self.updatePanel()
##		else:
##			self.content=WordFile(self.c.file[self.c.cur][0])
##			self.content.setStart(self.c.file[self.c.cur][1])

	def updatePanel(self):
		BasePanel.updatePanel(self)
		try:
			t=next(self.content)
		except StopIteration:
			print('stoped.')
			self.stat=const.StatStopped
			if self.timerid:
				self.label.after_cancel(self.timerid)
				self.timerid=None
		else:
			self.sText.set(t)
			self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
			self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))
			self.tooltiptext.set('%d/%d -- %s'%(self.content.curidx,self.content.maxidx,t))
			self.c.file[self.c.cur][1]=self.content.getIdx()
			self.timerid=self.label.after(self.c.interval,self.updatePanel)

	def pausePanel(self):
		if self.timerid:
			self.label.after_cancel(self.timerid)
			self.timerid=None

	def createMenu(self,mainmenu):
		BasePanel.createMenu(self,mainmenu)
		menu=tkinter.Menu(mainmenu,tearoff=False)

		self.cur_list_menu=tkinter.Menu(mainmenu,tearoff=False)
		for idx,i in enumerate(self.c.file):
			self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
				value=i[0],variable=self.vFile)
			if idx==self.c.cur:
				self.cur_list_menu.invoke(idx)
		mainmenu.add_cascade(label='files...',menu=self.cur_list_menu)

		for k,v in (('word file ...',self.onCmdChooseFile),
		            ('interval ...',self.onCmdChangeInterval)
								):
			menu.add_command(label = k,command = v)
			menu.add_separator()
		mainmenu.add_cascade(label = self.name,menu = menu)

	def onCmdSwitchFile(self):
		self.logger.info('swith to file %s',self.vFile.get())
		# 获取文件对应的索引
		idx=[i for i,n in enumerate(self.c.file) if n[0]==self.vFile.get()][0]
		t=WordFile(self.c.file[idx][0])
		t.setStart(self.c.file[idx][1])

		old_stat=self.stat
		if self.stat==const.StatPlaying:
			self.pausePanel()
		self.c.cur=idx
		self.content=t
		if old_stat in (const.StatPlaying,const.StatStopped) :
			self.updatePanel()


	def onCmdChooseFile(self):
		'''文件选择'''
##		oldstat=self.stat
##		if self.stat==const.StatPlaying and self.timerid:
##			self.pauseShow(const.StatPaused)
		f=tkFileDialog.askopenfilenames(parent=self.root,title='Choose file(s) to show',
			filetypes=[('Text','*.txt *.log'),('Python', '*.py *.pyw'), ('All files', '*')] )
		if f:
			flist=self.root.tk.splitlist(f) # http://psf.upfronthosting.co.za/roundup/tracker/issue5712 workaround: http://code.activestate.com/lists/python-tkinter-discuss/2016/
			if len(flist)>5:
				self.logger.info('一次最多添加5个文件，多余的会被丢弃，你选择了 %d个',len(flist))
				flist=flist[:5]
			for i,onefile in enumerate(flist):
				self.logger.debug('multi file %02d/%d: %s',i,len(flist),onefile)

			addorreplace=tkMessageBox.askyesnocancel('Add or replace','add the file(s) to your file list? (press "no" or replace current file list)',default=tkMessageBox.YES)
			self.logger.debug('addorreplace=%s',addorreplace)
			if addorreplace==None:
				self.logger.debug('do nothing')
			elif addorreplace==True: # add
				self.c.file.extend([i,0] for i in flist)
				# 更新filelist菜单
				for i in flist:
					self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
						value=i[0],variable=self.vFile)
				# 从recent中删除当前文件列表中存在的
				self.c.recent=[i for i in self.c.recent if i[0] not in (j[0] for j in self.c.file)]
				self.logger.debug('add done. new file list: %s',self.c.file)
			elif addorreplace==False: # replace
				if self.stat==const.StatPlaying:
					self.pausePanel()

				# 从recent中删除当前文件列表中存在的
				self.c.recent=[i for i in self.c.recent if i[0] not in (j[0] for j in self.c.file)]
				self.cur_list_menu.delete(0,len(self.c.file)-1) # 删掉filelist菜单
				# 当前文件列表入recent
				for t in reversed(self.c.file):
					self.c.recent.insert(0,t)
				del self.c.file[:]
				# 新文件如当前文件列表
				self.c.file.extend([[i,0] for i in flist])
				# 构造新filelist菜单
				self.c.cur=0
				for idx,i in enumerate(self.c.file):
					self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
						value=i[0],variable=self.vFile)
					if idx==self.c.cur:
						self.cur_list_menu.invoke(idx)
				self.logger.debug('replace done. new file list: %s\nnew recent: %s',self.c.file,self.c.recent)

				self.updatePanel() # start playing anyway


	def onCmdChangeInterval(self):
		'''设置刷新频率'''
		r=tkSimpleDialog.askinteger('change update speed','input new interval(ms) (1000-10000):',
			initialvalue=self.c.interval,maxvalue=10000,minvalue=1000)
		if r:
			self.c.interval=r

	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)
		if not section:
			section=self.section
		cfg.set(section,'cur',str(self.c.cur))
		cfg.set(section,'interval',str(self.c.interval))

class SubtitlePanel(BasePanel):
	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.cur=cfg.getint(section,'cur')
		self.c.interval=cfg.getint(section,'interval')
	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)
		if not section:
			section=self.section
		cfg.set(section,'cur',str(self.c.cur))
		cfg.set(section,'interval',str(self.c.interval))

class ReaderPanel(BasePanel):
	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.cur=cfg.getint(section,'cur')
		self.c.interval=cfg.getint(section,'interval')
		self.c.check_interval=cfg.get(section,'check_interval',900)

	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)
		if not section:
			section=self.section
		cfg.set(section,'cur',str(self.c.cur))
		cfg.set(section,'interval',str(self.c.interval))
		cfg.set(section,'check_interval',str(self.c.check_interval))

	def onCmdChooseRss(self):
		'''rss选择'''
		r=tkSimpleDialog.askstring('Input rss url','input rss url you want to read:',
			initialvalue='http://')
		if r:
			tkMessageBox.showinfo(message=r)
			# TODO: 实现解析rss并依次显示，自己过滤/高亮指定关键字/正则的条目

class DictionaryPanel(BasePanel):
	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)

	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)

class MyPanelApp(object):
	def __init__(self,inifile='my_panel.ini',inifile_encoding='utf-8'):
		self.root = tkinter.Tk()
		# 构造panel类工厂
		self.panelFactory={'RecitePanel':RecitePanel,
											'SubtitlePanel':SubtitlePanel,
											'ReaderPanel':ReaderPanel,
											'DictionaryPanel':DictionaryPanel}
		self.panellist=[]

		# 读取配置信息
		self.inifile_encoding=inifile_encoding
		self.curdir=os.path.abspath('.')
		if not os.path.isabs(inifile):
			self.inifile=os.path.join(self.curdir,inifile)
		else:
			self.inifile=inifile
		self.c=Cfg()
		self.cfg=None
		self.logger=None
		self.loadCfg()

		# 处理窗口拖动
		self.InDrag=False
		self.oldxy=[0,0]
		self.oldpos=[0,0]
		self.curgeometry=[320,240]

		self.curpanel=self.panellist[self.c.cur_panel-1] # 当前使用 panel


		self.root.wm_attributes("-topmost", 1) # set to Top Most
		# 绑定事件
		self.root.bind('<ButtonPress-1>', self.onLeftMouse)
		self.root.bind('<ButtonRelease-1>',self.onLeftMouse)
		self.root.bind('<Motion>',self.onLeftMouse)
		self.root.bind('<Leave>',self.onLeftMouse)
		self.root.bind('<Enter>',self.onLeftMouse)

		self.root.bind('<Double-Button-1>',self.onLeftMouseDbClick)
		self.root.bind('<Button-3>',self.onRightMouse)
		self.root.overrideredirect(True) # 不显示titlebar


		# 设置右键菜单
		self.menubar=tkinter.Menu(self.root,tearoff=False)

		self.vMode=tkinter.StringVar()
		for i,p in enumerate(self.panellist):
			self.menubar.add_radiobutton(label=p.name,command=self.switchMode,value=p.name,variable=self.vMode)
			if p==self.curpanel:
				self.menubar.invoke(i)
		self.menubar.add_separator()
		for p in self.panellist:
			p.createMenu(self.menubar)

		self.menubar.add_cascade(label='Quit',command=self.onQuit)

		# 初始化显示文件
		self.startShow()

	def switchMode(self):
		self.logger.info("self.vMode=%s",self.vMode.get())

	def loadCfg(self):
		self.cfg=configparser.SafeConfigParser()
		self.cfg.readfp(codecs.open(self.inifile,'r',self.inifile_encoding))

		self.c.logdir=self.cfg.get('account','logdir',self.curdir)
		self.c.logsuffix=self.cfg.get('account','logsuffix','%d'%(os.getpid(),))

		self.rundate=time.strftime('%Y%m%d') # 记录执行日期

		# 读取logging配置文件
		logging_conf=self.cfg.get('account','logging_conf','logging.conf')
		if not os.path.isabs(logging_conf):
			self.c.logging_conf=os.path.join(self.curdir,logging_conf)
		else:
			self.c.logging_conf=logging_conf
		logging.config.fileConfig(self.c.logging_conf)
		self.logger=logging.getLogger('main')
		self.logger.info("\n\n%s\n%s start %s %s\n%s\n 脚本最后更新: %s",'='*75,'='*((75-8-len(sys.argv[0]))//2),sys.argv[0],'='*((75-8-len(sys.argv[0]))//2),'='*75,time.strftime('%Y%m%d %H:%M:%S',time.localtime(os.stat(sys.argv[0]).st_mtime)))

		# 读取程序配置
		self.c.total_panel=self.cfg.getint('account','total_panel')
		self.c.cur_panel=self.cfg.getint('account','cur_panel')
		for i in range(1,self.c.total_panel+1):
			s='panel-%d'%(i,)
			p=self.cfg.get(s,'type')
			p=self.panelFactory[p]('%s-%s'%(s,p),s,self.root) # 建立相应panel对象
			p.loadCfg(self.cfg,s) # 由相应panel对象读取属于自己的配置
			p.applyCfg()
			self.panellist.append(p)


	def onQuit(self):
		print('onQuit')
		for p in self.panellist:
			p.saveCfg(self.cfg)

		self.cfg.write(codecs.open(self.inifile,'w',self.inifile_encoding))
		self.root.quit()

	def onRightMouse(self,event):
		'''右键选择菜单'''
		self.menubar.post(event.x_root,event.y_root)

	def startShow(self):
		'''开始显示内容'''
		self.curpanel.stat=const.StatPlaying
		self.curpanel.updatePanel()

	def pauseShow(self,new_stat):
		'''暂停显示内容'''
		self.curpanel.stat=new_stat
		self.curpanel.pausePanel()

	def onLeftMouse(self,event):
		'''处理窗体拖放、内容暂停/恢复'''
		if event.type=='6': # Motion
			if self.InDrag:
				xmvto=event.x_root-self.oldxy[0]
				ymvto=event.y_root-self.oldxy[1]
##				print('Motion at (%d,%d) +%d+%d'%(event.x,event.y,xmvto,ymvto))
				self.root.geometry('%dx%d+%d+%d'%(self.curpanel.curgeometry[0],self.curpanel.curgeometry[1],
					xmvto,ymvto))
		elif event.type=='7': # Enter
			if self.curpanel.stat==const.StatPlaying:
				print('StatPlaying->StatPaused4Hover')
				self.pauseShow(const.StatPaused4Hover)
		elif event.type=='8': # Leave
			if not self.InDrag and self.curpanel.stat==const.StatPaused4Hover:
				print('StatPaused4Hover->StatPlaying')
				self.startShow()
		elif event.type=='4': # ButtonPress
			if not self.InDrag:
##				print('ButtonPress at (%d,%d)-(%dx%d)'%(event.x,event.y,event.x_root,event.y_root))
				self.InDrag=True
				self.oldxy=[event.x,event.y]
		elif event.type=='5': # ButtonRelease
			if self.InDrag:
##				print('ButtonRelease at (%d,%d)'%(event.x,event.y))
				self.InDrag=False
		else:
			print(event.type)
			print('in onLeftMouse (%d,%d)'%(event.x,event.y))

	def onLeftMouseDbClick(self,event):
		'''暂停/继续'''
		if self.curpanel.stat in (const.StatPlaying,const.StatPaused4Hover):
			print('StatPlaying or StatPaused4Hover ->StatPaused')
			self.pauseShow(const.StatPaused)
		elif self.curpanel.stat==const.StatPaused:
			print('StatPaused->StatPlaying')
			self.startShow()
		elif self.curpanel.stat==const.StatStopped:
			print('StatStopped->StatPlaying')
			self.startShow()


	def run(self):
		self.root.mainloop()
		self.root.quit()

if __name__=='__main__':
	m=MyPanelApp()
	m.run()

	input('press ENTER to exit...')

