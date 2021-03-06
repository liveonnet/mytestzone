#! /usr/bin/env python
#coding=utf-8
# reference http://bugs.python.org/file6887/AutoComplete.py

##with open(r'd:\onlyword.txt','w') as o:
##	with codecs.open(r'd:\out1.txt','r',encoding='utf-8') as f:
##		s=list(set([x.split('\t',1)[0].split(' ',1)[0].lower() for x in f]))
##		s.sort()
##		s=[x+'\n' for x in s]
##		o.writelines(s)

import re, sys, os, tkinter
import itertools
import tkinter.font as tkFont
import logging

class AutoComplete(object):
	def __init__(self, win,callbackfunc,suggestlist=None):
		self.logger=logging.getLogger(self.__class__.__name__)
		self.win = win
		self.active = False
		self.record = None # 当前字符串
		self.curQuickIdx=None # 当前使用的索引
		self.recent_fail=None # 保存最近的查不到任何匹配的字符串，用于优化
		self.blkidx,self.blkendidx=0,0 # 当前listbox显示的是self.suggestlist的部分内容：self.suggestlist[self.blkidx:self.blkendidx]
		self.curidx=0 # 在suggestlist中最接近当前字符串的item索引
		self.listbox=None
##		self.listcontent=tkinter.StringVar()
		self.win.bind("<1>", self.onClick,'+')
		self.win.bind("<KeyRelease>", self.onKeyRelease)

		if not suggestlist and __name__=='__main__':
			suggestlist=[x.rstrip() for x in open(r'/mnt/driver_D/word.txt').readlines() if x.rstrip()!='']
		self.suggestlist=suggestlist


		self.quickIdx=None # 记录各字母开头的词汇的起始结束索引
		if not self.suggestlist:
			self.logger.info('没有用于自动完成的数据!')
		else:
			self.prepareData()

		self.cbFunc=callbackfunc # 回调函数

	def prepareData(self):
		# 保存两字符起始、结束索引，用于优化
		self.quickIdx={}
		tmp=0
		pre_k=''
		for k,g in itertools.groupby(self.suggestlist,key=lambda x:x[:2].lower()):
			if pre_k:
				self.quickIdx[pre_k].append(tmp)
			self.quickIdx[k]=[tmp,]
			tmp+=len(list(g))
			pre_k=k
		if pre_k:
			self.quickIdx[pre_k].append(tmp)
		self.logger.info('total %d block',len(self.quickIdx))


	def FilterInput(self):
		if not self.suggestlist:
			return
		if not self.record:
			return

		# 初步优化
		if (len(self.record)>=2 and self.record[0:2]!=self.curQuickIdx):
			try:
				self.blkidx,self.blkendidx=self.quickIdx[self.record[0:2]] # 起始，结束索引
			except KeyError:
				self.logger.debug('no quickIdx %s',self.record[0:2])
				self.DestroyGUI()
				return
			else:
				self.recent_fail=''
				self.logger.debug('set quickIdx[%s]  [%d,%d)',self.record[0:2],self.blkidx,self.blkendidx)
				self.curQuickIdx=self.record[0:2]
				self.listbox.delete(0,tkinter.END) # 先清空

				for i in self.suggestlist[self.blkidx:self.blkendidx]:
					self.listbox.insert(tkinter.END,i) # 插入本段数据
				self.logger.debug('插入 %d 个数据, listbox中总共 %d 个',self.blkendidx-self.blkidx,self.listbox.size())
##				self.listbox.selection_clear(self.listbox.curselection()[0])
##				self.listbox.yview_scroll(idx-self.curidx,tkinter.UNITS)
##				self.curidx=idx
				self.curidx=0
				self.listbox.select_set(self.curidx)
##				return

		if self.recent_fail and self.record.startswith(self.recent_fail): #re.match('^%s'%(self.recent_fail,),self.record):
			self.logger.debug('%s 以最近查找失败的串 %s 为起始串,不查找',self.record,self.recent_fail)
			return

		if '*' in self.record: # 替换星号以便正确处理特殊股票名称，比如 *ST系列股票
			tmp=self.record.replace('*','\\*')
		else:
			tmp=self.record[:]

		# 过滤re中的保留字
		re_chars=['(',')','[',']','{','}']
		for c in re_chars:
			if c in tmp:
				tmp=tmp.replace(c,'\\%s'%c)
##		p=re.compile('^%s[a-zA-Z0-9|\-|\.| ]*'%(self.record,),re.I)
		p=re.compile('^%s[a-zA-Z0-9|\-|\.| ]*'%(tmp,),re.I)
		for i,w in enumerate(self.suggestlist[self.blkidx:self.blkendidx]):
			if re.match(p,w):
				if self.listbox.curselection():
					self.listbox.selection_clear(self.listbox.curselection()[0]) # 取消以前的选择
				self.listbox.yview_scroll(i-self.curidx,tkinter.UNITS)
				self.curidx=i
				self.listbox.see(self.curidx)
				self.listbox.select_set(self.curidx)
				break
		else: # 没有完全匹配的则查最接近匹配的
##			self.recent_fail=self.record[:]
##			self.logger.debug('没有完全匹配 %s 的',self.recent_fail)
			self.logger.debug('没有完全匹配 %s 的',self.record)
			record=self.record[:]
			if '*' in record: # 替换星号
				record=record.replace('*','\\*')

			# 过滤re中的保留字
			re_chars=['(',')','[',']','{','}']
			for c in re_chars:
				if c in record:
					record=record.replace(c,'\\%s'%c)

			while len(record)>2:
				record=record[:-1]
				p=re.compile('^%s[a-zA-Z0-9|\-|\.| ]*'%(record,))
				for i,w in enumerate(self.suggestlist[self.blkidx:self.blkendidx]):
					if re.match(p,w):
						if self.listbox.curselection():
							self.listbox.selection_clear(self.listbox.curselection()[0])
						self.listbox.yview_scroll(i-self.curidx,tkinter.UNITS)
						self.curidx=i
						self.listbox.see(self.curidx)
##						self.listbox.select_set(self.curidx)
						self.logger.debug('最接近匹配的是 %s',record)
						return

			self.logger.debug('最终查不到 %s',self.record)
			self.recent_fail=self.record[:]

	def onKeyRelease(self, event):
##		self.logger.debug('input %s',event.char)
		if not self.suggestlist:
			self.logger.debug('not suggestlist!')
			return
		key = event.char
		modified=False
		if self.record!=self.win.get().lower():
			self.record=self.win.get().lower()
			modified=True
			self.logger.debug('modified! key=|%s| keysym=%s, len(self.record)=%d,|%s|',key,event.keysym,len(self.record),self.record)

		if re.match('[a-zA-Z0-9|\-|\.| ]', key):
			if not self.active and len(self.record)>1:
				self.MakeGUI()
			elif self.active and modified:
				self.FilterInput()
		elif event.keysym in ('BackSpace','Delete'):
			if self.active:
				if len(self.record)>1:
					self.FilterInput()
			elif len(self.record)>1:
				self.MakeGUI()
			else:
				self.DestroyGUI()
		elif event.keysym == 'Return':
			if self.active:
				if self.listbox.curselection():
					self.win.delete(0,tkinter.END)
					self.win.insert(tkinter.INSERT, self.listbox.get(self.listbox.curselection()[0]))
				self.win.select_range(0, tkinter.END) # 选择
				self.DestroyGUI()
				self.logger.debug('pressed return!')
				self.cbFunc()
		elif event.keysym == 'Escape': # 按 ESC 则隐藏listbox
			if self.active:
				self.DestroyGUI()
		elif event.keysym in ('Up','Down','Next','Prior','Shift_R', 'Shift_L',
##			'Control_L', 'Control_R', 'Alt_L','Alt_R',
			'parenleft', 'parenright'):
			pass
		else:
			self.logger.debug('else~')
			if modified and len(self.record)>1:
				self.MakeGUI()
##			if self.active:
##				self.DestroyGUI()
##			else:
##				if modified and len(self.record)>1:
####					self.DestroyGUI()
##					self.MakeGUI()

	def onKeyPress(self,event):
		if not self.suggestlist:
			return
		# 如果当前没有显示listbox但是输入的字符串曾经(部分)匹配过则再次显示listbox。这是为了增加易用性，避免误按esc后如果不输入字符串则不
		#  显示listbox的问题
		if (not self.active):
			if self.listbox.curselection():
				self.MakeGUI()
			else:
				return

		if event.keysym =='Down':
			if self.listbox.curselection():
				idx=int(self.listbox.curselection()[0])
				newidx=(idx+self.listbox.size()+1)%self.listbox.size()
				self.listbox.selection_clear(idx)
				self.listbox.see(newidx)
				self.listbox.selection_set (newidx)
		elif event.keysym=='Up':
			if self.listbox.curselection():
				idx=int(self.listbox.curselection()[0])
				newidx=(idx+self.listbox.size()-1)%self.listbox.size()
				self.listbox.selection_clear(idx)
				self.listbox.see(newidx)
				self.listbox.selection_set (newidx)
		elif event.keysym=='Next':
			self.logger.debug('nearest %d',self.listbox.nearest(self.listbox.winfo_height()))
			if self.listbox.nearest(self.listbox.winfo_height())<self.blkendidx-self.blkidx-1:
				self.listbox.yview_scroll(1,tkinter.PAGES)
			else:
				self.listbox.see(0)
		elif event.keysym=='Prior':
			self.logger.debug('nearest %d',self.listbox.nearest(0))
			if self.listbox.nearest(0)!=0:
				self.logger.debug('继续上翻')
				self.listbox.yview_scroll(-1,tkinter.PAGES)
			else:
				self.logger.debug('到最后 %d',self.blkendidx-self.blkidx-1)
				self.listbox.see(self.blkendidx-self.blkidx-1)


	def onClick(self, event):
		if self.active:
			self.DestroyGUI()

	def onDbClick(self, event):
		if not self.suggestlist:
			return
		if self.listbox.curselection():
			self.win.delete(0,tkinter.END)
			self.win.insert(tkinter.INSERT, self.listbox.get(self.listbox.curselection()[0]))
			self.DestroyGUI()
			self.cbFunc()

	def MakeGUI(self):
##		self.logger.debug('makegui...')
		x, y, cx, cy = self.win.bbox("insert")
		self.logger.debug('x,y=%d,%d, cx,cy=%d,%d',x,y,cx,cy)
		x = x + self.win.winfo_rootx() + 2
		y = y + cy + self.win.winfo_rooty()+self.win.winfo_height()+1
		if not self.listbox:
			tl = tkinter.Toplevel(self.win.master)
			tl.wm_overrideredirect(1)
			tl.wm_geometry("+%d+%d" % (x, y))
			form = tkinter.Frame(tl, highlightthickness=0)
			form.pack(fill=tkinter.BOTH, expand=tkinter.YES)
			sb = tkinter.Scrollbar(form, highlightthickness=0)
			sb.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
			ft = tkFont.Font(family = 'Fixdsys',size = 12)
			self.listbox = tkinter.Listbox(form, font=ft,highlightthickness=0,relief=tkinter.FLAT,
##				yscrollcommand=sb.set, height=10,listvariable=self.listcontent)
				yscrollcommand=sb.set, height=10)
			self.listbox.selection_set(0)
			self.listbox.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
			sb.config(command=self.listbox.yview)
##		else:
		self.listbox.master.master.wm_geometry("+%d+%d" % (x, y))
		self.win.bind("<KeyPress-Down>", self.onKeyPress)
		self.win.bind("<KeyPress-Up>", self.onKeyPress)
		self.win.bind("<KeyPress-Next>", self.onKeyPress)
		self.win.bind("<KeyPress-Prior>", self.onKeyPress)
		self.win.bind("<KeyRelease-Return>",self.onKeyRelease) # 接管回车
		self.listbox.bind("<KeyRelease-Return>",self.onKeyRelease) # 接管回车
	##	self.win.bind("<KeyRelease>", self.onKeyRelease)
		self.listbox.bind("<Double-1>", self.onDbClick)
		self.listbox.master.master.deiconify()

		self.FilterInput()
		self.active=True

	def DestroyGUI(self):
##		self.listbox.master.master.destroy()
		if self.listbox:
			self.listbox.master.master.withdraw()
			self.curidx=0
			self.active = False
			self.win.bind("<KeyRelease-Return>", self.cbFunc) # 恢复回车
			self.logger.debug('destory gui')

	def setSuggestContent(self,suggest_content):
		if self.active:
			self.DestroyGUI()
		self.suggestlist=suggest_content
##		self.logger.info('id of \'test\' is %x',0 if 'test' not in self.suggestlist else id(self.suggestlist[self.suggestlist.index('test')]))
		self.logger.debug('sizeof suggestlist is %d',sys.getsizeof(self.suggestlist))

##		# 打印内存占用情况
##		import gc
##		from io import StringIO
##		from pprint import pprint
##		from collections import defaultdict
##		d = defaultdict(int)
##		objects = gc.get_objects()
##		self.logger.debug('gc objects size: %d', len(objects))
##		for o in objects:
##			d[str(type(o))] += sys.getsizeof(o)
##		d=[(k,v) for k,v in d.items()]
##		d.sort(key=lambda x:x[1],reverse=True)
##		t=StringIO()
##		pprint(d,t)
##		self.logger.debug('memory usage:\n%s',t.getvalue())
##		t.close()

		# 先reset自动完成状态数据
		self.recent_fail=''
		if self.listbox: self.listbox.delete(0,tkinter.END) # 先清空
		self.curQuickIdx=None
		self.curidx=0
		self.blkidx,self.blkendidx=0,0
		self.prepareData()
		# 将新数据应用于自动完成
		e=lambda x:None
		e.keysym=''
		e.char='x'
		self.onKeyRelease(e)

# Test
if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG,format='%(thread)d %(asctime)s %(message)s',datefmt= '%H:%M:%S')
	app=tkinter.Tk()
	app.wm_attributes("-topmost", 1) # set to Top Most
	app.overrideredirect(True) # 不显示titlebar
	def fun(*args,**kwargs):
		logging.debug('called. %s', vInput.get())
		if app.overrideredirect():
			app.overrideredirect(False)
		else:
			app.overrideredirect(True)
			app.focusmodel(tkinter.ACTIVE)
			t.focus_force()
		app.withdraw()
		app.deiconify()

##	app.wm_attributes('-fullscreen')
	container=tkinter.Frame(app,bd=0,padx=0,pady=0,relief=tkinter.RIDGE)

	vInput=tkinter.StringVar()
	t = tkinter.Entry(container,font=('courier', 10),textvariable=vInput)
	t.pack()
	btn=tkinter.Button(container,text='do',command=fun)
	btn.pack()
	container.pack(expand=True,fill=tkinter.BOTH)
##    t.insert("end", "import Tkinter\nt = Tkinter")

	a = AutoComplete(t,fun)
	t.focus_force()
##	t.grab_set()
	app.tkraise()
	app.update()
	app.geometry('+200+200')
	app.mainloop()