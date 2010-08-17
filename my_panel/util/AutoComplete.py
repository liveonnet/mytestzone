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
	def __init__(self, win,suggestlist=None):
		self.logger=logging.getLogger('atcmplt')
		self.win = win
		self.active = False
		self.record = '' # 当前字符串
		self.recent_fail='' # 保存最近的查不到任何匹配的字符串，用于优化
		self.blkidx,self.blkendidx=0,0 # 当前listbox显示的是self.suggestlist的部分内容：self.suggestlist[self.blkidx:self.blkendidx]
		self.curidx=0 # 在suggestlist中最接近当前字符串的item索引
		self.listcontent=tkinter.StringVar()
		self.win.bind("<1>", self.onClick)
		self.win.bind("<KeyRelease>", self.onKeyRelease)

		if not suggestlist and __name__=='__main__':
			suggestlist=[x for x in open(r'd:\word.txt').readlines() if x.rstrip()!=0]
		self.suggestlist=suggestlist

		if not self.suggestlist:
			raise Exception('没有用于自动完成的数据!')


		# 保存将两字符起始索引，用于优化
		self.quickIdx={}
		tmp=0
		for k,g in itertools.groupby(self.suggestlist,key=lambda x:x[:2]):
			self.quickIdx[k]=tmp
			tmp+=len(list(g))
		self.logger.info('total %d block')


	def FilterInput(self):
		# 初步优化
		if len(self.record)==2:
			try:
				self.blkidx=self.quickIdx[self.record] # 起始索引
			except KeyError:
				return
			else:
				# 获取结束索引
				try:
					self.blkendidx=min((x for x in self.quickIdx.values() if x>self.blkidx))
				except ValueError:
					self.blkendidx=len(self.suggestlist)
				self.logger.debug('blkendidx=%d',self.blkendidx)
				self.logger.debug('set [%d,%d) through quickIdx for %s',self.blkidx,self.blkendidx,self.record)
				self.listbox.delete(0,tkinter.END) # 先清空

				for i in self.suggestlist[self.blkidx:self.blkendidx]:
					self.listbox.insert(tkinter.END,i) # 插入本段数据
				self.logger.debug('插入 %d 个数据, listbox中总共 %d 个',self.blkendidx-self.blkidx,self.listbox.size())
##				self.listbox.selection_clear(self.listbox.curselection()[0])
##				self.listbox.yview_scroll(idx-self.curidx,tkinter.UNITS)
##				self.curidx=idx
				self.curidx=0
				self.listbox.select_set(self.curidx)
				return

		if self.recent_fail and re.match('^%s'%(self.recent_fail,),self.record):
			self.logger.debug('%s 以最近查找失败的串 %s 为起始串,不查找',self.record,self.recent_fail)
			return

		p=re.compile("^%s[a-zA-Z0-9|\-|\.]*"%(self.record,))
		for i,w in enumerate(self.suggestlist[self.blkidx:self.blkendidx]):
			if re.match(p,w):
				self.listbox.selection_clear(self.listbox.curselection()[0])
				self.listbox.yview_scroll(i-self.curidx,tkinter.UNITS)
				self.curidx=i
##				self.listbox.see(self.curidx)
				self.listbox.select_set(self.curidx)
				break
		else: # 没有完全匹配的则查最接近匹配的
			self.recent_fail=self.record[:]
			self.logger.debug('没有完全匹配 %s 的',self.recent_fail)
			record=self.record[:]
			while len(record)>2:
				record=record[:-1]
				p=re.compile("^%s[a-zA-Z0-9|\-|\.]*"%(record,))
				for i,w in enumerate(self.suggestlist[self.blkidx:self.blkendidx]):
					if re.match(p,w):
						self.listbox.selection_clear(self.listbox.curselection()[0])
						self.listbox.yview_scroll(i-self.curidx,tkinter.UNITS)
						self.curidx=i
						self.listbox.select_set(self.curidx)
						self.logger.debug('最接近匹配的是 %s',record)
						return

			self.logger.debug('最终查不到 %s',self.record)
			self.recent_fail=self.record[:]

	def onKeyRelease(self, event):
		key = event.char
		self.record=self.win.get()
		if re.match("[a-zA-Z0-9|\-|\.]", key):
			if not self.active and len(self.record)>1:
				self.MakeGUI()
			elif self.active:
				self.FilterInput()
		elif event.keysym in ("BackSpace","Delete"):
			if self.active:
				if len(self.record)>1:
					self.FilterInput()
			elif len(self.record)>1:
				self.MakeGUI()
			else:
				self.DestroyGUI()
		elif event.keysym == "Return":
			if self.active:
				self.win.delete(0,tkinter.END)
				self.win.insert(tkinter.INSERT, self.listbox.get(self.listbox.curselection()[0]))
				self.DestroyGUI()
		elif event.keysym in ("Up","Down","Next","Prior","Shift_R", "Shift_L",
			"Control_L", "Control_R", "Alt_L",
			"Alt_R", "parenleft", "parenright"):
			pass
		else:
			if self.active:
				self.DestroyGUI()

	def onKeyPress(self,event):
		if not self.active:
			return
		if event.keysym =="Down":
			idx=int(self.listbox.curselection()[0])
			newidx=(idx+self.listbox.size()+1)%self.listbox.size()
			self.listbox.selection_clear(idx)
			self.listbox.see(newidx)
			self.listbox.selection_set (newidx)
		elif event.keysym=="Up":
			idx=int(self.listbox.curselection()[0])
			newidx=(idx+self.listbox.size()-1)%self.listbox.size()
			self.listbox.selection_clear(idx)
			self.listbox.see(newidx)
			self.listbox.selection_set (newidx)
		elif event.keysym=="Next":
			self.logger.debug('nearest %d',self.listbox.nearest(self.listbox.winfo_height()))
			if self.listbox.nearest(self.listbox.winfo_height())<self.blkendidx-self.blkidx-1:
				self.listbox.yview_scroll(1,tkinter.PAGES)
			else:
				self.listbox.see(0)
		elif event.keysym=="Prior":
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
		self.win.delete(0,tkinter.END)
		self.win.insert(tkinter.INSERT, self.listbox.get(self.listbox.curselection()[0]))
		self.DestroyGUI()

	def MakeGUI(self):
		x, y, cx, cy = self.win.bbox("insert")
		self.logger.debug('x,y=%d,%d, cx,cy=%d,%d',x,y,cx,cy)
		x = x + self.win.winfo_rootx() + 2
		y = y + cy + self.win.winfo_rooty()+22 # TODO: magic number 20 是标题栏高度
		tl = tkinter.Toplevel(self.win.master)
		tl.wm_overrideredirect(1)
		tl.wm_geometry("+%d+%d" % (x, y))
		form = tkinter.Frame(tl, highlightthickness=0)
		form.pack(fill="both", expand="yes")
		sb = tkinter.Scrollbar(form, highlightthickness=0)
		sb.pack(side="right", fill="y")
		ft = tkFont.Font(family = 'Fixdsys',size = 12)
		self.listbox = tkinter.Listbox(form, font=ft,highlightthickness=0,relief="flat",
			yscrollcommand=sb.set, height=10,listvariable=self.listcontent)
		self.listbox.selection_set(0)
		self.listbox.pack(side="left", fill="both")
		sb.config(command=self.listbox.yview)
##        self.listbox.focus()
		self.win.bind("<KeyPress-Down>", self.onKeyPress)
		self.win.bind("<KeyPress-Up>", self.onKeyPress)
		self.win.bind("<KeyPress-Next>", self.onKeyPress)
		self.win.bind("<KeyPress-Prior>", self.onKeyPress)
		self.win.bind("<KeyRelease>", self.onKeyRelease)
		self.listbox.bind("<Double-1>", self.onDbClick)
		self.FilterInput()
		self.active=True

	def DestroyGUI(self):
		self.listbox.master.master.destroy()
		self.curidx=0
		self.active = False

# Test
if __name__ == "__main__":
	t = tkinter.Entry(font=("courier", 10))
	t.pack()
##    t.insert("end", "import Tkinter\nt = Tkinter")
	a = AutoComplete(t)
	t.mainloop()