#coding=utf-8
import tkinter
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
##import tkinter.ttk as ttk

import json
import logging
import os
import datetime
import time
import webbrowser
import xml.sax.saxutils
from _thread import start_new_thread
import subprocess

from util.ToolTip import ToolTip
from util.HyperlinkManager import HyperlinkManager
import tkinter.colorchooser as tkColorChooser
import util.const as const
from util.Cfg import Cfg
from util.AutoComplete import AutoComplete
from util.MeaningTip import MeaningTip
from contentcontainer import WordFile
from contentcontainer import SubtitleFile
from contentcontainer import StartDictFile
from contentcontainer import RSSFile
import util.Tts


class BasePanel(object):
	def __init__(self,name,section,root):
		self.name=name # 显示的panel名称
		self.section=section # 存取配置默认使用的section
		self.root=root
		self.logger=None # 日志对象
		self.menu=None # 本panel的菜单
		self.cur_list_menu=None # 显示当前的 文件/源/字典 列表
		self.recent_list_menu=None # 显示最近的 文件/源/字典 列表
		self.draggableCtrl=None # 可用于拖放的widget
		self.c=Cfg()

		self.tooltiptext=None
		self.stat=None

		# 处理窗口拖动
		self.InDrag=False
		self.oldxy=[0,0]
		self.curgeometry=[320,240]
		self.offsetx,self.offsety=0,0 # 被拖动的widget距离(top,left)的值

		# TTS
##		self.tts=None
		self.tts=util.Tts.TtsVoice()
		self.tts_stat=tkinter.IntVar()

	def bindLeftMouse(self):
		self.logger.info('bind leftmouse')
		self.draggableCtrl.bind('<ButtonPress-1>', self.onLeftMouse,add='+')
		self.draggableCtrl.bind('<ButtonRelease-1>',self.onLeftMouse)
		self.draggableCtrl.bind('<Motion>',self.onLeftMouse,add='+')
		self.draggableCtrl.bind('<Leave>',self.onLeftMouse,add='+')
		self.draggableCtrl.bind('<Enter>',self.onLeftMouse,add='+')

	def bindLeftMouseDbClick(self):
		self.logger.info('bind leftmouse db click')
		self.draggableCtrl.bind('<Double-Button-1>',self.onLeftMouseDbClick)

	def unbindLeftMouse(self):
		self.logger.info('unbind leftmouse')
		self.draggableCtrl.unbind('<ButtonPress-1>')
		self.draggableCtrl.unbind('<ButtonRelease-1>')
		self.draggableCtrl.unbind('<Motion>')
		self.draggableCtrl.unbind('<Leave>')
		self.draggableCtrl.unbind('<Enter>')
##		self.draggableCtrl.unbind('<ButtonPress-1>', self.onLeftMouse)
##		self.draggableCtrl.unbind('<ButtonRelease-1>',self.onLeftMouse)
##		self.draggableCtrl.unbind('<Motion>',self.onLeftMouse)
##		self.draggableCtrl.unbind('<Leave>',self.onLeftMouse)
##		self.draggableCtrl.unbind('<Enter>',self.onLeftMouse)

	def unbindLeftMouseDbClick(self):
		self.logger.info('unbind leftmouse db click')
##		self.draggableCtrl.unbind('<Double-Button-1>',self.onLeftMouseDbClick)
		self.draggableCtrl.unbind('<Double-Button-1>')

	def onLeftMouse(self,event):
		'''处理窗体拖放、内容暂停/恢复'''
		if event.type=='6': # Motion
			if self.InDrag:
##				self.logger.info('offsetxy=(%d,%d)',self.offsetx,self.offsety)
				xmvto=event.x_root-self.oldxy[0]-self.offsetx
				ymvto=event.y_root-self.oldxy[1]-self.offsety
##				self.logger.debug('Motion at (%d,%d) +%d+%d'%(event.x,event.y,xmvto,ymvto))
				self.c.position='+%d+%d'%(xmvto,ymvto)
				self.root.geometry('%dx%d%s'%(self.curgeometry[0],self.curgeometry[1],self.c.position))
		elif event.type=='7': # Enter
			self.root.attributes("-alpha", 1) # use transparency level 0.1 to 1.0 (no transparency)
			if self.stat==const.StatPlaying:
				self.logger.debug('StatPlaying->StatPaused4Hover')
				self.pausePanel(const.StatPaused4Hover)
		elif event.type=='8': # Leave
			self.root.attributes("-alpha", self.c.alpha) # use transparency level 0.1 to 1.0 (no transparency)
			if not self.InDrag and self.stat==const.StatPaused4Hover:
				self.logger.debug('StatPaused4Hover->StatPlaying')
				self.updatePanel()
		elif event.type=='4': # ButtonPress
			if not self.InDrag:
				self.logger.debug('ButtonPress at (%d,%d)-(%dx%d)'%(event.x,event.y,event.x_root,event.y_root))
				self.InDrag=True
				self.oldxy=[event.x,event.y]
		elif event.type=='5': # ButtonRelease
			if self.InDrag:
##				self.logger.debug('ButtonRelease at (%d,%d)'%(event.x,event.y))
				self.InDrag=False
		else:
			self.logger.debug(event.type)
			self.logger.debug('in onLeftMouse (%d,%d)'%(event.x,event.y))

	def onLeftMouseDbClick(self,event):
		'''暂停/继续'''
		if self.stat in (const.StatPlaying,const.StatPaused4Hover):
			self.logger.debug('StatPlaying or StatPaused4Hover ->StatPaused')
			self.pausePanel(const.StatPaused)
		elif self.stat==const.StatPaused:
			self.logger.debug('StatPaused->StatPlaying')
			self.updatePanel()
		elif self.stat==const.StatStopped:
			self.logger.debug('StatStopped->StatPlaying')
			self.updatePanel()

	def loadCfg(self,cfg,section=None):
		if not section:
			section=self.section
		self.c.title=cfg.get(section,'title','unknown') # 日志中的模块名
		self.c.enabled=cfg.getboolean(section,'enabled')
		self.c.position=cfg.get(section,'position')
		self.c.file=json.JSONDecoder().decode(cfg.get(section,'file'))
		self.c.alpha=cfg.getfloat(section,'alpha')
		self.c.fg=cfg.get(section,'fg')
		self.c.bg=cfg.get(section,'bg')
		self.c.tts_read=cfg.getboolean(section,'tts_read')
		self.c.tts_chinese_voice=cfg.get(section,'tts_chinese_voice')
		self.c.tts_english_voice=cfg.get(section,'tts_english_voice')
		self.c.recent=json.JSONDecoder().decode(cfg.get(section,'recent'))

	def applyCfg(self):
		self.logger=logging.getLogger(self.c.title)
		self.root.attributes("-alpha", self.c.alpha) # use transparency level 0.1 to 1.0 (no transparency)

		# TTS
		self.tts.setVoiceCharacter(self.c.tts_chinese_voice,self.c.tts_english_voice)

	def saveCfg(self,cfg,section=None):
		if not section:
			section=self.section
		cfg.set(section,'title',self.c.title)
		cfg.set(section,'enabled',str(self.c.enabled))
		cfg.set(section,'position',self.c.position)
		cfg.set(section,'file',json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.c.file).replace(',[',',\n['))
		cfg.set(section,'alpha',str(self.c.alpha))
		cfg.set(section,'fg',str(self.c.fg))
		cfg.set(section,'bg',str(self.c.bg))
		cfg.set(section,'tts_read',str(self.c.tts_read))
		cfg.set(section,'tts_chinese_voice',self.c.tts_chinese_voice)
		cfg.set(section,'tts_english_voice',self.c.tts_english_voice)
		cfg.set(section,'recent',json.JSONEncoder(ensure_ascii =False,separators=(',', ':')).encode(self.c.recent).replace(',[',',\n['))

	def pausePanel(self,new_stat):
		self.stat=new_stat

	def updatePanel(self):
		self.stat=const.StatPlaying

	def createMenu(self,mainmenu):
		self.menu=tkinter.Menu(mainmenu,tearoff=False)

		# TTS
		self.tts_stat.set(1 if self.c.tts_read else 0)
		self.menu.add_checkbutton(label= 'TTS Voice',variable=self.tts_stat,command = lambda v=self.onCmdToggleTts,c=None:v(c))
		self.menu.add_separator()

	def onCmdToggleTts(self,extra=None):
		self.c.tts_read=(True if self.tts_stat.get()==1 else False)
		self.logger.debug('now self.c.tts_read=%s',self.c.tts_read)



	def hide(self):
		pass

	def show(self):
		self.root.attributes("-alpha", self.c.alpha) # use transparency level 0.1 to 1.0 (no transparency)

	def setExit(self):
		if self.c.tts_read and self.tts:
			self.tts.stop()
		pass

	@property
	def title(self):
		return self.c.title
	@property
	def sectionname(self):
		return self.section

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
		self.label.pack(expand=True,fill=tkinter.BOTH)
		self.draggableCtrl=self.label

		self.curContent=None # 当前显示的文字

		# 设置tooltip
		self.tooltiptext=tkinter.StringVar()
		ft = tkFont.Font(family = 'Fixdsys',size = 12,weight = tkFont.BOLD)
		self.tt=ToolTip(self.label,follow_mouse=0,font=ft,wraplength=self.root.winfo_screenwidth()/3,textvariable=self.tooltiptext)

##		self.label.bind('<Leave>',self.onLeftMouse,'+')
##		self.label.bind('<Enter>',self.onLeftMouse,'+')



	def show(self):
		BasePanel.show(self)
		self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
		self.label.pack(expand=True,fill=tkinter.BOTH)
		self.root.geometry('%dx%d%s'%(self.curgeometry[0],self.curgeometry[1],self.c.position))

	def hide(self):
		BasePanel.hide(self)
		self.label.pack_forget()

	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.interval=cfg.getint(section,'interval')
		self.c.cur=cfg.getint(section,'cur')
		self.c.recent_dir=cfg.get(section,'recent_dir')

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

	def showNext(self):
		if not self.content:
			self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()]
			self.logger.info('no content to show.')
			return
		if self.timerid:
			self.label.after_cancel(self.timerid)
			self.timerid=None

		# TTS
		if self.c.tts_read and self.tts:
			if self.tts.isSpeaking():
				self.timerid=self.label.after(300,self.showNext)
				return

		oldstat=self.stat
		try:
			self.stat=const.StatPaused4Data
			t=next(self.content)
			self.stat=oldstat
		except StopIteration:
			self.logger.debug('stoped.')

			self.curContent='no content to show.'
			self.updatePanel()
			self.pausePanel(const.StatStopped)
		else:
			self.curContent=t

			# TTS
			if self.c.tts_read and self.tts:
##				tmp=self.tts.Q2B(t)
				if t.find(' ')!=-1:
					self.tts.Speak(t[t.find(' '):])
				else:
					self.tts.Speak(t)

			self.stat=const.StatPlaying

			self.tooltiptext.set('%d/%d -- %s'%(self.content.curidx,self.content.maxidx,t))
			self.c.file[self.c.cur][1]=self.content.getIdx()
			self.updatePanel()


	def updatePanel(self):
		BasePanel.updatePanel(self)

		if self.curContent is None:
			self.timerid=self.label.after(10,self.showNext)
			return

		self.sText.set(self.curContent)
		t=self.curContent[:]
		while True:
			if self.label.winfo_reqwidth()<= self.root.winfo_screenwidth()-self.root.winfo_rootx():
				break
			t=t[:-1]
			self.sText.set(t)

		self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
		self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))
##		self.logger.debug('%dx%d',self.curgeometry[0],self.curgeometry[1])
		self.timerid=self.label.after(self.c.interval,self.showNext)

	def pausePanel(self,new_stat):
		BasePanel.pausePanel(self,new_stat)
		if self.timerid:
			self.label.after_cancel(self.timerid)
			self.timerid=None

	def createMenu(self,mainmenu):
		BasePanel.createMenu(self,mainmenu)
		if not self.c.enabled:
			return

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
			self.pausePanel(const.StatPaused4Data)
		self.c.cur=idx
		self.content=t
		if old_stat in (const.StatPlaying,const.StatStopped) :
			self.showNext()


	def onCmdChooseFile(self,extra=None):
		'''文件选择'''
##		oldstat=self.stat
##		if self.stat==const.StatPlaying and self.timerid:
##			self.pauseShow(const.StatPaused)
		f=tkFileDialog.askopenfilenames(parent=self.root,title='Choose file(s) to show',
			initialdir=self.c.recent_dir,
			filetypes=[('Text','*.txt *.log'),('Python', '*.py *.pyw'), ('All files', '*')] )
		if f:
			flist=self.root.tk.splitlist(f) # http://psf.upfronthosting.co.za/roundup/tracker/issue5712 workaround: http://code.activestate.com/lists/python-tkinter-discuss/2016/
			if len(flist)>5:
				self.logger.info('一次最多添加5个文件，多余的会被丢弃，你选择了 %d个',len(flist))
				flist=flist[:5]
			for i,onefile in enumerate(flist):
				self.logger.debug('multi file %02d/%d: %s',i,len(flist),onefile)

			addorreplace=tkMessageBox.askyesnocancel('Add or replace','add the file(s) to your file list? (press "no" will replace current file list)',default=tkMessageBox.YES)
			self.logger.debug('addorreplace=%s',addorreplace)
			self.c.recent_dir=os.path.split(flist[0])[0]
			if addorreplace==None:
				self.logger.debug('do nothing')
			elif addorreplace==True: # add
				self.c.file.extend([i,0] for i in flist)
				# 更新filelist菜单
				for i in flist:
					self.cur_list_menu.add_radiobutton(label=os.path.basename(i),command=self.onCmdSwitchFile,
						value=i,variable=self.vFile)
				# 从recent中删除当前文件列表中存在的
				self.c.recent=[i for i in self.c.recent if i[0] not in (j[0] for j in self.c.file)]
				self.logger.debug('add done. new file list: %s',self.c.file)

			elif addorreplace==False: # replace
				if self.stat==const.StatPlaying:
					self.pausePanel(const.StatPaused4Switch)

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
		cfg.set(section,'recent_dir',self.c.recent_dir)

class SubtitlePanel(BasePanel):
	def __init__(self,name,section,root):
		BasePanel.__init__(self,name,section,root)
		self.content=None
		self.timerid=None
		self.vFile=tkinter.StringVar() # 当前显示的文件
		self.ft = tkFont.Font(family = 'Fixdsys',size = 20,weight = tkFont.BOLD)
		self.text=tkinter.Text(self.root,font=self.ft,width=50,height=1,padx=2,pady=2,relief=tkinter.FLAT,takefocus=0,wrap=None,exportselection=0,cursor='left_ptr')
##		self.logger.debug('=%d'%(self.text.winfo_reqheight(),))
		self.text.insert(tkinter.INSERT,'MyPanel v0.1 powered by Python~')
		self.text.pack(expand=tkinter.YES,fill=tkinter.BOTH)
		self.draggableCtrl=self.text

		self.curContent=None # 当前要显示的文字

		# 设置tooltip
		self.tooltiptext=tkinter.StringVar()
		ft = tkFont.Font(family = 'Fixdsys',size = 12,weight = tkFont.BOLD)
		self.tt=ToolTip(self.text,follow_mouse=0,font=ft,wraplength=self.root.winfo_screenwidth()/3,textvariable=self.tooltiptext)

##		self.text.bind('<Leave>',self.onLeftMouse,'+')
##		self.text.bind('<Enter>',self.onLeftMouse,'+')

	def show(self):
		BasePanel.show(self)
		self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()]
		self.text.pack(expand=True,fill=tkinter.BOTH)
		self.root.geometry('%dx%d%s'%(self.curgeometry[0],self.curgeometry[1],self.c.position))

	def hide(self):
		BasePanel.hide(self)
		self.text.pack_forget()

	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.cur=cfg.getint(section,'cur')
		self.c.interval=cfg.getint(section,'interval')
		self.c.recent_dir=cfg.get(section,'recent_dir')

	def applyCfg(self):
		BasePanel.applyCfg(self)
		self.text.configure(bg=self.c.bg,fg=self.c.fg)
		self.text.configure(selectbackground=self.c.bg,selectforeground=self.c.fg,selectborderwidth=0)

	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)
		if not section:
			section=self.section
		cfg.set(section,'cur',str(self.c.cur))
		cfg.set(section,'interval',str(self.c.interval))
		cfg.set(section,'recent_dir',self.c.recent_dir)

	def showNext(self):
		if not self.content:
			self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()]
			self.logger.info('no content to show.')
			return
		if self.timerid:
			self.text.after_cancel(self.timerid)
			self.timerid=None

		# TTS
		if self.c.tts_read and self.tts:
			if self.tts.isSpeaking():
				self.timerid=self.text.after(300,self.showNext)
				return

		oldstat=self.stat
		try:
			self.stat=const.StatPaused4Data
			t=next(self.content)
			self.stat=oldstat
		except StopIteration:
			self.logger.debug('stoped.')

			self.curContent='no content to show.'
			self.updatePanel()
			self.pausePanel(const.StatStopped)
		else:
			self.curContent=t

			# TTS
			if self.c.tts_read and self.tts:
##				tmp=self.tts.Q2B(t)
				if t.find(' ')!=-1:
					self.tts.Speak(t[t.find(' '):])
				else:
					self.tts.Speak(t)

			self.stat=const.StatPlaying

			self.tooltiptext.set('%d/%d -- %s'%(self.content.curidx,self.content.maxidx,self.curContent))
			self.c.file[self.c.cur][1]=self.content.getIdx()

			self.updatePanel()

	def updatePanel(self):
		BasePanel.updatePanel(self)

		if self.curContent is None:
			self.timerid=self.text.after(10,self.showNext)
			return

		lines=self.curContent.split(os.linesep)
		linecnt=len(lines) # 行数

		maxwidth=max((self.ft.measure(i) for i in lines)) # 最大行需要宽度
		maxwidth+=2+2+2+2 # 总宽度 (算上两边的 paddingx + borderwidth)

		max_width_allowed=self.root.winfo_screenwidth()-self.root.winfo_rootx() # 最大允许总宽度：不超过屏幕最右边

		if maxwidth>max_width_allowed: # 需要调整
			maxwidth=max_width_allowed
			linecnt=0
			maxwidth_text=max_width_allowed-2-2-2-2
			# 判断需要多少行
			for i in lines:
				# 每行需要拆为多少行
				tmp=i[:]
				while tmp:
					while self.ft.measure(tmp) >maxwidth_text:
						tmp=tmp[:-1]
					linecnt+=1
					i=i[len(tmp):]
					tmp=i[:]

		self.text.config(state=tkinter.NORMAL)
		self.text.delete('0.0',tkinter.END)
		self.text.insert(tkinter.INSERT,self.curContent)
		self.text.config(state=tkinter.DISABLED)

##		self.logger.info('font linespace=%d, text.winfo_reqheight()=%d',self.ft.metrics("linespace"),self.text.winfo_reqheight())
##		x=self.text.winfo_reqheight()-self.ft.metrics("linespace")

##		self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()*len(lines)]
##		self.curgeometry=[maxwidth,self.text.winfo_reqheight()*linecnt-linecnt*4]
##		self.curgeometry=[maxwidth,(self.text.winfo_reqheight()-x)*linecnt-x]
		self.curgeometry=[maxwidth,linecnt*self.ft.metrics('linespace')+self.ft.metrics('descent')]
		self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))
##		self.text.see('end')
		self.logger.debug('%dx%d ,lines=%d,maxlinelength=%d',self.curgeometry[0],self.curgeometry[1],linecnt,maxwidth)
		self.timerid=self.text.after(self.c.interval,self.showNext)

	def pausePanel(self,new_stat):
		BasePanel.pausePanel(self,new_stat)
		if self.timerid:
			self.text.after_cancel(self.timerid)
			self.timerid=None

	def createMenu(self,mainmenu):
		BasePanel.createMenu(self,mainmenu)
		if not self.c.enabled:
			return

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
			self.pausePanel(const.StatPaused4Switch)
		self.c.cur=idx
		self.content=t
		if old_stat in (const.StatPlaying,const.StatStopped) :
			self.showNext()


	def onCmdChooseFile(self,extra=None):
		'''文件选择'''
##		oldstat=self.stat
##		if self.stat==const.StatPlaying and self.timerid:
##			self.pauseShow(const.StatPaused)
		f=tkFileDialog.askopenfilenames(parent=self.root,title='Choose file(s) to show',
			initialdir=self.c.recent_dir,
			filetypes=[('Text','*.txt *.log'),('Subtitle', '*.sub'), ('All files', '*')] )
		if f:
			flist=self.root.tk.splitlist(f) # http://psf.upfronthosting.co.za/roundup/tracker/issue5712 workaround: http://code.activestate.com/lists/python-tkinter-discuss/2016/
			if len(flist)>5:
				self.logger.info('一次最多添加5个文件，多余的会被丢弃，你选择了 %d个',len(flist))
				flist=flist[:5]
			for i,onefile in enumerate(flist):
				self.logger.debug('multi file %02d/%d: %s',i,len(flist),onefile)

			addorreplace=tkMessageBox.askyesnocancel('Add or replace','add the file(s) to your file list? (press "no" will replace current file list)',default=tkMessageBox.YES)
			self.logger.debug('addorreplace=%s',addorreplace)
			self.c.recent_dir=os.path.split(flist[0])[0]
			if addorreplace==None:
				self.logger.debug('do nothing')
			elif addorreplace==True: # add
				self.c.file.extend([i,0] for i in flist)
				# 更新filelist菜单
				for i in flist:
					self.cur_list_menu.add_radiobutton(label=os.path.basename(i),command=self.onCmdSwitchFile,
						value=i,variable=self.vFile)
				# 从recent中删除当前文件列表中存在的
				self.c.recent=[i for i in self.c.recent if i[0] not in (j[0] for j in self.c.file)]
				self.logger.debug('add done. new file list: %s',self.c.file)
			elif addorreplace==False: # replace
				if self.stat==const.StatPlaying:
					self.pausePanel(const.StatPaused4Switch)

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
	def __init__(self,name,section,root):
		BasePanel.__init__(self,name,section,root)

		self.content=None # 内容容器
##		self.curContent={'google_id':'0',
##		                 'published':time.time(),
##		                 'link':'http://code.google.com/p/mytestzone/',
##		                 'title':'my_panel rss panel, loading ...',
##		                 'content':'my_panel 1.0~',
##		                 'author':'kevin'
##		                 } # 当前显示的item
		self.startContent={'id':'0',
		                 'alternate':[{'href':'http://code.google.com/p/mytestzone/','type':'text/html'},],
		                 'published':time.time(),
##		                 'link':'http://code.google.com/p/mytestzone/',
		                 'title':'rss panel, loading data ...',
		                 'summary':{'content':'my_panel 1.0~','direction':'ltr'},
		                 'origin':{'streamId':0,'title':'No'},
		                 'my':{'pos':-1,'removed':True},
##		                 'content':'my_panel 1.0~',
		                 'author':'kevin'
		                 } # 当前显示的item
		self.curContent=self.startContent.copy()
		self.timerid=None
		self.text_tag='tag-rss'
		self.ft = tkFont.Font(family = 'Fixdsys',size = 20,weight = tkFont.BOLD)
		self.text=tkinter.Text(self.root,font=self.ft,width=50,height=1,padx=2,pady=2,relief=tkinter.FLAT,takefocus=0,wrap=None,exportselection=0,cursor='left_ptr')
##		self.logger.debug('=%d'%(self.text.winfo_reqheight(),))
		self.text.insert(tkinter.INSERT,'MyPanel v0.1 powered by Python~')
		self.text.pack(expand=tkinter.YES,fill=tkinter.BOTH)
		self.draggableCtrl=self.text

		self.hl=HyperlinkManager(self.text)
		self.iconLink=tkinter.PhotoImage(file=os.path.join(os.path.join(os.path.abspath('.'),'icon'),'link.gif'))

		# 设置tooltip
		self.tooltiptext=tkinter.StringVar()
		ft = tkFont.Font(family = 'Fixdsys',size = 12,weight = tkFont.BOLD)
		self.tt=ToolTip(self.text,follow_mouse=0,font=ft,wraplength=self.root.winfo_screenwidth()/3,textvariable=self.tooltiptext)

##		self.mtft = tkFont.Font(family = 'Fixdsys',size = 12) # meaningtip字体
##		self.mt=MeaningTip(self.text,font=self.mtft) # 显示摘要

		self.hm=HyperlinkManager(self.text)

		self.flag4stat='>' # 通过不同字符在UI上表示暂停和继续两种状态

	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.cur=cfg.getint(section,'cur')
		self.c.interval=cfg.getint(section,'interval')
		self.c.check_interval=cfg.get(section,'check_interval',900)
		self.c.email=cfg.get(section,'email')
		self.c.pwd=cfg.get(section,'pwd')
		self.c.cookiefile=cfg.get(section,'cookiefile')
		if not os.path.isabs(self.c.cookiefile):
			self.c.cookiefile=os.path.join(os.path.abspath('.'),self.c.cookiefile)
		self.c.auth=cfg.get(section,'auth','')
		self.c.browser2use=cfg.get(section,'browser2use',None)
		self.c.excludewords=json.JSONDecoder().decode(cfg.get(section,'excludewords'))
		self.c.highlightwords=json.JSONDecoder().decode(cfg.get(section,'highlightwords'))
		self.c.hideduplicate=cfg.getboolean(section,'hideduplicate')

	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)
		if not section:
			section=self.section
		cfg.set(section,'cur',str(self.c.cur))
		cfg.set(section,'interval',str(self.c.interval))
		cfg.set(section,'check_interval',str(self.c.check_interval))
		cfg.set(section,'email',self.c.email)
		cfg.set(section,'pwd',self.c.pwd)
		cfg.set(section,'cookiefile',self.c.cookiefile)
		self.c.auth=self.content.getAuthInfo()
		cfg.set(section,'auth',self.c.auth)
		cfg.set(section,'browser2use',self.c.browser2use)

	def applyCfg(self):
		BasePanel.applyCfg(self)
		self.content=RSSFile(self.c.email,self.c.pwd,self.c.cookiefile)
		if self.c.auth:
			self.content.setAuthInfo(self.c.auth)
		self.text.configure(fg=self.c.fg,bg=self.c.bg)
		self.text.configure(selectbackground=self.c.bg,selectforeground=self.c.fg,selectborderwidth=0)

	def onCmdChooseRss(self):
		'''rss选择'''
		r=tkSimpleDialog.askstring('Input rss url','input rss url you want to read:',
			initialvalue='http://')
		if r:
			tkMessageBox.showinfo(message=r)
			# TODO: 实现解析rss并依次显示，自己过滤/高亮指定关键字/正则的条目

	def createMenu(self,mainmenu):
		BasePanel.createMenu(self,mainmenu)
		if not self.c.enabled:
			return

		self.cur_list_menu=tkinter.Menu(self.menu,tearoff=False)
		for idx,i in enumerate(self.c.file):
			self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
				value=i[0],variable=self.vFile)
			if idx==self.c.cur:
				self.cur_list_menu.invoke(idx)
		self.menu.add_cascade(label='files...',menu=self.cur_list_menu)

		for k,v,c in (
								('bg color ...',self.onCmdChooseColor,'bg'),
								('fg color ...',self.onCmdChooseColor,'fg'),
		            ('interval ...',self.onCmdChangeInterval,None),
		            ('refresh',self.onCmdGetRss,None),
								):
			self.menu.add_command(label = k,command = lambda v=v,c=c:v(c))
			self.menu.add_separator()
		mainmenu.add_cascade(label = '%s config '%(self.title,),menu = self.menu)

	def show(self):
		BasePanel.show(self)
		self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()]
		self.text.pack(expand=True,fill=tkinter.BOTH)
		self.root.geometry('%dx%d%s'%(self.curgeometry[0],self.curgeometry[1],self.c.position))

	def hide(self):
		BasePanel.hide(self)
		self.text.pack_forget()

	def showNext(self):
		# TTS
		if self.c.tts_read and self.tts:
			if self.curContent['id']!=self.startContent['id']: # 是真实条目而非起始页
				if not self.curContent['my']['removed']: # 并非是因为用户点击图标而跳到下一个
					if self.tts.isSpeaking():
						self.timerid=self.text.after(300,self.showNext)
						return
				else: # 用户点击图标而跳到下一个，则跳过当前文本朗读
					self.tts.Skip()

##		if self.curContent['id']!=self.startContent['id'] and (not self.curContent['my']['removed']):
##			self.logger.debug('del cur item before showNext')
##			self.content.setEditItem({'a':'read','i':self.curContent['id'],'pos':self.curContent['my']['pos'],'s':self.curContent['origin']['streamId']})

		oldstat=self.stat
		try:
			self.stat=const.StatPaused4Data
			t=next(self.content)
			self.stat=oldstat
		except StopIteration:
			self.logger.debug('stoped.')
##			self.stat=const.StatStopped

##			if self.curContent['id']==self.startContent['id']:
			self.curContent=self.startContent.copy()
			self.curContent['title']='rss panel, no rss item unread.'
			self.updatePanel()
			self.pausePanel(const.StatStopped)
		else:
			# TODO: 重复标题检查
			# 高亮检查
			# 排除检查

			t['my']={'removed':False,'pos':self.content.getIdx()}
			self.curContent=t

			# TTS
			if self.c.tts_read and self.tts:
				self.tts.Speak(t['title'],util.Tts.SVSFlagsAsync|util.Tts.SVSFPurgeBeforeSpeak)

			self.stat=const.StatPlaying
			self.updatePanel()

	def updatePanel(self):
		BasePanel.updatePanel(self)

		progress='[%s%s%d]'%(str(self.curContent['my']['pos']+1).rjust(len(str(self.content.getActualMax()))),
		                    self.flag4stat,
		                    self.content.getActualMax())
		self.flag4stat='>'


		maxwidth=self.ft.measure(progress+self.curContent['title']+' ') # 最大行需要宽度
		linecnt=1
		# 计算行数
		maxwidth+=2+2+2+2 # 总宽度 (算上两边的 paddingx + borderwidth)
		max_width_allowed=self.root.winfo_screenwidth()-self.root.winfo_rootx() # 最大允许总宽度：不超过屏幕最右边
		if maxwidth>max_width_allowed: # 需要调整
			maxwidth=max_width_allowed
			linecnt=0
			maxwidth_text=max_width_allowed-2-2-2-2
			# 判断需要多少行
			for i in [progress+self.curContent['title']+' ',]:#lines:
				# 每行需要拆为多少行
				tmp=i[:]
				while tmp:
					while self.ft.measure(tmp) >maxwidth_text:
						tmp=tmp[:-1]
					linecnt+=1
					i=i[len(tmp):]
					tmp=i[:]

		self.text.config(state=tkinter.NORMAL)
		self.text.delete('0.0',tkinter.END)

##		self.logger.debug('%s',self.curContent['title'])
		self.text.insert(tkinter.INSERT,progress)
##		self.text.insert(tkinter.INSERT,self.curContent['title'],self.hm.add(lambda ev,c=self.curContent.get('summary',{'content':'None','direction':'ltr'}):self.onCmdShowSummary(ev,summary=c)))
		tmp=self.text.index(tkinter.INSERT)
		self.text.image_create(tkinter.INSERT,image=self.iconLink)
		self.text.tag_delete(self.text_tag) # 删掉原tag
		self.text.tag_add(self.text_tag,tmp) # 添加图标对应的tag
##		self.text.tag_config(self.text_tag,background='#00ff00',bgstipple='gray25',relief=tkinter.GROOVE)
		self.text.tag_bind(self.text_tag,'<Enter>',self._enter,add='+')
		self.text.tag_bind(self.text_tag,'<Leave>',self._leave,add='+')
		self.text.tag_bind(self.text_tag,'<Button-1>',
		                   lambda ev,a='read',cid=self.curContent['id'],cpos=self.curContent['my']['pos'],cs=self.curContent['origin']['streamId']:self.onCmdClickIcon(ev,a=a,i=cid,pos=cpos,s=cs),add='+')

		self.text.insert(tkinter.INSERT,self.curContent['title'],self.hm.add(lambda ev,c=self.curContent['alternate'][0]['href']:self.onCmdOpenUrl(ev,url=c)))

		self.text.config(state=tkinter.DISABLED)
		# 设tooltip
		self.tooltiptext.set('published: %s by %s\nKind: %s\n%s'%(
		  datetime.datetime.fromtimestamp(self.curContent['published']).strftime("%Y-%m-%d %H:%M:%S"),
		  self.curContent.get('author','None'),
		  self.curContent['origin']['title'],
      self.curContent['summary']['content'][:500] if 'summary' in self.curContent else 'No Summary' # 最多显示500个字符
		  ))

##		self.curgeometry=[self.text.winfo_reqwidth(),self.text.winfo_reqheight()]
		self.curgeometry=[maxwidth,linecnt*self.ft.metrics('linespace')+self.ft.metrics('descent')]
		self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))
		self.timerid=self.text.after(self.c.interval,self.showNext)

	def onCmdOpenUrl(self,event,**kwargs):
		url=xml.sax.saxutils.unescape(kwargs['url'])
		self.logger.debug('open %s ...',url)
		if self.c.browser2use:
			start_new_thread(subprocess.Popen,([self.c.browser2use,url],),{'shell':False})
##			start_new_thread(os.system,('%s %s'%(self.c.browser2use,url),))
##			os.system('%s %s'%(self.c.browser2use,url))
		else:
			webbrowser.open_new_tab(url)

	def onCmdShowSummary(self,event,**kwargs):
		pass
##		self.logger.debug('%s event %s show content for %s',self,event,kwargs)
##		self.mt.show(kwargs['summary']['content'])

	def onCmdClickIcon(self,event,**kwargs):
##		self.logger.debug('%s event %s for %s',self,event,kwargs)
		if event.state&0x0001: # TODO: 点击的同时按下SHIFT，表示相同标题的也一并过滤
			pass
##			self.logger.debug('Shift pressed')
		if kwargs['i']==0:
			self.logger.debug('not really rss item,ignore')
			return
		elif self.curContent['my']['removed']:
			self.logger.debug('already marked removed.')
			return
		self.content.setEditItem({'a':kwargs['a'],'i':kwargs['i'],'pos':kwargs['pos'],'s':kwargs['s']})
		self.curContent['my']['removed']=True

		self.pausePanel(const.StatPaused)
		self.showNext()
		self.pausePanel(const.StatPaused4Hover)

	def _enter(self, event):
##		self.logger.debug('~~')
		self.text.config(cursor="X_cursor")
	def _leave(self, event):
##		self.logger.debug('``')
		self.text.config(cursor="")

	def pausePanel(self,new_stat):
		BasePanel.pausePanel(self,new_stat)
##		self.logger.debug('paused, %s,timerid=%s',new_stat,self.timerid)
		if self.timerid:
			self.text.after_cancel(self.timerid)
			self.timerid=None

		# 在UI上标识出暂停状态
		if self.stat==const.StatPaused:
##			self.logger.debug('to show paused icon???')
			self.flag4stat='|'
			self.updatePanel() # 为了显示暂停状态而额外刷新一次
			BasePanel.pausePanel(self,new_stat)
			if self.timerid:
				self.text.after_cancel(self.timerid)
				self.timerid=None


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
		# TODO: 完成正确代码
		self.logger.info('swith to dictionary file %s',self.vFile.get())
		# 获取文件对应的索引
		idx=[i for i,n in enumerate(self.c.file) if n[0]==self.vFile.get()][0]
		self.c.cur=idx
		self.cur_dict=StartDictFile(self.c.file[self.c.cur][0])
		self.cur_dict.readIFO()
		self.cur_dict.readIDX()
		self.ac.setSuggestContent(self.cur_dict.getIdxList())

	def onCmdChangeInterval(self,extra=None):
		'''设置刷新频率'''
		r=tkSimpleDialog.askinteger('change update speed','input new interval(ms) (1000-10000):',
			initialvalue=self.c.interval,maxvalue=10000,minvalue=1000)
		if r:
			self.c.interval=r

	def setExit(self):
		BasePanel.setExit(self)
		self.content.setExit()

	def onCmdGetRss(self,extra):
		self.pausePanel(const.StatPaused4Switch)
		self.content.reset()
		self.curContent=self.startContent.copy()
		self.updatePanel()




class DictionaryPanel(BasePanel):
	def __init__(self,name,section,root):
		BasePanel.__init__(self,name,section,root)
		self.vInput=tkinter.StringVar()
		self.cur_dict=None
		self.vFile=tkinter.StringVar() # 当前显示的文件
		self.container=tkinter.Frame(root,bd=0,padx=0,pady=0,relief=tkinter.RIDGE)
		self.ft = tkFont.Font(family = 'Fixdsys',size = 15,weight = tkFont.BOLD)
		self.mtft = tkFont.Font(family = 'Fixdsys',size = 12) # meaningtip字体

		self.labelInput=tkinter.Label(self.container,font=self.ft,text='word: ')
		self.labelInput.grid(row=0,column=0,padx=0,pady=0,sticky=tkinter.EW)
##		self.draggableCtrl=self.labelInput
##		self.offsetx,self.offsety=5+2+2,5+2+2
		self.draggableCtrl=self.container
		self.offsetx,self.offsety=0,0

		self.entryInput=tkinter.Entry(self.container,font=self.ft,bd=0,textvariable=self.vInput)
		self.FirstIn=True
##		self.entryInput.bind('<Activate>',self.entryInput.focus_get,'+')
##		self.entryInput.bind('<Activate>',lambda ev:self.entryInput.select_range(0, tkinter.END),'+')
		self.entryInput.bind('<ButtonPress-1>',self._InputClickedByLeftMouse,'+')
		self.entryInput.bind('<FocusIn>',self._InputFocusIn)
##		self.entryInput.bind('<FocusOut>',self._InputFocusOut)
		self.ac=AutoComplete(self.entryInput,self.onCmdSearch)#,open(r'd:\onlyword.txt').readlines()) # 自动完成
		self.entryInput.grid(row=0,column=1,columnspan=1,sticky=tkinter.EW)

		self.btnSearch=tkinter.Button(self.container,padx=0,pady=0,relief=tkinter.FLAT,overrelief=tkinter.RAISED,text='query',command=self.onCmdSearch)
		self.btnSearch.grid(row=0,column=2,sticky=tkinter.NSEW)

		self.btnSave=tkinter.Button(self.container,padx=0,pady=0,relief=tkinter.FLAT,overrelief=tkinter.RAISED,text='save',command=self.onCmdSave)
		self.btnSave.grid(row=0,column=3,sticky=tkinter.NSEW)

		self.container.pack(expand=True,fill=tkinter.BOTH)

		# 通过 label 处理拖动
		self.labelInput.bind("<ButtonPress-1>", self.onLeftMouse,'+')
		self.labelInput.bind("<ButtonRelease-1>",self.onLeftMouse,'+')
		self.labelInput.bind("<Motion>",self.onLeftMouse,'+')

		self.mt=MeaningTip(self.entryInput,font=self.mtft) # 显示释义
		self.entryInput.bind("<1>", lambda ev:self.mt.hide(ev), '+')  # 当点击输入框时关闭释义窗口

	def _InputFocusIn(self,event):
		self.logger.debug('focusin')
		if self.FirstIn:
			self.entryInput.select_range(0, tkinter.END)
			self.FirstIn=False
		else: self.FirstIn=True

	def _InputClickedByLeftMouse(self,event):
		self.logger.debug('FirstIn=%s',self.FirstIn)
		if self.FirstIn:
			self.logger.debug('select all~')
			self.entryInput.select_range(0, tkinter.END)
			self.labelInput.focus_set()

##	def _InputFocusOut(self,event):
##		self.logger.debug('focusout')



	def onLeftMouse(self,event):
		BasePanel.onLeftMouse(self,event)
		if self.InDrag:
			if self.ac.active:
				self.ac.DestroyGUI()
			self.mt.hide()



	def loadCfg(self,cfg,section):
		BasePanel.loadCfg(self,cfg,section)
		self.c.cur=cfg.getint(section,'cur')
		self.c.recent_dir=cfg.get(section,'recent_dir')

	def saveCfg(self,cfg,section=None):
		BasePanel.saveCfg(self,cfg,section)
		if not section:
			section=self.section
		cfg.set(section,'cur',str(self.c.cur))
		cfg.set(section,'recent_dir',self.c.recent_dir)


	def applyCfg(self):
		BasePanel.applyCfg(self)
		self.container.configure(bg=self.c.bg)
		self.labelInput.configure(bg=self.c.bg,fg=self.c.fg)
		self.entryInput.configure(bg=self.c.bg,fg=self.c.fg)
		self.btnSearch.configure(bg=self.c.bg,fg=self.c.fg)
		self.btnSave.configure(bg=self.c.bg,fg=self.c.fg)


	def createMenu(self,mainmenu):
		BasePanel.createMenu(self,mainmenu)
		if not self.c.enabled:
			return

		self.cur_list_menu=tkinter.Menu(self.menu,tearoff=False)
		for idx,i in enumerate(self.c.file):
			self.cur_list_menu.add_radiobutton(label=os.path.split(i[0])[1],command=self.onCmdSwitchFile,
				value=i[0],variable=self.vFile)
			if idx==self.c.cur:
				self.cur_list_menu.invoke(idx)
		self.menu.add_cascade(label='files...',menu=self.cur_list_menu)

		for k,v,c in (('dictionary file ...',self.onCmdChooseFile,None),
								('bg color ...',self.onCmdChooseColor,'bg'),
								('fg color ...',self.onCmdChooseColor,'fg'),
								):
			self.menu.add_command(label = k,command = lambda v=v,c=c:v(c))
			self.menu.add_separator()
		mainmenu.add_cascade(label = '%s config '%(self.title,),menu = self.menu)

	def show(self):
		BasePanel.show(self)
		self.vInput.set('') # self.vInput.set('input word here:')
		self.entryInput.select_range(0,tkinter.END)
		self.entryInput.icursor(tkinter.END)
		self.entryInput.focus_force()
		w=self.labelInput.winfo_reqwidth()+self.entryInput.winfo_reqwidth()\
			+self.btnSearch.winfo_reqwidth()+self.btnSave.winfo_reqwidth()#+(5+2)*2
		h=max(self.labelInput.winfo_reqheight(),self.entryInput.winfo_reqheight(),
				self.btnSearch.winfo_reqheight(),self.btnSave.winfo_reqheight())#+(5+2)*2
##		self.curgeometry=[self.container.winfo_reqwidth(),self.container.winfo_reqheight()]
		self.curgeometry=[w,h]
		self.logger.info('crgeometry=%dx%d',*self.curgeometry)
		self.logger.info('input=%dx%d,btn=%dx%d',
			self.entryInput.winfo_reqwidth(),self.entryInput.winfo_reqheight(),
			self.btnSearch.winfo_reqwidth(),self.btnSearch.winfo_reqheight())
##		self.container.pack(expand=True,fill=tkinter.BOTH)
		self.logger.info('grid_size=%dx%d',*self.container.grid_size())
		self.logger.info('contaner=%dx%d',self.container.winfo_reqwidth(),self.container.winfo_reqheight())
		self.logger.info('w.grid_info()=%s',self.container.grid_info())
##		self.logger.info('root=%dx%d',self.root.winfo_reqwidth(),self.root.winfo_reqheight())

		self.container.pack(expand=True,fill=tkinter.BOTH)
		self.root.geometry('%dx%d%s'%(self.curgeometry[0],self.curgeometry[1],self.c.position))
##		self.container.geometry('%dx%d'%(640,480))

	def hide(self):
		BasePanel.hide(self)
		self.ac.DestroyGUI()
		self.mt.hide()
		self.container.pack_forget()

	def updatePanel(self):
		BasePanel.updatePanel(self)

	def pausePanel(self,new_stat):
		BasePanel.pausePanel(self,new_stat)

	def onCmdChooseColor(self,extra):
		self.logger.debug('extra=%s',extra)
		if extra=='bg':
			_,r=tkColorChooser.askcolor(self.c.bg,title='Choose background color')
			if r:
				self.c.bg=r
				self.container.configure(bg=self.c.bg)
				self.labelInput.configure(bg=self.c.bg)
				self.entryInput.configure(bg=self.c.bg)
				self.btnSearch.configure(bg=self.c.bg)
				self.btnSave.configure(bg=self.c.bg)
		elif extra=='fg':
			_,r=tkColorChooser.askcolor(self.c.fg,title='Choose foreground color')
			if r:
				self.c.fg=r
				self.labelInput.configure(fg=self.c.fg)
				self.entryInput.configure(fg=self.c.fg)
				self.btnSearch.configure(fg=self.c.fg)
				self.btnSave.configure(fg=self.c.fg)

	def onCmdChooseFile(self,extra=None):
		'''文件选择'''
##		oldstat=self.stat
##		if self.stat==const.StatPlaying and self.timerid:
##			self.pauseShow(const.StatPaused)
		f=tkFileDialog.askopenfilenames(parent=self.root,title='Choose file(s) to use',
			initialdir=self.c.recent_dir,
			filetypes=[('Dict','*.dict *.dz'),('Idx', '*.idx'), ('Ifo','*.ifo'),('All files', '*')] )
		if f:
			flist=self.root.tk.splitlist(f) # http://psf.upfronthosting.co.za/roundup/tracker/issue5712 workaround: http://code.activestate.com/lists/python-tkinter-discuss/2016/
			if len(flist)>5:
				self.logger.info('一次最多添加5个文件，多余的会被丢弃，你选择了 %d个',len(flist))
				flist=flist[:5]
			for i,onefile in enumerate(flist):
				self.logger.debug('multi file %02d/%d: %s',i,len(flist),onefile)

			addorreplace=tkMessageBox.askyesnocancel('Add or replace','add the file(s) to your file list? (press "no" will replace current file list)',default=tkMessageBox.YES)
			self.logger.debug('addorreplace=%s',addorreplace)
			self.c.recent_dir=os.path.split(flist[0])[0]
			if addorreplace==None:
				self.logger.debug('do nothing')
			elif addorreplace==True: # add
				self.c.file.extend([i,0] for i in flist)
				# 更新filelist菜单
				for i in flist:
					self.cur_list_menu.add_radiobutton(label=os.path.basename(i),command=self.onCmdSwitchFile,
						value=i,variable=self.vFile)
				# 从recent中删除当前文件列表中存在的
				self.c.recent=[i for i in self.c.recent if i[0] not in (j[0] for j in self.c.file)]
				self.logger.debug('add done. new file list: %s',self.c.file)

			elif addorreplace==False: # replace
				if self.stat==const.StatPlaying:
					self.pausePanel(const.StatPaused4Switch)

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

	def onCmdSwitchFile(self):
		self.logger.info('swith to dictionary file %s',self.vFile.get())
		# 获取文件对应的索引
		idx=[i for i,n in enumerate(self.c.file) if n[0]==self.vFile.get()][0]
		self.c.cur=idx
		self.cur_dict=StartDictFile(self.c.file[self.c.cur][0])
		self.cur_dict.readIFO()
		self.cur_dict.readIDX()
		self.ac.setSuggestContent(self.cur_dict.getIdxList())

	def onCmdSearch(self,event=None):
		text=self.entryInput.get().strip()
		self.logger.debug('查询 %s ...',text)
		r=self.cur_dict.getMeaning(text.lower())
		if not r: r=self.cur_dict.getMeaning(text)

		if r:
			# TTS
			if self.c.tts_read and self.tts:
				self.tts.Speak(text)

			self.logger.debug('返回 %s',r.encode('gb18030'))
			# 显示在text中
			self.mt.show(r)

		self.onCmdSave(text)

	def onCmdSave(self,text=None):
		if not text:
			text=self.entryInput.get()

		if text:
			open(r'd:\stored_words.txt','a').write(' '.join((datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'),text,'\n')))
