#!/usr/bin/env python
#coding=utf-8

#A*算法总结
#1. 将开始节点放入开放列表(开始节点的F和G值都视为0);
#2. 重复一下步骤:
	#i. 在开放列表中查找具有最小F值的节点,并把查找到的节点作为当前节点;
	#ii. 把当前节点从开放列表删除, 加入到封闭列表;
	#iii. 对当前节点相邻的每一个节点依次执行以下步骤:
		#1. 如果该相邻节点不可通行或者该相邻节点已经在封闭列表中,则什么操作也不执行,继续检验下一个节点;
		#2. 如果该相邻节点不在开放列表中,则将该节点添加到开放列表中, 并将该相邻节点的父节点设为当前节点,同时保存该相邻节点的G和F值;
		#3. 如果该相邻节点在开放列表中, 则判断若经由当前节点到达该相邻节点的G值是否小于原来保存的G值,若小于,则将该相邻节点的父节点设为当前节点,并重新设置该相邻节点的G和F值.
	#iv. 循环结束条件:
		#当终点节点被加入到开放列表作为待检验节点时, 表示路径被找到,此时应终止循环;
		#或者当开放列表为空,表明已无可以添加的新节点,而已检验的节点中没有终点节点则意味着路径无法被找到,此时也结束循环;
#3. 从终点节点开始沿父节点遍历, 并保存整个遍历到的节点坐标,遍历所得的节点就是最后得到的路径;

class Node(object):
	def __init__(self,parent,x,y,target):
		self.parent=parent
		self.x,self.y=x,y
		self.g=0
		# 根据target节点计算H值
		# H值取本节点与目的节点间直线距离的1.2倍
		self.h=sqrt(pow(x-target[0],2)+pow(y-target[1],2))*1.2
	def updateG(self,simple=True):
		u"""根据父节点更新G值,simple指示是否直接使用父节点的g值
		"""
		if simple:
			if self.parent:
				self.g=self.parent.g
				if self.x==self.parent.x or self.y==self.parent.y: # 不是斜角节点
					self.g+=10
				else:		self.g+=14
		else:
			self.g=0
			p=self.parent
			while p:
				if self.x==p.x or self.y==p.y: # 不是斜角节点
					self.g+=10
				else:		self.g+=14
				p=p.parent
		return self.g
	def setParent(self,parent):
		u"""重新设置父节点并更新G值"""
		#if self.parent!=parent:
		self.parent=parent
		self.updateG()
	def __eq__(self,other):
		if isinstance(other,tuple):
			return other[0]==self.x and other[1]==self.y
		elif isinstance(other,Node):
			return (self.x==other.x) and (self.y==other.y)
		else: 	return False
	def __repr__(self):
		return 'Node<(%d,%d),%d+%d=%d>'%(self.x,self.y,self.g,self.h,self.g+self.h)

class AStarTest(object):
	def __init__(self,map_max_x,map_max_y,map_array,unreachable_marks):
		self.openlist,self.closedlist=[],[]
		self.mapMaxX,self.mapMaxY=map_max_x,map_max_y
		self.map=map_array
		self.to_coord=None # 记录目的节点
		self.unreachable=unreachable_marks # 图中代表不可通过的字符集
		logging.basicConfig(level=logging.DEBUG,
	#			format="%(asctime)s %(levelname)s %(funcName)s | %(message)s",
	      format='%(funcName)s %(lineno)d | %(message)s',
	      datefmt='%H:%M:%S',
	      filename=ur'd:\AStar.log',
	      filemode='a')
		# loggin to console
		console=logging.StreamHandler()
		console.setLevel(logging.DEBUG)
		console.setFormatter(logging.Formatter('%(message)s'))
		logging.getLogger('').addHandler(console)

		logging.info(u"%d %d",self.mapMaxX,self.mapMaxY)

	def getSubNode(self,node):
		u""" 返回节点node的有效子节点"""
		subList=[
			(node.x-1,node.y-1),(node.x,node.y-1),(node.x+1,node.y-1),\
			(node.x-1,node.y),                    (node.x+1,node.y),\
			(node.x-1,node.y+1),(node.x,node.y+1),(node.x+1,node.y+1)]
		for x,y in subList:
			if x<self.mapMaxX and x>=0 and y<self.mapMaxY and y>=0: # 坐标值有效
				if self.map[y][x] not in self.unreachable: # 可通行
					if (x,y) not in self.closedlist: # 不在closedlist中
						yield Node(node,x,y,self.to_coord)
	def getPath(self,from_coord,to_coord,coord_marks='SE',show_mark='X'):
		u"""获取两点间的路径
		from_coord 起点
		to_coord 终点
		coord_marks 起点终点标志字符
		show_mark 用来显示路径的字符
		"""
		del self.openlist[:]
		del self.closedlist[:]

		if from_coord==None or to_coord==None: # 需要从图中找到起点和终点
			from_coord,to_coord=self.getFromTo(coord_marks)

		logging.info(u"起点 %s 终点 %s",from_coord,to_coord)
		self.to_coord=to_coord
		curCoord=None
		currGoodG=0 # 记录当前最好的G值
		# 1 把起始格添加到开启列表。
		self.openlist.append(Node(None,*from_coord,target=self.to_coord))
		while self.openlist: # 重复如下的工作：
			# a) 寻找开启列表中F值最低的格子。我们称它为当前格。
			curCoord=self.findCurNode()
			#logging.debug(u"curCoord=%s",curCoord)
			# b) 把它切换到关闭列表。
			self.openlist.remove(curCoord)
			self.closedlist.append(curCoord)

			subs=list(self.getSubNode(curCoord))
			#pprint(subs)
			# c) 对相邻的8格中的每一个
			for item in subs:
				# 如果它不在开启列表中，把它添加进去。把当前格作为这一格的父节点。
				# 记录这一格的F,G,和H值。
				if item not in self.openlist:
					self.openlist.append(item)
					item.updateG()
					if item==to_coord:
						# 保存路径。从目标格开始，沿着每一格的父节点移动直到回到起始格。这就是你的路径。
						logging.info(u"找到路径 %d/%d",item.updateG(),item.updateG(False))
						l=[item,]
						p=item.parent
						while p:
							l.append(p)
							p=p.parent
						l.reverse()
						self.showPath(l,show_mark)
						return

				# 如果它已经在开启列表中，用G值为参考检查新的路径是否更好。更低的G值
				# 意味着更好的路径。如果是这样，就把这一格的父节点改成当前格，并且
				# 重新计算这一格的G和F值。如果你保持你的开启列表按F值排序，改变之后
				# 你可能需要重新对开启列表排序。
				else:
					#logging.debug(u"%s 已经在开启列表中了",item)
					tmpG=self.calcG(item,curCoord) # 以当前节点curCorrd为item暂时的父节点计算G值
					if tmpG<currGoodG or currGoodG==0:
						#logging.debug(u"发现更好的路径")
						item.setParent(curCoord)
		logging.info(u"没有找到路径!")

	def findCurNode(self):
		u"""寻找开启列表中F值最低的格子"""
		return min(self.openlist,key=lambda x:x.g+x.h)


	def calcG(self,item,curCoord):
		u"""计算当节点item以节点curCoord为父节点时的G值"""
		g=curCoord.g
		if item.x==curCoord.x or item.y==curCoord.y: # 不是斜角节点
			g+=10
		else:	g+=14
		return g

	def showPath(self,path,mark='X'):
		u"""以图形方式显示路径"""
		s=StringIO()
		for idxy,i in enumerate(self.map):
			for idxx,j in enumerate(i):
				if (idxx,idxy) in path: # 在路径中
					if (idxx,idxy) in [path[0],path[len(path)-1]]: # 是起点和终点则原样输出
						s.write('%s'%(j,))
					else:
						s.write('%s'%(mark,))
				else:
					s.write('%s'%(j,))
			s.write('\n')
		logging.info(u"\n%s",s.getvalue())
		s.close()

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
		return None

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
	t=AStarTest(len(m[0]),len(m),m,['#'])
	t.getPath(None,None,'SE','X')

if __name__=='__main__':
	import sys
	import logging
	from pprint import pprint
	from cStringIO import StringIO
	from math import sqrt
	run()

