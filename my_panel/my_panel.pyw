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
import util.lockfile

import os
import time
import sys
import imp
imp.reload(sys)
sys.setdefaultencoding('utf-8')
import configparser
import logging
import logging.config
import json
import re

# TODO: 各panel建立自己的菜单,
# 支持Drag & Drop: http://sourceforge.net/projects/tkdnd/
# 文件输入支持gzip
# dictionarypanel中正确计算texttip的位置和大小（包括拖放panel时的跟随or消失？），texttip消失的时机
# 正确显示音标
# 增加读取大字典idx文件的速度
# 查询结果根据内容智能分行(*开头.结尾)的可行性试验
# 切换不同字典时对当前suggestlist的设置是否正确？

const.StatPlaying,const.StatStopped,const.StatPaused,const.StatPaused4Hover,const.StatPaused4Switch,const.StatPaused4Data,const.StatDisabled=range(7)


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

		self.curpanel=self.panellist[self.c.cur_panel] # 当前使用 panel
		for i in self.panellist:
			if i!=self.curpanel:
				i.hide()


		self.root.wm_attributes("-topmost", 1) # set to Top Most
		# 绑定事件
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
			self.curpanel.pausePanel(const.StatDisabled)
			self.curpanel.unbindLeftMouse()
			self.curpanel.unbindLeftMouseDbClick()
			self.curpanel.hide()
		self.c.cur_panel=self.vMode.get()
		self.curpanel=self.panellist[self.c.cur_panel]
		self.curpanel.bindLeftMouse()
		self.curpanel.bindLeftMouseDbClick()
		self.curpanel.show()
		self.curpanel.updatePanel()

	def loadCfg(self):
		self.cfg=configparser.SafeConfigParser()
		self.cfg.readfp(codecs.open(self.inifile,'r',self.inifile_encoding))

		self.c.logdir=self.cfg.get('account','logdir',self.curdir)
		self.c.logsuffix=self.cfg.get('account','logsuffix','%d'%(os.getpid(),))

		self.rundate=time.strftime('%Y%m%d') # 记录执行日期

		# 读取logging配置文件
		if len(sys.argv)>1 and sys.argv[1]=='console': # 命令行中指定了输出信息到控制台
			logging_conf='logging_console.conf'
		else:
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
		self.logger.debug('onQuit')
		if self.curpanel:
			self.curpanel.pausePanel(const.StatStopped)
		self.cfg.set('account','total_panel',str(self.c.total_panel))
		self.cfg.set('account','cur_panel',str(self.c.cur_panel))
		for p in self.panellist:
			p.saveCfg(self.cfg)

		for p in self.panellist:
			p.setExit()

		self.cfg.write(codecs.open(self.inifile,'w',self.inifile_encoding))
		self.root.quit()
	def onRightMouse(self,event):
		'''右键选择菜单'''
		self.menubar.post(event.x_root,event.y_root)


	def run(self):
		self.root.mainloop()
		self.root.quit()

if __name__=='__main__':
	locker = util.lockfile.LockFile(os.path.join(os.path.abspath('.'),'locked.txt'))
	try:
		locker.lock()
	except Exception:
##		print ('program have already run')
		sys.exit()
	else:
##		print ('successful')
		m=MyPanelApp()
		m.run()

	input('press ENTER to exit...')

