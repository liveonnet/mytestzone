#!/usr/bin/env python
#coding=utf-8
class Node:
	def __init__(self,parent,x,y,h):
		self.parent=parent
		self.x,self.y=x,y
		self.hv = (x << 16) ^ y
		self.g,self.h=0,h
	def __repr__(self):
		return '(%d,%d)'%(self.x,self.y)
	def __eq__(self,other):
		return self.hv == other.hv
	def __hash__(self):
		return self.hv

class AStarTest:
	def __init__(self,map_max_x,map_max_y,map):
		self.openlist,self.closedlist=[],Set()
		self.mapMaxX,self.mapMaxY=map_max_x,map_max_y
		print '%d %d'%(self.mapMaxX,self.mapMaxY)
		self.map=map
	def inCloseList(self,x,y):
		u"""检查(x,y)是否在closedlist中"""
		return Node(None,x,y,0) in self.closedlist
	def inOpenList(self,x,y):
		u"""检查(x,y)是否在openlist中"""
		for i,n in enumerate(self.openlist):
			if n.x==x and n.y==y:
				return i
		return -1
	def showPath(self,l,showmark):
		u"""显示路径"""
		tm=[]
		for i in self.map:
			tm.append(list(i))
		for i in self.closedlist:
			tm[i.y][i.x]=' '
		for i in l:
			tm[i.y][i.x]=showmark
		for i in tm:
			print ''.join(i)
	def SubNode(self,node,to_x,to_y):
		u""" 返回节点node的有效子节点"""
		subList=[
			(node.x-1,node.y-1),(node.x,node.y-1),(node.x+1,node.y-1),\
			(node.x-1,node.y),                    (node.x+1,node.y),\
			(node.x-1,node.y+1),(node.x,node.y+1),(node.x+1,node.y+1)]
		for x,y in subList:
			if x<self.mapMaxX and x>=0 and y<self.mapMaxY and y>=0 and self.map[y][x] !='#': # 坐标值有效
				if not self.inCloseList(x,y): # 不在closedlist中
					item= Node(node,x,y,sqrt((x-to_x)*(x-to_x)+(y-to_y)*(y-to_y))*1.2)
					if item.x==item.parent.x or item.y==item.parent.y: # 不是斜角节点
						item.g=item.parent.g+1.0
					else:	item.g=item.parent.g+1.4
					yield item

	def getPath(self,from_x,from_y,to_x,to_y,coord_marks,show_mark):
		u"""获取两点间的路径
		from_coord 起点
		to_coord 终点
		coord_marks 起点终点标志字符
		show_mark 用来显示路径的字符
		"""
		if from_x==None or from_x==None or to_x==None or to_y==None: # 需要从图中找到起点和终点
			(from_x,from_y),(to_x,to_y)=self.getFromTo(coord_marks)
		print "(%d,%d)->(%d,%d)"%(from_x,from_y,to_x,to_y)

		self.openlist.append(Node(None,from_x,from_y,0))
		while self.openlist: # 重复如下的工作：
			# a) 寻找开启列表中F值最低的格子。我们称它为当前格。
			minf,minidx,curCoord=1000000,-1,None # 假设当前最新f为1000000
			for i,n in enumerate(self.openlist):
				if n.g+n.h<minf:
					minf=n.g+n.h
					curCoord=n
					minidx=i
			# b) 把它切换到关闭列表。
			del self.openlist[minidx]
			self.closedlist.add(curCoord)

			# c) 对相邻的8格中的每一个
			for item in self.SubNode(curCoord,to_x,to_y):
				# 如果它不在开启列表中，把它添加进去。把当前格作为这一格的父节点。
				# 记录这一格的F,G,和H值。
				i=self.inOpenList(item.x,item.y)
				if i==-1:
					self.openlist.append(item)
					# 保存路径。从目标格开始，沿着每一格的父节点移动直到回到起始格。这就是你的路径。
					if item.x==to_x and item.y==to_y:
						print "found %d,len(closedlist)=%d"%(item.g,len(self.closedlist))
						l=[item]
						p=item.parent
						while p:
							l.append(p)
							p=p.parent
						for o in self.closedlist:# 为显示起始节点本来的字符而删掉起始节点
							if o.x==from_x and o.y==from_y:
								self.closedlist.remove(o)
								break
						self.showPath(l[1:-1],show_mark)
						return True

				# 如果它已经在开启列表中，用G值为参考检查新的路径是否更好。更低的G值
				# 意味着更好的路径。如果是这样，就把这一格的父节点改成当前格，并且
				# 重新计算这一格的G和F值。如果你保持你的开启列表按F值排序，改变之后
				# 你可能需要重新对开启列表排序。
				else:
					if item.g<self.openlist[i].g:
						self.openlist[i].parent=curCoord
						self.openlist[i].g=item.g


		print "no path found!"
		return False
	def getFromTo(self,marks):
		u"""从图中找到标为marks[0]的点作为起点，marks[1]的点作为终点"""
		from_coord,to_coord=None,None
		for idxy,i in enumerate(self.map):
			for idxx,j in enumerate(i):
				if j==marks[0]:
					from_coord=(idxx,idxy)
				elif j==marks[1]:
					to_coord=(idxx,idxy)
				if (from_coord is not None) and (to_coord is not None):
					return from_coord,to_coord
		return None,None

def run():
	m = [
	'############################################################',
	'#..........................................................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#.......S.....................#............................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#.............................#............................#',
	'#######.#######################################............#',
	'#....#........#............................................#',
	'#....#........#............................................#',
	'#....##########............................................#',
	'#..........................................................#',
	'#..........................................................#',
	'#..........................................................#',
	'#..........................................................#',
	'#..........................................................#',
	'#...............................##############.............#',
	'#...............................#........E...#.............#',
	'#...............................#............#.............#',
	'#...............................#............#.............#',
	'#...............................#............#.............#',
	'#...............................###########..#.............#',
	'#..........................................................#',
	'#..........................................................#',
	'############################################################']
	t=AStarTest(len(m[0]),len(m),m)
	t.getPath(None,None,None,None,'SE','o')

if __name__=='__main__':
	import sys
	from math import sqrt
	from sets import Set
	import cProfile,pstats
	cProfile.run('run()')
	#cProfile.run('run()','d:\\p.txt')
	#p=pstats.Stats('d:\\p.txt')
	#p.sort_stats('time', 'cum').print_stats(.5, 'inCloseList')
	#p.sort_stats('time', 'cum').print_stats()
	#run()
