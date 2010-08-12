#coding=utf-8
import tkinter
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import tkinter.ttk as ttk

import json
import logging
import os
from util.ToolTip import ToolTip
from util.HyperlinkManager import HyperlinkManager
import tkinter.colorchooser as tkColorChooser
import util.const as const
from util.Cfg import Cfg
from contentcontainer import WordFile

class BasePanel(object):
	def __init__(self,name,section,root):
		self.name=name # 显示的panel名称
		self.section=section # 存取配置默认使用的section
		self.root=root
		self.logger=None # 日志对象
		self.title=None # 日志中的模块名
		self.menu=None # 本panel的菜单
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

	def hide(self):
		pass

	def show(self):
		pass

class RecitePanel(BasePanel):
	def __init__(self,name,section,root):
		BasePanel.__init__(self,name,section,root)
		self.content=None
		self.timerid=None
		self.sText=tkinter.StringVar() # label显示的内容
		self.vFile=tkinter.StringVar() # 当前显示的文件
		self.sText.set('MyPanel v0.1 powered by Python~')
		ft = tkFont.Font(family = 'Fixdsys',size = 20,weight = tkFont.BOLD)
		self.label=tkinter.Label(self.root,font=ft,relief='ridge',anchor='center',textvariable=self.sText)
		self.label.pack(expand='yes',fill=tkinter.BOTH)

		# 设置tooltip
		self.tooltiptext=tkinter.StringVar()
		ft = tkFont.Font(family = 'Fixdsys',size = 12,weight = tkFont.BOLD)
		self.tt=ToolTip(self.label,follow_mouse=0,font=ft,wraplength=self.root.winfo_screenwidth()/3,textvariable=self.tooltiptext)

		self.label.bind('<Leave>',self.onLeftMouse,'+')
		self.label.bind('<Enter>',self.onLeftMouse,'+')


	def show(self):
		self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
		self.label.pack(expand='yes',fill=tkinter.BOTH)
		self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))

	def hide(self):
		self.label.pack_forget()

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
		if not self.content:
			self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
			self.logger.info('no content to show.')
			return

		if self.timerid:
			self.label.after_cancel(self.timerid)
			self.timerid=None

		try:
			t=next(self.content)
		except StopIteration:
			print('stoped.')
			self.stat=const.StatStopped
		else:
			self.sText.set(t)
			while True:
				if self.label.winfo_reqwidth()<= self.root.winfo_screenwidth()-self.root.winfo_rootx():
					break
				t=t[:-1]
				self.sText.set(t)

			self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
			self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))
			self.logger.debug('%dx%d',self.curgeometry[0],self.curgeometry[1])
			self.tooltiptext.set('%d/%d -- %s'%(self.content.curidx,self.content.maxidx,t))
			self.c.file[self.c.cur][1]=self.content.getIdx()
			self.timerid=self.label.after(self.c.interval,self.updatePanel)

	def pausePanel(self):
		if self.timerid:
			self.label.after_cancel(self.timerid)
			self.timerid=None

	def createMenu(self,mainmenu):
		BasePanel.createMenu(self,mainmenu)
		if not self.c.enabled:
			if self.cur_list_menu:
				mainmenu.index(END)


		self.menu=tkinter.Menu(mainmenu,tearoff=False)

		self.cur_list_menu=tkinter.Menu(self.menu,tearoff=False)
		for idx,i in enumerate(self.c.file):
			self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
				value=i[0],variable=self.vFile)
			if idx==self.c.cur:
				self.cur_list_menu.invoke(idx)
		self.menu.add_cascade(label='files...',menu=self.cur_list_menu)

		for k,v,c in (('word file ...',self.onCmdChooseFile,None),
		            ('interval ...',self.onCmdChangeInterval,None),
								('bg color ...',self.onCmdChooseColor,'bg'),
								('fg color ...',self.onCmdChooseColor,'fg'),
								):
			self.menu.add_command(label = k,command = lambda v=v,c=c:v(c))
			self.menu.add_separator()
		mainmenu.add_cascade(label = '%s config'%(self.title,),menu = self.menu)

	def onCmdChooseColor(self,extra):
		self.logger.debug('extra=%s',extra)
		if extra=='bg':
			_,r=tkColorChooser.askcolor(self.c.bg,title='Choose background color')
			if r:
				self.c.bg=r
				self.label.configure(bg=self.c.bg)
		elif extra=='fg':
			_,r=tkColorChooser.askcolor(self.c.fg,title='Choose foreground color')
			if r:
				self.c.fg=r
				self.label.configure(fg=self.c.fg)


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


	def onCmdChooseFile(self,extra=None):
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
					self.cur_list_menu.add_radiobutton(label=os.path.split(i)[1],command=self.onCmdSwitchFile,
						value=i,variable=self.vFile)
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
				# 新文件入当前文件列表
				self.c.file.extend([[i,0] for i in flist])
				# 从recent中删除当前文件列表中存在的
				self.c.recent=[i for i in self.c.recent if i[0] not in (j[0] for j in self.c.file)]
				# 构造新filelist菜单
				self.c.cur=0
				for idx,i in enumerate(self.c.file):
					self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
						value=i[0],variable=self.vFile)
					if idx==self.c.cur:
						self.cur_list_menu.invoke(idx)
				self.logger.debug('replace done. new file list: %s\nnew recent: %s',self.c.file,self.c.recent)

##				self.updatePanel() # start playing anyway


	def onCmdChangeInterval(self,extra=None):
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
	def __init__(self,name,section,root):
		BasePanel.__init__(self,name,section,root)
		self.content=None
		self.timerid=None
		self.sText=tkinter.StringVar() # label显示的内容
		self.vFile=tkinter.StringVar() # 当前显示的文件
		ft = tkFont.Font(family = 'Fixdsys',size = 20,weight = tkFont.BOLD)
		self.text=tkinter.Text(self.root,font=ft,width=50,height=1,padx=2,pady=2,relief=tkinter.FLAT,takefocus=0,wrap=None,exportselection=0)
		self.text.insert(tkinter.INSERT,'MyPanel v0.1 powered by Python~')
		self.text.pack(expand='yes',fill=tkinter.BOTH)

		# 设置tooltip
		self.tooltiptext=tkinter.StringVar()
		ft = tkFont.Font(family = 'Fixdsys',size = 12,weight = tkFont.BOLD)
		self.tt=ToolTip(self.text,follow_mouse=0,font=ft,wraplength=self.root.winfo_screenwidth()/3,textvariable=self.tooltiptext)

		self.text.bind('<Leave>',self.onLeftMouse,'+')
		self.text.bind('<Enter>',self.onLeftMouse,'+')

	def show(self):
		self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()]
		self.text.pack(expand='yes',fill=tkinter.BOTH)
		self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))

	def hide(self):
		self.text.pack_forget()

	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.cur=cfg.getint(section,'cur')
		self.c.interval=cfg.getint(section,'interval')

	def applyCfg(self):
		BasePanel.applyCfg(self)
		self.text.configure(bg=self.c.bg)
		self.text.configure(fg=self.c.fg)

	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)
		if not section:
			section=self.section
		cfg.set(section,'cur',str(self.c.cur))
		cfg.set(section,'interval',str(self.c.interval))

	def updatePanel(self):
		BasePanel.updatePanel(self)
		if not self.content:
			self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()]
			self.logger.info('no content to show.')
			return
		if self.timerid:
			self.text.after_cancel(self.timerid)
			self.timerid=None

		try:
			t=next(self.content)
		except StopIteration:
			print('stoped.')
			self.stat=const.StatStopped
		else:
			self.sText.set(t)
			while True:
				if self.label.winfo_reqwidth()<= self.root.winfo_screenwidth()-self.root.winfo_rootx():
					break
				t=t[:-1]
				self.sText.set(t)

			self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
			self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))
			self.logger.debug('%dx%d',self.curgeometry[0],self.curgeometry[1])
			self.tooltiptext.set('%d/%d -- %s'%(self.content.curidx,self.content.maxidx,t))
			self.c.file[self.c.cur][1]=self.content.getIdx()
			self.timerid=self.label.after(self.c.interval,self.updatePanel)

	def pausePanel(self):
		if self.timerid:
			self.label.after_cancel(self.timerid)
			self.timerid=None

	def createMenu(self,mainmenu):
		BasePanel.createMenu(self,mainmenu)
		if not self.c.enabled:
			if self.cur_list_menu:
				mainmenu.index(END)


		self.menu=tkinter.Menu(mainmenu,tearoff=False)

		self.cur_list_menu=tkinter.Menu(self.menu,tearoff=False)
		for idx,i in enumerate(self.c.file):
			self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
				value=i[0],variable=self.vFile)
			if idx==self.c.cur:
				self.cur_list_menu.invoke(idx)
		self.menu.add_cascade(label='files...',menu=self.cur_list_menu)

		for k,v,c in (('subtitle file ...',self.onCmdChooseFile,None),
		            ('interval ...',self.onCmdChangeInterval,None),
								('bg color ...',self.onCmdChooseColor,'bg'),
								('fg color ...',self.onCmdChooseColor,'fg'),
								):
			self.menu.add_command(label = k,command = lambda v=v,c=c:v(c))
			self.menu.add_separator()
		mainmenu.add_cascade(label = '%s config '%(self.title,),menu = self.menu)

	def onCmdChooseColor(self,extra):
		self.logger.debug('extra=%s',extra)
		if extra=='bg':
			_,r=tkColorChooser.askcolor(self.c.bg,title='Choose background color')
			if r:
				self.c.bg=r
				self.text.configure(bg=self.c.bg)
		elif extra=='fg':
			_,r=tkColorChooser.askcolor(self.c.fg,title='Choose foreground color')
			if r:
				self.c.fg=r
				self.text.configure(fg=self.c.fg)


	def onCmdSwitchFile(self):
		self.logger.info('swith to file %s',self.vFile.get())
		# 获取文件对应的索引
		idx=[i for i,n in enumerate(self.c.file) if n[0]==self.vFile.get()][0]
		t=SubtitleFile(self.c.file[idx][0])
		t.setStart(self.c.file[idx][1])

		old_stat=self.stat
		if self.stat==const.StatPlaying:
			self.pausePanel()
		self.c.cur=idx
		self.content=t
		if old_stat in (const.StatPlaying,const.StatStopped) :
			self.updatePanel()


	def onCmdChooseFile(self,extra=None):
		'''文件选择'''
##		oldstat=self.stat
##		if self.stat==const.StatPlaying and self.timerid:
##			self.pauseShow(const.StatPaused)
		f=tkFileDialog.askopenfilenames(parent=self.root,title='Choose file(s) to show',
			filetypes=[('Text','*.txt *.log'),('Subtitle', '*.sub'), ('All files', '*')] )
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
				# 新文件入当前文件列表
				self.c.file.extend([[i,0] for i in flist])
				# 从recent中删除当前文件列表中存在的
				self.c.recent=[i for i in self.c.recent if i[0] not in (j[0] for j in self.c.file)]
				# 构造新filelist菜单
				self.c.cur=0
				for idx,i in enumerate(self.c.file):
					self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
						value=i[0],variable=self.vFile)
					if idx==self.c.cur:
						self.cur_list_menu.invoke(idx)
				self.logger.debug('replace done. new file list: %s\nnew recent: %s',self.c.file,self.c.recent)

##				self.updatePanel() # start playing anyway


	def onCmdChangeInterval(self,extra=None):
		'''设置刷新频率'''
		r=tkSimpleDialog.askinteger('change update speed','input new interval(ms) (1000-10000):',
			initialvalue=self.c.interval,maxvalue=10000,minvalue=1000)
		if r:
			self.c.interval=r


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

