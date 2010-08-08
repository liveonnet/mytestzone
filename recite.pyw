import tkinter
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import tkinter.ttk as ttk


import codecs


'''Michael Lange <klappnase at 8ung dot at>
The ToolTip class provides a flexible tooltip widget for tkinter; it is based on IDLE's ToolTip
module which unfortunately seems to be broken (at least the version I saw).
INITIALIZATION OPTIONS:
anchor :        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
				default is "center"
bd :            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
bg :            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
delay :         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
				entered the parent widget; default is 1500
fg :            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
follow_mouse :  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
				outside of the parent widget; this may be useful if you want to use tooltips for
				large widgets like listboxes or canvases; default is 0
font :          font to use for the widget; default is system specific
justify :       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
padx :          extra space added to the left and right within the widget; default is 4
pady :          extra space above and below the text; default is 2
relief :        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
state :         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
text :          the text that is displayed inside the widget
textvariable :  if set to an instance of tkinter.StringVar() the variable's value will be used as text for the widget
width :         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
wraplength :    limits the number of characters in each line; default is 150

WIDGET METHODS:
configure(**opts) : change one or more of the widget's options as described above; the changes will take effect the
					next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

Other widget methods that might be useful if you want to subclass ToolTip:
enter() :           callback when the mouse pointer enters the parent widget
leave() :           called when the mouse pointer leaves the parent widget
motion() :          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
					tooltip has shown up to continually update the coordinates of the tooltip window
coords() :          calculates the screen coordinates of the tooltip window
create_contents() : creates the contents of the tooltip window (by default a tkinter.Label)
'''
# Ideas gleaned from PySol

import tkinter

class ToolTip(object):
	def __init__(self, master, text='Your text here', delay=1500, **opts):
		self.master = master
		self._opts = {'anchor':'center', 'bd':1, 'bg':'lightyellow', 'delay':delay, 'fg':'black',\
					  'follow_mouse':0, 'font':None, 'justify':'left', 'padx':4, 'pady':2,\
					  'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,\
					  'width':0, 'wraplength':150}
		self.configure(**opts)
		self._tipwindow = None
		self._id = None
		self._id1 = self.master.bind("<Enter>", self.enter, '+')
		self._id2 = self.master.bind("<Leave>", self.leave, '+')
		self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
		self._follow_mouse = 0
		if self._opts['follow_mouse']:
			self._id4 = self.master.bind("<Motion>", self.motion, '+')
			self._follow_mouse = 1

	def configure(self, **opts):
		for key in opts:
			if key in self._opts:
				self._opts[key] = opts[key]
			else:
				KeyError = 'KeyError: Unknown option: "%s"' %key
				raise KeyError

	##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
	##----events on the parent widget; override them if you want to change the widget's behavior--##

	def enter(self, event=None):
		self._schedule()

	def leave(self, event=None):
		self._unschedule()
		self._hide()

	def motion(self, event=None):
		if self._tipwindow and self._follow_mouse:
			x, y = self.coords()
			self._tipwindow.wm_geometry("+%d+%d" % (x, y))

	##------the methods that do the work:---------------------------------------------------------##

	def _schedule(self):
		self._unschedule()
		if self._opts['state'] == 'disabled':
			return
		self._id = self.master.after(self._opts['delay'], self._show)

	def _unschedule(self):
		id = self._id
		self._id = None
		if id:
			self.master.after_cancel(id)

	def _show(self):
		if self._opts['state'] == 'disabled':
			self._unschedule()
			return
		if not self._tipwindow:
			self._tipwindow = tw = tkinter.Toplevel(self.master)
			# hide the window until we know the geometry
			tw.withdraw()
			tw.wm_overrideredirect(1)

			if tw.tk.call("tk", "windowingsystem") == 'aqua':
				tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

			self.create_contents()
			tw.update_idletasks()
			x, y = self.coords()
			tw.wm_geometry("+%d+%d" % (x, y))
			tw.deiconify()

	def _hide(self):
		tw = self._tipwindow
		self._tipwindow = None
		if tw:
			tw.destroy()

	##----these methods might be overridden in derived classes:----------------------------------##

	def coords(self):
		# The tip window must be completely outside the master widget;
		# otherwise when the mouse enters the tip window we get
		# a leave event and it disappears, and then we get an enter
		# event and it reappears, and so on forever :-(
		# or we take care that the mouse pointer is always outside the tipwindow :-)
		tw = self._tipwindow
		twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
		w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
		# calculate the y coordinate:
		if self._follow_mouse:
			y = tw.winfo_pointery() + 20
			# make sure the tipwindow is never outside the screen:
			if y + twy > h:
				y = y - twy - 30
		else:
			y = self.master.winfo_rooty() + self.master.winfo_height() + 3
			if y + twy > h:
				y = self.master.winfo_rooty() - twy - 3
		# we can use the same x coord in both cases:
		x = tw.winfo_pointerx() - twx / 2
		if x < 0:
			x = 0
		elif x + twx > w:
			x = w - twx
		return x, y

	def create_contents(self):
		opts = self._opts.copy()
		for opt in ('delay', 'follow_mouse', 'state'):
			del opts[opt]
		label = tkinter.Label(self._tipwindow, **opts)
		label.pack()


# copy from http://effbot.org/zone/tkinter-text-hyperlink.htm
class HyperlinkManager(object):
	def __init__(self, text):
		self.text = text
		self.text.tag_config("hyper", foreground="blue", underline=1)
		self.text.tag_bind("hyper", "<Enter>", self._enter)
		self.text.tag_bind("hyper", "<Leave>", self._leave)
		self.text.tag_bind("hyper", "<Button-1>", self._click)

		self.reset()

	def reset(self):
		self.links = {}

	def add(self, action):
		# add an action to the manager.  returns tags to use in
		# associated text widget
		tag = "hyper-%d" % len(self.links)
		self.links[tag] = action
		return "hyper", tag

	def _enter(self, event):
		self.text.config(cursor="hand2")

	def _leave(self, event):
		self.text.config(cursor="")

	def _click(self, event):
		for tag in self.text.tag_names(CURRENT):
			if tag[:6] == "hyper-":
				self.links[tag]()
				return


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

		for k,v in {'source...':self.onCommandChangeSource
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

	def onCommandChangeSource(self):
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

