import codecs
import tkinter
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import tkinter.ttk as ttk

from util.ToolTip import ToolTip
from util.HyperlinkManager import HyperlinkManager
from util.Cfg import Cfg
from panels import RecitePanel,SubtitlePanel,ReaderPanel,DictionaryPanel
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

const.StatPlaying,const.StatStopped,const.StatPaused,const.StatPaused4Hover,const.StatDisabled=range(5)


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

		self.curpanel=self.panellist[self.c.cur_panel] # 当前使用 panel
		for i in self.panellist:
			if i!=self.curpanel:
				i.hide()


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

		for p in self.panellist:
			p.createMenu(self.menubar)
		self.menubar.add_separator()

		self.vMode=tkinter.IntVar()
		for i,p in enumerate(self.panellist):
			self.menubar.add_radiobutton(label=p.title,command=self.switchMode,value=i,variable=self.vMode)
			if p==self.curpanel:
				self.menubar.invoke(tkinter.END) # set cur panel as checked
		self.menubar.add_separator()

		self.menubar.add_cascade(label='Quit',command=self.onQuit)


	def switchMode(self):
		self.logger.info("self.vMode=%d",self.vMode.get())
		if self.curpanel and self.curpanel!=self.panellist[self.vMode.get()]:
			self.curpanel.pausePanel()
			self.curpanel.stat=const.StatDisabled
			self.curpanel.hide()
		self.curpanel=self.panellist[self.vMode.get()]
		self.curpanel.show()
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
			s='panel-%d'%(i,)
			p=self.cfg.get(s,'type')
			p=self.panelFactory[p]('%s-%s'%(s,p),s,self.root) # 建立相应panel对象
			p.loadCfg(self.cfg,s) # 由相应panel对象读取属于自己的配置
			p.applyCfg()
			self.panellist.append(p)


	def onQuit(self):
		print('onQuit')
		self.cfg.set('account','total_panel',str(self.c.total_panel))
		self.cfg.set('account','cur_panel',str(self.c.cur_panel))
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

