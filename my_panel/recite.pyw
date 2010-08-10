import codecs
import tkinter
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import tkinter.ttk as ttk

from util.ToolTip import ToolTip
from util.HyperlinkManager import HyperlinkManager

import os
import time
import sys
import configparser
import logging
import logging.config
import json

# TODO: 各panel建立自己的菜单


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

class Cfg(object):pass

class BasePanel(object):
	def __init__(self,name,root):
		self.name=name
		self.root=root
		self.c=Cfg()

		self.tooltiptext=None
		self.curgeometry=None


	def loadCfg(self,cfg):
		self.c.title=cfg.get(self.name,'title','unknown')
		self.c.enabled=cfg.getboolean(self.name,'enabled')
		self.c.file=json.JSONDecoder().decode(cfg.get(self.name,'file'))
		self.c.alpha=cfg.getfloat(self.name,'alpha')
		self.c.fg=cfg.get(self.name,'fg')
		self.c.bg=cfg.get(self.name,'bg')
		self.c.recent=json.JSONDecoder().decode(cfg.get(self.name,'recent'))

	def applyCfg(self):
		self.root.attributes("-alpha", self.c.alpha) # use transparency level 0.1 to 1.0 (no transparency)

	def saveCfg(self,cfg):
		pass

	def updatePanel(self):
		pass

	def onLeftMouse(self,event):
		if event.type=='7': # Enter
			self.root.attributes("-alpha", 1)
		elif event.type=='8': # Leave
			self.root.attributes("-alpha", self.c.alpha)

class RecitePanel(BasePanel):
	def __init__(self,name,root):
		BasePanel.__init__(self,name,root)
		self.content=None
		self.timerid=None
		self.sText=tkinter.StringVar() # label显示的内容
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


		# 设置超链接
##		self.hyperlink_manager=HyperlinkManager(self.label)

	def loadCfg(self,cfg):
		BasePanel.loadCfg(self,cfg)
		self.c.interval=cfg.getint(self.name,'interval')
		self.c.cur=cfg.getint(self.name,'cur')

	def applyCfg(self):
		self.label.configure(bg=self.c.bg)
		self.label.configure(fg=self.c.fg)
		self.content=WordFile(self.c.file[self.c.cur][0])
		self.content.setStart(self.c.file[self.c.cur][1])

	def updatePanel(self):
		try:
			t=next(self.content)
		except StopIteration:
			print('stoped.')
			self.root.stat=self.StatStoped
			if self.timerid:
				self.label.after_cancel(self.timerid)
				self.timerid=None
		else:
			self.sText.set(t)
			self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
			self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))
			self.tooltiptext.set('%d/%d -- %s'%(self.content.curidx,self.content.maxidx,t))
			self.timerid=self.label.after(self.c.interval,self.updatePanel)

	def pausePanel(self):
		if self.timerid:
			self.label.after_cancel(self.timerid)
			self.timerid=None

class SubtitlePanel(BasePanel):
	def loadCfg(self,cfg):
		BasePanel.loadCfg(self,cfg)
		self.c.cur=cfg.getint(self.name,'cur')
		self.c.interval=cfg.getint(self.name,'interval')

class ReaderPanel(BasePanel):
	def loadCfg(self,cfg):
		BasePanel.loadCfg(self,cfg)
		self.c.cur=cfg.getint(self.name,'cur')
		self.c.interval=cfg.getint(self.name,'interval')
		self.c.check_interval=cfg.get(self.name,'check_interval',900)

class DictionaryPanel(BasePanel):
	def loadCfg(self,cfg):
		BasePanel.loadCfg(self,cfg)

class MyPanel(object):
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

		# 处理状态
		self.StatPlaying,self.StatStoped,self.StatPaused,self.StatPaused4Hover=range(4)
		self.Stat=None

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
		content_menu=tkinter.Menu(self.menubar,tearoff=False)
		config_menu=tkinter.Menu(self.menubar,tearoff=False)

		for k,v in {'file ...':self.onCommandChooseFileSource,
		            'rss ...':self.onCommandChooseRssSource,
								}.items():
			content_menu.add_command(label = k,command = v)
			content_menu.add_separator()
		self.menubar.add_cascade(label = 'content',menu = content_menu)
		for k,v in {'interval...':self.onCommandChangeInterval
		            }.items():
			config_menu.add_command(label = k,command = v)
			config_menu.add_separator()
		self.menubar.add_cascade(label = 'config',menu = config_menu)

		self.menubar.add_cascade(label='Quit',command=self.onQuit)



		# 初始化显示文件
		self.startShow()

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
			self.logger.info("==== %d",i)
			s='panel-%d'%(i,)
			p=self.cfg.get(s,'type')
			p=self.panelFactory[p](s,self.root)
			p.loadCfg(self.cfg)
			p.applyCfg()
			self.panellist.append(p)


	def onQuit(self):
		print('onQuit')
		for p in self.panellist:
			p.saveCfg(self.cfg)

		self.cfg.write(codecs.open(self.inifile,'w',self.inifile_encoding))
		self.root.quit()
	def onCommandChangeInterval(self):
		'''设置刷新频率'''
		r=tkSimpleDialog.askinteger('change update speed','input new interval(ms) (1000-10000):',
			initialvalue=self.interval,maxvalue=10000,minvalue=1000)
		if r:
			self.interval=r
	def onCommandChooseRssSource(self):
		'''rss选择'''
		r=tkSimpleDialog.askstring('input rss url','input rss url you want to see:',
			initialvalue='http://')
		if r:
			tkMessageBox.showinfo(message=r)
			# TODO: 实现解析rss并依次显示，自己过滤/高亮指定关键字/正则的条目

	def onCommandChooseFileSource(self):
		'''文件选择'''
		oldstat=self.Stat
		if self.Stat==self.StatPlaying and self.timerid:
			self.pauseShow(self.StatPaused)
		f=tkFileDialog.askopenfilename(parent=self.root,title='choose file to show',
			filetypes=[('Text','*.txt *.log'),('Python', '*.py *.pyw'), ('All files', '*')] )
		print(f)
		if f:
			tmp=WordFile(f)
			if tkMessageBox.askyesno('confirm show','total lines %d, are you sure to show it?'%(len(tmp),),default=tkMessageBox.NO):
				self.content=tmp
				self.startShow()
				return

		if oldstat==self.StatPlaying:
			self.startShow()



	def onRightMouse(self,event):
		'''右键选择菜单'''
		self.menubar.post(event.x_root,event.y_root)

	def startShow(self):
		'''开始显示内容'''
		self.Stat=self.StatPlaying
		self.curpanel.updatePanel()

	def pauseShow(self,new_stat):
		'''暂停显示内容'''
		self.Stat=new_stat
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
			if self.Stat==self.StatPlaying:
				print('StatPlaying->StatPaused4Hover')
				self.pauseShow(self.StatPaused4Hover)
		elif event.type=='8': # Leave
			if not self.InDrag and self.Stat==self.StatPaused4Hover:
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
		if self.Stat in (self.StatPlaying,self.StatPaused4Hover):
			print('StatPlaying or StatPaused4Hover ->StatPaused')
			self.pauseShow(self.StatPaused)
		elif self.Stat==self.StatPaused:
			print('StatPaused->StatPlaying')
			self.startShow()
		elif self.Stat==self.StatStoped:
			print('StatStoped.')


	def run(self):
		self.root.mainloop()
		self.root.quit()

if __name__=='__main__':
	m=MyPanel()
	m.run()

	input('press ENTER to exit...')

