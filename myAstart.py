#!/usr/bin/env python
#coding=utf-8
class Node:
	def __init__(self,parent,x,y,h):
		self.parent=parent
		self.x,self.y=x,y
		self.g,self.h=0,h

class AStarTest:
	def __init__(self,map_max_x,map_max_y,map):
		self.openlist,self.closedlist=[],[]
		self.mapMaxX,self.mapMaxY=map_max_x,map_max_y
		print '%d %d'%(self.mapMaxX,self.mapMaxY)
		self.map=map
	def inCloseList(self,x,y):
		for n in self.closedlist:
			if n.x==x and n.y==y:
				return True
		return False
	def inOpenList(self,x,y):
		for i,n in enumerate(self.openlist):
			if n.x==x and n.y==y:
				return i
		return -1
	def showPath(self,l,cl):
		tm=[]
		for i in self.map:
			tm.append(list(i))
		for i in cl:
			tm[i.y][i.x]=' '
		for i in l:
			tm[i.y][i.x]='X'
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
			from_x,from_y,to_x,to_y=self.getFromTo(coord_marks)

		curCoord=None
		# 1 把起始格添加到开启列表。
		t=Node(None,from_x,from_y,0)
		self.openlist.append(t)
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
			self.closedlist.append(curCoord)

			# c) 对相邻的8格中的每一个
			for item in self.SubNode(curCoord,to_x,to_y):
				# 如果它不在开启列表中，把它添加进去。把当前格作为这一格的父节点。
				# 记录这一格的F,G,和H值。
				i=self.inOpenList(item.x,item.y)
				if i==-1:
					self.openlist.append(item)
					if item.x==to_x and item.y==to_y:
						# 保存路径。从目标格开始，沿着每一格的父节点移动直到回到起始格。这就是你的路径。
						print "find %d"%(item.g,)
						print "%d"%(len(self.closedlist),)
						for i,t in enumerate(self.closedlist): # 删掉起始节点
							if t.x==from_x and t.y==from_y:
								del self.closedlist[i]
								break

						l=[item]
						p=item.parent
						while p:
							l.append(p)
							p=p.parent
						self.showPath(l[1:-1],self.closedlist)
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
	t.getPath(8,5,41,23,'SE','X')

if __name__=='__main__':
	import sys
	from math import sqrt
	run()

