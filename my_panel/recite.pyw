import codecs
import tkinter
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import tkinter.ttk as ttk

from util.ToolTip import ToolTip
from util.HyperlinkManager import HyperlinkManager


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
			return self.wordlist[self.curidx]
		else:
			raise StopIteration()

	def __len__(self):
		return len(self.wordlist)


class MyRecite(object):
	def __init__(self):
		# 处理窗口拖动
		self.InDrag=False
		self.oldxy=[0,0]
		self.oldpos=[0,0]
		self.curgeometry=[320,240]

		# 处理定时刷新
		self.timerid=None
		self.StatPlaying,self.StatStoped,self.StatPaused=0,1,2
		self.Stat=None
		self.interval=2000

		self.content=None # 当前显示的对象

		self.root = tkinter.Tk()
		self.root.attributes("-alpha", 0.5) # use transparency level 0.1 to 1.0 (no transparency)
		self.root.wm_attributes("-topmost", 1) # set to Top Most
		# 绑定事件
		self.root.bind('<ButtonPress-1>', self.onLeftMouse)
		self.root.bind('<ButtonRelease-1>',self.onLeftMouse)
		self.root.bind('<Motion>',self.onLeftMouse)

		self.root.bind('<Double-Button-1>',self.onLeftMouseDbClick)
		self.root.bind('<Button-3>',self.onRightMouse)
		self.root.overrideredirect(True) # 不显示titlebar

		self.sText=tkinter.StringVar() # label显示的内容
		self.sText.set('MyRecite v0.1 powered by Python~')
		ft = tkFont.Font(family = 'Fixdsys',size = 20,weight = tkFont.BOLD)
##		self.label=tkinter.Label(self.root,font=ft,relief='ridge',anchor='center',bg='#000fff000',textvariable=self.sText)
		self.label=tkinter.Label(self.root,font=ft,relief='ridge',anchor='center',bg='#00ff00',fg='#0000ff',textvariable=self.sText)
		self.label.pack(expand='yes',fill=tkinter.BOTH)

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

		# 设置tooltip
		self.tooltiptext=tkinter.StringVar()
		ft = tkFont.Font(family = 'Fixdsys',size = 12,weight = tkFont.BOLD)
		self.tt=ToolTip(self.label,follow_mouse=0,font=ft,wraplength=self.root.winfo_screenwidth()/3,textvariable=self.tooltiptext)


		# 设置超链接
##		self.hyperlink_manager=HyperlinkManager(self.label)


		# 初始化显示文件
		self.content=WordFile(r'C:\Documents and Settings\刘强\桌面\1000句最常用英语口语-1.txt')
		self.startShow()
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
			self.pauseShow()
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
		try:
			t=next(self.content)
			self.Stat=self.StatPlaying
			self.timerFunc(t)
		except StopIteration:
			self.stat=self.StatStoped
			if self.timerid:
				self.label.after_cancel(self.timerid)

	def pauseShow(self):
		'''暂停显示内容'''
		self.label.after_cancel(self.timerid)
		self.timerid=None
		self.Stat=self.StatPaused

	def timerFunc(self,text2show):
		'''定时刷新函数'''
		self.sText.set(text2show)
		self.tooltiptext.set('%d/%d -- %s'%(self.content.curidx,self.content.maxidx,text2show))

		self.curgeometry=[self.label.winfo_reqwidth(),self.label.winfo_reqheight()]
		self.root.geometry('%dx%d'%(self.curgeometry[0],self.curgeometry[1]))

		try:
			t=next(self.content)
			self.timerid=self.label.after(self.interval,self.timerFunc,t)
		except StopIteration:
			print('stoped.')
			self.stat=self.StatStoped
			if self.timerid:
				self.label.after_cancel(self.timerid)
				self.timerid=None


	def onLeftMouse(self,event):
		'''处理窗体拖放'''
		if event.type=='6': # Motion
			if self.InDrag:
				xmvto=event.x_root-self.oldxy[0]
				ymvto=event.y_root-self.oldxy[1]
##				print('Motion at (%d,%d) +%d+%d'%(event.x,event.y,xmvto,ymvto))
				self.root.geometry('%dx%d+%d+%d'%(self.curgeometry[0],self.curgeometry[1],
					xmvto,ymvto))
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
		if self.Stat==self.StatPlaying and self.timerid:
			print('StatPlaying->StatPaused')
			self.pauseShow()
		elif self.Stat==self.StatPaused:
			print('StatPaused->StatPlaying')
			self.startShow()
		elif self.stat==self.StatStoped:
			print('StatStoped.')


	def run(self):
		self.root.mainloop()
		self.root.quit()

if __name__=='__main__':
	m=MyRecite()
	m.run()

	input('press ENTER to exit...')

