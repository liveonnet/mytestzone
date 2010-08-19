#coding=utf-8
# copy from http://tkinter.unpythonic.net/wiki/ToolTip
import tkinter
import logging

class MeaningTip(object):
	def __init__(self, master, text='Your text here', **opts):
		self.logger=logging.getLogger(self.__class__.__name__)
		self.master = master
		self._opts = {'bd':1, 'bg':'lightyellow', 'fg':'black',\
		  'follow_mouse':0, 'font':None, 'padx':4, 'pady':2,\
		  'relief':'solid', 'state':'normal', 'takefocus':0, 'height':15,\
		  'width':40,'wrap':tkinter.WORD}
		self.configure(**opts)
		self._tipwindow = None
		self.container=None
##		self._id1 = self.master.bind("<Enter>", self.enter, '+')
##		self._id2 = self.master.bind("<Leave>", self.leave, '+')
##		self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
		self._id3 = self.master.bind("<Button-1>", self.hide, '+')
##		self._id4 = self.master.bind("<Motion>", self.motion, '+')

	def configure(self, **opts):
		for key in opts:
			if key in self._opts:
				self._opts[key] = opts[key]
			else:
				KeyError = 'KeyError: Unknown option: "%s"' %key
				raise KeyError

	##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
	##----events on the parent widget; override them if you want to change the widget's behavior--##


##	def motion(self, event=None):
##		if self._tipwindow:
##			x, y = self.coords()
##			self._tipwindow.wm_geometry("+%d+%d" % (x, y))

	##------the methods that do the work:---------------------------------------------------------##


	def show(self,content):
		if not self._tipwindow:
			self._tipwindow = tw = tkinter.Toplevel(self.master)
			# hide the window until we know the geometry
			tw.withdraw()
			tw.wm_overrideredirect(1)

			self.container=tkinter.Frame(self._tipwindow,highlightthickness=0)

			if tw.tk.call("tk", "windowingsystem") == 'aqua':
				tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

			opts = self._opts.copy()
			for opt in ( 'follow_mouse', 'state'):
				del opts[opt]
			sb=tkinter.Scrollbar(self.container)
			sb.pack(side=tkinter.RIGHT,fill=tkinter.Y)
			self.text = tkinter.Text(self.container, yscrollcommand=sb.set,**opts)
			sb.config(command=self.text.yview)
			self.text.pack(side=tkinter.LEFT,expand=tkinter.Y)
			self.container.pack(fill=tkinter.BOTH,expand=tkinter.YES)
			tw.update_idletasks()
			x, y = self.coords()
			logging.debug('x,y=%d,%d',x,y)
			tw.wm_geometry("+%d+%d" % (x, y))
			tw.deiconify()
			logging.debug('meaning tip created.')
		if not content:
			content='查不到'
		self.text.config(state=tkinter.NORMAL)
		self.text.delete('0.0',tkinter.END)
		l=content.split('\n')
		logging.debug('total %d lines to show',len(l))
		for el in l:
			self.text.insert(tkinter.INSERT,el)
			self.text.insert(tkinter.INSERT,'\n')
		self.text.config(state=tkinter.DISABLED)

	def hide(self,event=None):
		tw = self._tipwindow
		self._tipwindow = None
		if tw:
			logging.debug('meaning tip closed.')
			tw.destroy()

	##----these methods might be overridden in derived classes:----------------------------------##

	def coords(self):
		# The tip window must be completely outside the master widget;
		# otherwise when the mouse enters the tip window we get
		# a leave event and it disappears, and then we get an enter
		# event and it reappears, and so on forever :-(
		# or we take care that the mouse pointer is always outside the tipwindow :-)
		tw = self.master
		twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
		w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
		# calculate the y coordinate:
		y = self.master.winfo_rooty() + self.master.winfo_height() + 3
		if y + twy > h:
			y = self.master.winfo_rooty() - twy - 3
		# we can use the same x coord in both cases:
		tw.update_idletasks()
		x = tw.winfo_rootx() + twx / 2
		if x+self.master.winfo_reqwidth()>w:
			x=x-twx
		elif x + twx > w:
			x = w - twx
		return x, y

if __name__=='__main__':
	r=tkinter.Tk()
	m=MeaningTip(r)
	m.show('test')
	tkinter.mainloop()