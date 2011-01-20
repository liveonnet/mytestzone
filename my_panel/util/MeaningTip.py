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
		  'width':50,'wrap':tkinter.WORD}
		self.configure(**opts)
		self._tipwindow = None
		self.container=None
##		self._id1 = self.master.bind("<Enter>", self.enter, '+')
##		self._id2 = self.master.bind("<Leave>", self.leave, '+')
##		self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
##		self._id3 = self.master.bind("<1>", self.hide, '+')
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
			self.container.pack(fill=tkinter.BOTH,expand=tkinter.YES)

			if tw.tk.call("tk", "windowingsystem") == 'aqua':
				tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

			opts = self._opts.copy()
			for opt in ( 'follow_mouse', 'state'):
				del opts[opt]
			self.sb=tkinter.Scrollbar(self.container)
			self.sb.pack(side=tkinter.RIGHT,fill=tkinter.Y)
			self.text = tkinter.Text(self.container,**opts)
			self.text.pack(side=tkinter.LEFT,expand=tkinter.Y)
			self.sb.config(command=self.text.yview)
			self.text.config(yscrollcommand=self.sb.set)
			tw.update_idletasks()
##			x, y = self.coords()
##			self.logger.debug('x,y=%d,%d',x,y)
##			tw.wm_geometry("+%d+%d" % (x, y))
##			tw.deiconify()
			self.logger.debug('meaning tip created.')
		else:
			self._tipwindow.withdraw()
		if not content:
			content='查不到'
		x, y = self.coords()
		self.logger.debug('x,y=%d,%d',x,y)
		self._tipwindow.wm_geometry("+%d+%d" % (x, y))
		self._tipwindow.deiconify()
		self.text.config(state=tkinter.NORMAL)
		self.text.delete('0.0',tkinter.END)
		l=content.split('\n')
		self.logger.debug('total %d lines to show',len(l))
		for el in l:
			self.text.insert(tkinter.INSERT,el)
			self.text.insert(tkinter.INSERT,'\n')
##		self.text.yview(tkinter.MOVETO, 1.0)
##		self.text.yview(tkinter.MOVETO,0.0)
		self.text.config(state=tkinter.DISABLED)

	def hide(self,event=None):
		tw = self._tipwindow
		self._tipwindow = None
		if tw:
			self.logger.debug('meaning tip closed.')
			tw.withdraw()
			tw.destroy()

	##----these methods might be overridden in derived classes:----------------------------------##

	def coords(self):
		tw = self.master.master
		if not tw:
			tw=self.master
		tw.update_idletasks()
		twx, twy = self.text.winfo_reqwidth()+self.sb.winfo_reqwidth(),self.text.winfo_reqheight()
		w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
		# calculate the y coordinate:
		y = self.master.winfo_rooty() + self.master.winfo_height()
##		self.logger.debug('master.master req twx,twy=%d,%d w,h=%d,%d y=%d',twx,twy,w,h,y)
##		self.logger.debug('master.master twx,twy=%d,%d',tw.winfo_width(),tw.winfo_height())
##		self.logger.debug('text %d,%d',self.text.winfo_reqwidth(),self.text.winfo_reqheight())
##		self.logger.debug('master  req %d,%d',self.master.winfo_reqwidth(),self.master.winfo_reqheight())
##		self.logger.debug('master %d,%d',self.master.winfo_width(),self.master.winfo_height())
		if y + twy > h:
			y = tw.winfo_rooty() - twy

		if y<tw.winfo_rooty():
			x = tw.winfo_rootx()
		else:
			x = tw.winfo_rootx() + twx / 2
		if x + twx > w: # 右边出界
			x = w - twx
##		elif x+self.master.winfo_reqwidth()>w:
##			x=x-twx
		return x, y

if __name__=='__main__':
	r=tkinter.Tk()
	m=MeaningTip(r)
	m.show('test')
	tkinter.mainloop()