# -*- coding: utf_8 -*-

#sys.path.append(r'd:\javaproj\testPython\src')

## 三目运算符
#x=0.8
#print (x>0.5 and [1] or [0])[0]
#x=0.3
#print (x>0.5 and [1] or [0])[0]

# try except finally 的联合使用
##import traceback
##try:
##	raise EOFError()
##except EOFError:
##	print 'in except EOFError'
##	er = traceback.format_exc() # 打印完整堆栈信息
##	print er
##finally:
##	print 'in finally'

## 获取cookie
#import urllib2
#req=urllib2.Request('http://www.google.com')
#resp=urllib2.urlopen(req)
#cookie=resp.info().getheader('Set-Cookie')
## 将获取的cookie设置回html
#req=urllib2.Request('http://www.google.com')
#req.add_header('Cookie',cookie)
#resp=urllib2.urlopen(req)
# print resp.read()
#print cookie
#instr=raw_input('press ENTER to continue...')
#print 'Done.'

## 另一个获取cookie的例子
#import urllib
#resp=urllib.urlopen('http://www.google.com')
#cookie=resp.info().getheader('Set-Cookie')
#print cookie


## 将字符串转换为16进制
#asscii_string = lambda s: ' '.join(map(lambda c: "%02X" % ord(c), s))
#print asscii_string('4sdr42')

# 将字符串转换为16进制的另外一种方法
##s='4sdr42'
##print ' '.join(["%02X"%(ord(c)) for c in s])

# ini文件读取
##import ConfigParser
##iniFile=ConfigParser.ConfigParser()
##iniFile.readfp(open(r'd:\javaproj\testPython\src\test.ini'))
##print iniFile.get('General','DftOutDir')
##print iniFile.get('Recite','Interval')
##print iniFile.get('General','testnew')


# xml文件解析
#import xml.dom.minidom

# 获取当前行号
##def LINE():
##    import traceback
##    return traceback.extract_stack()[-2][1]
##print LINE()

# 去除重复空格
##import re
##s='sfd   dfd  d af  ee '
##print ' '.join(re.split(r'\s+',s))

# ftp读取文件
##import ftplib
##ftp = ftplib.FTP("192.168.10.103")
##print ftp.login('sedstest','sedstest') # 登录
##print 'welcome msg: ' +ftp.getwelcome() # 获取欢迎信息
##print ftp.cwd('liuqiang_test') # 转换目录
##lists=ftp.nlst() # 获取文件名列表
##print lists
##def funGetFileSize(s):
##	try:
##		return ftp.size(s)
##	except: # 八成是目录
##		return -1
##mapFileSize=map(funGetFileSize,lists)
##print mapFileSize
####ftp.retrbinary("RETR "+"/home/ftptest/filename.txt",f,1024)
##ftp.quit()


##数组高级操作
##1. 抽取数组中不重复的数据
#a=[ x*2 for x in range(1,5) ]*2
#uniq = list(set(a))
#uniq = sorted(set(a))
#b={}
#for x in a:
#	b[x]=1
#uniq = b.keys()
#
##2. 去除在另一个数组中元素
#a = [ x*2 for x in range(1,5) ]
#b = [ x for x in a if x >3 ]
#aonly = [x for x in a if x not in b]
#a_set = set(a)
#b_set = set(b)
#aonly = list(a_set - b_set)
#
##3. 数组排序
#def comp(x,y):
#	if x>y:
#		return -1
#	elif x==y:
#		return 0
#	else :
#		return 1
#unsorted_list = [82, 67, 10, 46, 81, 40, 71, 88, 55]
#unsorted_list.sort(comp)
#
#
##4. 两个数组交、并操作
#a = [ x*2 for x in range(1,5) ]
#b = [ x for x in range(3,7) ]
#a_set = set(a)
#b_set = set(b)
## Union
#print list (a_set | b_set )
##Intersection
#print list(a_set & b_set)
##Difference
#print list(a_set ^ b_set)
#
#
##5. 数组函数map()、filter()、reduce()
##a) map()
##map(function,sequence)为每一个sequence的元素调用function(item) 并把返回值组成一个数组。
#def fun(x): return x*x
#print map(fun,range(0,5))
#
##使用map(None,list1,list2)可以快速把两个数组变成元素对的一个数组
#print map(None,range(0,5),range(100,105))
#
##b) filter()
##filter(function,sequence)返回一个序列，包含了所有调用function(item)后返回值为true的元素。
#unsorted_list = [82, 67, 10, 46, 81, 40, 71, 88, 55]
#def fun(x): return x%2==0
#print filter(fun,unsorted_list)
#
##c) reduce()
##reduce(function,sequence)返回一个单值，首先以数组的前两个元素调用函数function，在以返回值和第三个元素为参数调用，依次执行下去。
##例如，以下程序计算1到10的整数的和
#def add(x,y): return x+y
#print reduce(add,range(0,11))

## 获取程序当前目录
#import os
#print os.path.abspath(".")

## 按任意键继续
#raw_input("Press Enter to continue: ")

## 通过COM接口操作xls文件，需要安装python的win32扩展包
## 从win32com.client模块中导入Dispatch
#from win32com.client import Dispatch
## COM中通过一个字符串来唯一标示一个COM组件
#xlsApp = Dispatch("Excel.Application")
## 添加一个Workbook
#xlsApp.Workbooks.Add()
## 获得Workbook(1)的引用
#xlsBook = xlsApp.Workbooks(1)
## 为Sheet1表赋值
#xlsBook.Sheets[0].Cells(1,1).Value = '25'
## 获取值
#print xlsBook.Sheets[0].Cells(1,1).Value
## 使用公式来给单元格赋值
#xlsBook.Sheets[0].Cells(1,2).Formula = '=A1+10'
#print xlsBook.Sheets[0].Range('A1:B1').Value
## 获取一个区块的值，返回一个元组
#print xlsBook.Sheets[0].Range('F2:F4').Value
## 为Sheet1改名
#xlsBook.Sheets[0].Name = 'The first sheet'
## 保存一个Workbook到xls文件
#xlsBook.SaveAs(Filename = 'C:\\testsheet.xls')
## 如果你希望看到整个操作的过程，可以这样操作让操作可见
#xlsApp.Visible = 1
## 让操作过程不可见
#xlsApp.Visible = 0
## 关闭Workbook
#xlsBook.Close(SaveChanges = 0)
## 释放xlsApp
#del xlsApp


##由实例访问类属性，由实例访问类的私有方法
#class Test:
#	pubname=None # 类public属性
#	__priname="default" # 类private属性
#	def __init__(self,name):
#		self.pubname="instance public "+name
#		self.__priname="instance private "+name
#		self.__class__.pubname="class public "+name
#		self.__class__.__priname="class private "+name
#
#	def __hello(self):
#		print 'this is private method!'
#t=Test('testok')
## 访问类共有属性
#print Test.pubname # 直接访问类的公有属性
#print t.__class__.pubname # 通过实例访问类的公有属性
## 访问类私有属性
#print Test._Test__priname # 直接访问类的私有属性
#print t.__class__._Test__priname # 通过实例访问类的私有属性
## 访问实例共有/私有属性
#print t.pubname # 访问实例的公有属性
#print t._Test__priname # 访问实例的私有属性
## 访问类私有方法
#t._Test__hello()



## try..catch块无异常时对应的else语句才会被执行
#import sys
#try:
#	s = raw_input('Enter something --> ')
#except EOFError:
#	print '\nWhy did you do an EOF on me?'
#	sys.exit() # exit the program
#except:
#	print '\nSome error/exception occurred.'
#	# here, we are not exiting the program
#else: print 'No except occurred.'
#print 'Done'

## 打印字符串的原始形式，'\n'会被打出而不是被打成回车
#import os
#print repr(os.linesep) # 获取当前系统的换行符
#print repr(os.sep) # 获取系统的目录分隔符
#

# unicode->其它编码
# 例如:a为unicode编码 要转为gb2312
#a=u"测试"
#print a.encode('gb2312')
#print "%s" % a.encode('gb2312')

## 其它编码->unicode
## 例如:b为gb2312编码,要转为unicode.
#t=u"东东"
#b=t.encode("gb2312")
#unicode(b, 'gb2312') # 方法1
#b.decode('gb2312')  # 方法2

## 编码1 -> 编码2
## 可以先转为unicode再转为编码2
## 如gb2312转big5
#t=u"西西"
#c=t.encode("gb2312")
#unicode(c, 'gb2312').encode('big5')

## 判断字符串的编码
#s="erer"
#us=u"dfdf"
#print isinstance(s, str) # 用来判断是否为一般字符串
#print isinstance(us, str) # 用来判断是否为一般字符串
#print isinstance(s, unicode) # 用来判断是否为unicode字符串
#print isinstance(us, unicode) # 用来判断是否为unicode字符串

## 获取本地语言及编码
#import locale
#print locale.getdefaultlocale()

## property基本用法,使用property的类一定要继承自object，否则会有问题
#class TestProperty(object): # 本例使用类私有成员__width存放实际数据
#	__width=7
#	def _Width(self):
#		return self.__class__.__width
#	def _setWidth(self,width):
#		self.__class__.__width=width
#	def _Area(self):
#		return self.__class__.__width*self.__class__.__width
#	area=property(fget=_Area)
#	width=property(fget=_Width,fset=_setWidth)
#
#tp=TestProperty()
#print tp.width
#print tp.area
#tp.width=8
#print tp.width
#print tp.area


## 借助property实现只读属性
#class RdOnlyProperty(object):
#	"""a sample class to show how to define a read-only property"""
#	def __init__(self):
#		self._age=29
#
#	@property
#	def age(self):
#		"""this is a readonly property on class RdOnlyProperty~"""
#		return self._age
#rop=RdOnlyProperty()
#print rop.age

## print object's callable methods and their's docstrings
## 打印出一个对象的可调用的方法及其docstring
#class tmpClass:
#	def __init__(self):
#		"""__init__ of tmpClass!"""
#		pass
#	def fun1(self):
#		"""this is
#		fun1 in tmpClass!"""
#		pass
#	def fun2(self):
#		'''this is fun2 in
#		tmpClass~~~'''
#		pass
#def testFun(object,collapse=True,spacing=1):
#	processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
#	methodList=[method for method in dir(object) if callable(getattr(object,method))]
#	print "\n".join(["%s==%s" %
#		(method.ljust(spacing),processFunc(str(getattr(object, method).__doc__)))
#		for method in methodList])
#testFun(tmpClass)

## 定义三个方便调试的函数 watch、trace和raw
## 可打印包含文件名、行数、模块名和函数名的调试信息，输出变量值或提示信息
#import traceback
#traceOutput=sys.stdout
#watchOutput=sys.stdout
#rawOutput=sys.stdout
## calling 'watch(secretOfUniverse)' prints out something like:
## File "trace.py", line 57, in _ _testTrace
##    secretOfUniverse <int> = 42
#watch_format = ('File "%(fileName)s", line %(lineNumber)d, in'
#	' %(methodName)s\n   %(varName)s <%(varType)s>'
#	' = %(value)s\n\n')
#def watch(variableName):
#	if __debug__:
#		stack = traceback.extract_stack()[-2:][0]
#		actualCall = stack[3]
#		if actualCall is None:
#			actualCall = "watch([unknown])"
#		left = actualCall.find('(')
#		right = actualCall.rfind(')')
#		paramDict = dict(varName=actualCall[left+1:right].strip(),
#			varType=str(type(variableName))[7:-2],
#			value=repr(variableName),
#			methodName=stack[2],
#			lineNumber=stack[1],
#			fileName=stack[0])
#		watchOutput.write(watch_format % paramDict)
## calling 'trace("this line was executed")' prints out something like:
## File "trace.py", line 64, in ?
##    this line was executed
#trace_format = ('File "%(fileName)s", line %(lineNumber)d, in'
#								' %(methodName)s\n   %(text)s\n\n')
#def trace(text):
#	if __debug__:
#		stack = traceback.extract_stack( )[-2:][0]
#		paramDict = dict(text=text,
#										 methodName=stack[2],
#										 lineNumber=stack[1],
#										 fileName=stack[0])
#		watchOutput.write(trace_format % paramDict)
## calling 'raw("some raw text")' prints out something like:
## Just some raw text
#def raw(text):
#	if __debug__:
#		rawOutput.write(text)
## 测试用例
#def __testTrace( ):
#	secretOfUniverse = 42
#	watch(secretOfUniverse)
#if __name__ == "__main__":
#	a = "something else"
#	watch(a)
#	__testTrace()
#	trace("This line was executed!")
#	raw("Just some raw text...")

## 类属性的使用
#class testStaticMember:
#	title="this is a static var!"
#	def __init__(self):
#		testStaticMember.title="THIS IS A STATIC VAR!"
#	@staticmethod
#	def myStaticMethod():
#		print testStaticMember.title
#testStaticMember.myStaticMethod()
#m=testStaticMember()
#testStaticMember.myStaticMethod()


# test sqlite3 operation
#import sqlite3
#conn=sqlite3.connect(':memory:')
#conn.execute('CREATE TABLE tb_test(id integer primary key,c_name text,e_name text,file_cnt integer)')
#conn.execute("INSERT INTO tb_test VALUES(1,'testname',NULL,2)")
#conn.execute("INSERT INTO tb_test VALUES(2,'测试','test',3)")
#conn.text_factory=str
#conn.row_factory=sqlite3.Row
#for row in conn.execute('select * from tb_test'):
#	assert row[0]==row["id"]
#	assert row[1]==row['c_name']
#	assert row[2]==row['e_name']
#	assert row[3]==row['file_cnt']
#	print row['id'],row['c_name'].decode('utf-8').encode('gb18030'),row['e_name'],row['file_cnt']

# 测试打印出发生异常时的各级堆栈信息, 包括各帧的本地变量
#import sys
#def fun():
#	i = 120
#	for data in i:
#		print data
#
#def test():
#	j=50
#	fun()
#
#def print_tb():
#	_type, _value, tb = sys.exc_info()
#	print _type,_value
#	print
#	while tb:
#		print "file: %s,func %d" % (tb.tb_frame.f_code.co_filename,tb.tb_frame.f_code.co_firstlineno)
#		print "locals:",tb.tb_frame.f_locals
#		print "call point:",tb.tb_lineno
#		print "*"*30
#		tb = tb.tb_next
#
#def main():
#	m=60
#	j={}
#	try:
#		test()
#	except:
#		print_tb()
##		raise
#if __name__=="__main__":
#	main()
#
# 计算list中重复字符串出现次数的有效算法
#str_list=('aaa','abb','acb','bab','aba','aba','bbb','abb','aaa','bbb','aba','bbb','aba')
#list=[]
#import random
#for i in range(0,100**2):
##	list.append(random.randrange(1,10))
#	list.append(random.choice(str_list)) # 随机选择str_list中的字符串添加到list中
#di={} # key为字符串,value为此字符串在list中出现的次数
#for item in list:
#	di[item]=di.get(item,0)+1 # 关键是这句!
#
#print di
#cnt=0
#for v in di.itervalues():
#	cnt+=v
#print "v=",cnt

## 用于判断一种全排列是否是N皇后问题的有效解
## 1) lst为列表, lst[i]=x 代表第i行的第x列处放一个棋子
## 2) lst为一维数组, 保证了所有棋子不同行,
## 3) lst中数字互不相同, 保证了所有棋子不同列
## 4）判断两个棋子是否同斜线: 对任意lst[i]=x和lst[j]=y，保证|i-j|!=|x-y|
#def isRst(lst):
#	for i in range(1,len(lst)-1):
#		for j in range(i+1,len(lst)):
#			if abs(i-j)==abs(lst[i]-lst[j]):
#				return False
#	return True
#
## 获得连续N个数字的全排列算法,非递归
##    初始 lst为[0,1,2,3,...,N], len(lst)为N, lst[0]不参与运算
##    计算完成后lst为[0,N,...,3,2,1]
#def permutation(lst):
#	cnt=1
#	rstCnt=1
#	leng=len(lst)-1
#	n=leng
#	print "n=%d"%(n)
#	m=n-1
#	old_m=m
#	print "*******************(%d)%s\n" % (cnt,lst)
#	cnt+=1
#	while n>=1:
#		while m>=1:
##			print "if [%d]=%d > [%d]=%d ?" % (n,lst[n],m,lst[m])
#			if lst[n]>lst[m]:
#				x,y,aft=lst[m],lst[n],[]
#				lst[n]=x
#				lst[m]=y
#				aft=lst[m+1:]
##				print "aft=",aft
#				aft.sort()
#				lst=lst[:m+1]
#				lst.extend(aft)
#				old_m=m
#				n=leng
#				m=n-1
##				print "*******************(%d)%s, old_m=%d\n" % (cnt,lst,old_m)
##				print "*******************(%d)%s\n" % (cnt,lst) # 此时一个新排列产生
#				if isRst(lst): # 此处判断是否是N皇后问题的有效解
#					print "*******************(%d)%s\n" % (rstCnt,lst)
#					rstCnt+=1
#				cnt+=1
#
#			else:
#				if m==old_m:
#					break
#				else:
#					m-=1
#
#		n-=1
#		if n==old_m:
#			n=leng
#			old_m-=1
#		m=n-1
#
## 测试全排列函数
#l=range(0,9)
#from time import clock
#s=clock()
#permutation(l)
#f=clock()
#print (f-s)

# 用1元,2元,5元,10元,20元,50元的纸币组成100元,共有多少种情况 (4562种).
#cnt=0
#for a in range(0,100/50+1): # 50
#	for b in range(0,(100-a*50)/20+1): # 20
#		for c in range(0,(100-a*50-b*20)/10+1): # 10
#			for d in range(0,(100-a*50-b*20-c*10)/5+1): # 5
#				for e in range(0,(100-a*50-b*20-c*10-d*5)/2+1): # 2
#					cnt+=1
#print cnt

#问题描述如下:
#有2.5亿个整数(这2.5亿个整数存储在一个数组里面,至于数组是放在外存还是内存,没有进一步具体说明);
#要求找出这2.5亿个数字里面,不重复的数字的个数;
#另外，可用的内存限定为600M;
#要求算法尽量高效,最优;
# 思路:
# 设2.5亿个整数在List中,len(List)=2.5亿
# 正整数范围 2的31次方
# 数组a有[2的31次方]个bit, b有2.5亿个bit 初始都为0
#第一次遍历 List
#  对List[i]==x (i<2.5亿, 0<x<2的31次方), 则:
#     if a[x]==0 then a[x]=1
#     else b[i]=1
#第二次遍历 List
#  对List[i]==x, 则:
#    if b[i]==1 then a[x]=0
#最后 计算a中为1的bit的个数，即是不重复数字的个数(如果需要找到对应的在List中的索引,则需遍历b, 满足b[i]==0且a[i]==1的i即为不重复的数字的索引)


#给你一个单词a，如果通过交换单词中字母的顺序可以得到另外的单词b，那么定义b是a的兄弟单词。现在给你一个字典，用户输入一个单词，让你根据字典找出这个单词有多少个兄弟单词。  （这道题面试官说有O(1) 的解法，。。。。。）
# 思路:所有兄弟单词都可以写成一种形式 AxByCz..., 表示单词由x个A,y个B,z个C组成,ABC是排序后的.

# 比如  live和evil  --排序--> eilv
#  google --> eg2lo2


##假如当前字符串是: 2009-02-06 17:02:48.024179
##如何能转换成: 20090206170248024179 (就是仅保留数字部分) ?
#a = '2009-02-06 17:02:48.024179'
## 方法1
#b = ''.join([c for c in a if c.isdigit()])
#print b
## 方法2
#c=filter(str.isdigit,a)
#print c
## 方法3
#import re
#d=re.sub('[^\d]',"",a)
#print d

## 快速排序
#def qsort(L):
# if L == []: return []
# return qsort([x for x in L[1:] if x< L[0]]) + L[0:1] + \
#   qsort([x for x in L[1:] if x>=L[0]])
#
#ls=[113,1,5,7,3,9,4,6,8,55,83,52,762,72,6,4]
#print qsort(ls)
## 选择排序
#def selection_sort(L):
# if L==[]: return []
#
# length=len(L)
# for x in xrange(length):
#  lowest=x
#  for y in xrange(x+1,length):
#   if L[y]<L[lowest]:
#    lowest=y
#  temp=L[x]
#  L[x]=L[lowest]
#  L[lowest]=temp
#
# return L
#
#ls=[113,1,5,7,3,9,4,6,8,55,83,52,762,72,6,4]
#print selection_sort(ls)
#


#def conv(i):
# if len(i)==2:
#  return chr(int(i,16))
# else:
#  return chr(int(i[0:2],16))+i[2:]
#s=r'\xb7\xa2\xc9\xfa\xd2\xe2\xcd\xe2\xa1\xa3' #sys.argv[1]
#print s.replace('\\x',' ').split()
#print ' '.join(map(conv, s.replace('\\x',' ').split()))


#s=r'\xce\xde\xd0\xa7\xb5\xc4\xc0\xe0\xb1\xf0\xd7\xd6\xb7\xfb\xb4\xae' # u"无效的类别字符串"
#s=r'\xb7\xa2\xc9\xfa\xd2\xe2\xcd\xe2\xa1\xa3' # u"发生意外"
#def conv(i):
# if len(i)==2:
#  return chr(int(i,16))
# else:
#  return chr(int(i[0:2],16))+i[2:]
#print ''.join(map(conv, s.replace('\\x',' ').split()))



##Trilogy公司的笔试题
##如果n为偶数，则将它除以2，
##如果n为奇数，则将它加1或者减1。
##问对于一个给定的n，怎样才能用最少的步骤将它变到1。
##亠
##n=   61
##n--   60
##n/2   30
##n/2   15
##n++   16
##n/2   8
##n/2   4
##n/2   2
##n/2   1
#def func(x):
#	cnt=0
#	while x!=1:
#		cnt+=1
#		if not x%2:
#			x=x/2
#		elif x==3:
#			x=x-1
#		else:
#			if not ((x+1)/2)%2 :
#				x=x+1
#			else:
#				x=x-1
#		print "(%d)x=%d" % (cnt,x)
#	return cnt
##for x in xrange(1,101):
##	print "%d %d" % (,func(x))
#print func(100)


##整形数组平衡点问题: 平衡点指左边的整数和等于右边的整数和，
##求出平衡点位置，要求输入的数组可能是GB级
#def balancePoint(L):
#	sumAll=sum(L)
#	print "sumAll=%d" % (sumAll,)
#	sumNow=0
#	rst=[]
#	for i in xrange(len(L)):
#		if sumNow==sumAll-sumNow-L[i]:
#			rst.append(i)
#			print "*"*50
#		sumNow+=L[i]
#	print "rst=%s" % (rst)
#	return rst
#
#import random
#lst=[]
#for x in xrange(1000):
#	lst.append(random.randint(1,10))
#balancePoint(lst)
#

##实现一个去除整型数组中绝对值相同的数字.最后返回一个长度
#import random
#L,M=[],[]
#for x in xrange(10):
#	L.append(random.randint(-10,10))
#print L
#print "%d" % (len(L),)
##M=map(abs,L)
##M=[x for x in M if M.count(x)==1]
##print M
##print "%d" % (len(M))
#print "%d" % (len([x for x in map(abs,L) if map(abs,L).count(x)==1])) # 关键是这句


## 求最大公约数
#def max_common_divisor(a,b):
#	t=1
#	for i in xrange(2,max(a,b)+1):
#		while a%i==0 and b%i==0:
##			print i
#			t*=i
#			a=a/i
#			b=b/i
#	print t
#max_common_divisor(50,100)
#max_common_divisor(12,8)

## 产生组合
#rst=[]
#def perm(L):
#	print L
#	global rst
#	tmp_list=[]
#	for i in xrange(2**len(L)):
#		for j in xrange(len(L)):
#			if i & (1<<len(L)-1-j):
#				tmp_list.append(L[j])
#		rst.append(tmp_list)
#		tmp_list=[]
#lst=[1,2,3,4,5,6,7,8]
#perm(lst)
#print len(rst)
## 验证是否有重复
#di={}
#for x in rst:
#	di[str(x)]=di.get(str(x),0)+1
#for i in di.itervalues():
#	if i!=1:
#		print "dup found!"
#		break
#else:
#	print "no dup found."
#print len(di)
#print rst


## 身份证号码15位转18位时最后一位的算法
## 1) 计算 S=∑(aؗi),  即计算前17位的加权和
##     i----表示号码字符从由至左包括校验码在内的位置序号
##     ai----表示第i位置上的号码字符值
##     Wi----表示第i位置上的加权因子,其数值依据公式Wi=2(n-1)(mod 11)计算得
## 2）校验码为Y[S(mod 11)], Y为校验码表
##L='11010819790124631'
##L='11010519491231002'
##L='44052418800101001'
#L='34052419800101001'
#def ID15to18_getcheckno(L):
#	Wi=[]
#	# 加权因子 可以直接使用而不必每次计算生成 Wi=(7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2)
#	for n in xrange(18,1,-1):
#		Wi.append((2**(n-1))%11)
#	# 校验码
#	Y=(1,0,'X',9,8,7,6,5,4,3,2)
#	S=0
#	for i in xrange(17):
#		S+=int(L[i])*Wi[i]
#	print Y[S%11]
#ID15to18_getcheckno(L)

## 求pi值
#from string import atol, zfill
#def calc_pi(n):
#	r=atol('6'+zfill('0',n+1))
#	p=0L
#	k=0L
#	c=r/2
#	d=c/(2*k+1)
#	while d>0L:
#		p=p+d
#		k=k+1
#		k2=2*k
#		c=c*(k2-1)/(4*k2)
#		d=c/(k2+1)
#	return p
#print calc_pi(40) # 打印小数点后40位


## 返回汉字的拼音首字母,只支持GB汉字编码中3755个一级常用汉字,不支持多音字,默认输入utf8
##庠
## 国标码字符集GB2312-80收录了6763个常用汉字,其中一级汉字3755个,二级汉字3008个.另外还收录了各种符号682个,合计7445个.
##第一级汉字是常用汉字,计3755个,置于16-55区,按汉语拼音字母/笔形顺序排列;第二级汉字是次常用汉字,计3008个,置于56～87区,按部首／笔画顺序排
#def get_Mutil_CnFirstLetter(str):
#		index = 0;
#		strReturnCn = u""
#		print "len(str)=%s" % len(str)
#		while index <= (len(str)-1):
#				#print "strReturnCn=%s" % strReturnCn
#				#print get_cn_first_letter(str[index:index+2],"GBK")
#				print "idx=%d,%s" % (index,str[index:index+1].encode('gb2312'))
#				strReturnCn += get_cn_first_letter(str[index:index+1])
#				index += 1;
#		return strReturnCn;
#def get_cn_first_letter(str,codec="UTF8"):
##    if codec!="GBK":
##        if codec!="unicode":
##            str=str.decode(codec)
#		str=str.encode("GBK")
#
#		if str<"\xb0\xa1" or str>"\xd7\xf9":
#				return str
#		if str<"\xb0\xc4":
#				return "a"
#		if str<"\xb2\xc0":
#				return "b"
#		if str<"\xb4\xed":
#				return "c"
#		if str<"\xb6\xe9":
#				return "d"
#		if str<"\xb7\xa1":
#				return "e"
#		if str<"\xb8\xc0":
#				return "f"
#		if str<"\xb9\xfd":
#				return "g"
#		if str<"\xbb\xf6":
#				return "h"
#		if str<"\xbf\xa5":
#				return "j"
#		if str<"\xc0\xab":
#				return "k"
#		if str<"\xc2\xe7":
#				return "l"
#		if str<"\xc4\xc2":
#				return "m"
#		if str<"\xc5\xb5":
#				return "n"
#		if str<"\xc5\xbd":
#				return "o"
#		if str<"\xc6\xd9":
#				return "p"
#		if str<"\xc8\xba":
#				return "q"
#		if str<"\xc8\xf5":
#				return "r"
#		if str<"\xcb\xf9":
#				return "s"
#		if str<"\xcd\xd9":
#				return "t"
#		if str<"\xce\xf3":
#				return "w"
#		if str<"\xd1\x88":
#				return "x"
#		if str<"\xd4\xd0":
#				return "y"
#		if str<"\xd7\xf9":
#				return "z"
#
#if __name__== '__main__':
##		print get_cn_first_letter(u"我")
##		print get_cn_first_letter(u"们")
##		print get_cn_first_letter(u"他")
##		print get_cn_first_letter(u"是")
##		print get_cn_first_letter(u"大")
##		print get_Mutil_CnFirstLetter(u"大埔的d")
##		print get_Mutil_CnFirstLetter(u"我这里有部分代码需要的话")
#
#		import sys
#		reload(sys)
#		sys.setdefaultencoding('utf8')
#		L=[0xB0A1, 0xB0C5,0xB2C1,0xB4EE,0xB6EA,0xB7A2,0xB8C1,0xB9FE,0xBBF7,0xBBF7,0xBFA6,0xC0AC,0xC2E8,0xC4C3,0xC5B6,0xC5BE,0xC6DA,0xC8BB,0xC8F6,0xCBFA,0xCDDA,0xCDDA,0xCDDA,0xCEF4,0xD1B9,0xD4D1,0xD8A1,]
#		# get_cn_first_letter函数的简写形式
#		get_sm = lambda c:chr(len(filter(lambda x : x<reduce(lambda x,y:ord(x)*256+ord(y),c),L))+96)
#		X=u"类型的汉字转换为数字的函数"
#		S=""
#		print X.encode('gbk')
#		for x in X:
#			S+=get_sm(x.encode("GBK"))
#		print S








## 阳历转农历并获取干支名称
#def getGetDayOf(wYear,wMonth,wDay):
#	cTianGan=("甲","乙","丙","丁","戊","己","庚","辛","壬","癸")
#	# 地支名称
#	cDiZhi=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")
#	# 属相名称
#	cShuXiang=(u"鼠",u"牛",u"虎",u"兔",u"龙",u"蛇",u"马",u"羊",u"猴",u"鸡",u"狗",u"猪")
#	# 农历日期名
#	cDayName= (u"*",u"初一",u"初二",u"初三",u"初四",u"初五","u初六",u"初七",u"初八",u"初九",u"初十",u"十一",u"十二",u"十三",u"十四",u"十五",u"十六",u"十",u"十八",u"十九",u"二十",u"廿一",u"廿二",u"廿三",u"廿四",u"廿五",u"廿六",u"廿七",u"廿八",u"廿九",u"三十")
#	# 农历月份名
#	cMonName= (u"*",u"正",u"二",u"三",u"四",u"五",u"六",u"七",u"八",u"九",u"十",u"十一",u"腊")
#
#	# 公历每月前面的天数
#	wMonthAdd= (0,31,59,90,120,151,181,212,243,273,304,334)
#	# 农历数据
#	wNongliData=(2635,333387,1701,1748,267701,694,2391,133423,1175,396438,3402,3749,331177,1453,694,201326,2350,465197,3221,3402,400202,2901,1386,267611,605,2349,137515,2709,464533,1738,2901,330421,1242,2651,199255,1323,529706,3733,1706,398762,2741,1206,267438,2647,1318,204070,3477,461653,1386,2413,330077,1197,2637,268877,3365,531109,2900,2922,398042,2395,1179,267415,2635,661067,1701,1748,398772,2742,2391,330031,1175,1611,200010,3749,527717,1452,2742,332397,2350,3222,268949,3402,3493,133973,1386,464219,605,2349,334123,2709,2890,267946,2773,592565,1210,2651,395863,1323,2707,265877)
#	wCurYear,wCurMonth,wCurDay=0,0,0
#	nTheDate,nIsEnd,m,k,n,i,nBit=0,0,0,0,0,0,0
#	szNongli,szNongliDay,szShuXiang="","",""
#	# 取当前公历年、月、日
#	wCurYear = wYear
#	wCurMonth = wMonth
#	wCurDay = wDay
#	# 计算到初始时间1921年2月8日的天数: 1921-2-8(正月初一)
#	nTheDate = (wCurYear - 1921) * 365 + (wCurYear - 1921) / 4 + wCurDay + wMonthAdd[wCurMonth - 1] - 38
#	if wCurYear % 4==0 and wCurMonth > 2:
#		nTheDate = nTheDate + 1
#
#	# 计算农历天干、地支、月、日
#	nIsEnd = 0
#	m = 0
#	while nIsEnd != 1:
#		if wNongliData[m] < 4095:
#			k = 11
#		else:
#			k = 12
#		n = k
#		while n>=0:
#			# 获取wNongliData(m)的第n个二进制位的值
#			nBit = wNongliData[m]
#			for i in range(1,n+1):
#				nBit = nBit/2
#
#			nBit = nBit % 2
#
#			if nTheDate <= (29 + nBit):
#				nIsEnd = 1
#				break
#
#			nTheDate = nTheDate - 29 - nBit
#			n = n - 1
#
#		if nIsEnd:
#			break
#		m = m + 1
#
#	wCurYear = 1921 + m
#	wCurMonth = k - n + 1
#	wCurDay = nTheDate
#	if k == 12:
#		if wCurMonth == wNongliData[m] / 65536 + 1:
#			wCurMonth = 1 - wCurMonth
#		elif wCurMonth > wNongliData[m] / 65536 + 1:
#			wCurMonth = wCurMonth - 1
#
#	# 生成农历天干、地支、属相 ==> wNongli
#	szShuXiang=u"%s" % (cShuXiang[((wCurYear - 4) % 60) % 12],)
#	szNongli=u"%s(%s%s)年" % (szShuXiang,cTianGan[((wCurYear - 4) % 60) % 10],cDiZhi[((wCurYear - 4) % 60) % 12])
#
#	# 生成农历月、日 ==> wNongliDay
#	if wCurMonth < 1:
#		szNongliDay=u"闰%s" % (cMonName[-1 * wCurMonth],)
#	else:
#		szNongliDay=cMonName[wCurMonth]
#
#	szNongliDay+=u"月"
#	szNongliDay+=cDayName[wCurDay]
#	return szNongli+szNongliDay
#
#gLunarHolDay=(
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1901
#0x96,0xA4,0x96,0x96,0x97,0x87,0x79,0x79,0x79,0x69,0x78,0x78,#1902
#0x96,0xA5,0x87,0x96,0x87,0x87,0x79,0x69,0x69,0x69,0x78,0x78,#1903
#0x86,0xA5,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x78,0x87,#1904
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1905
#0x96,0xA4,0x96,0x96,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1906
#0x96,0xA5,0x87,0x96,0x87,0x87,0x79,0x69,0x69,0x69,0x78,0x78,#1907
#0x86,0xA5,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1908
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1909
#0x96,0xA4,0x96,0x96,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1910
#0x96,0xA5,0x87,0x96,0x87,0x87,0x79,0x69,0x69,0x69,0x78,0x78,#1911
#0x86,0xA5,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1912
#0x95,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1913
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1914
#0x96,0xA5,0x97,0x96,0x97,0x87,0x79,0x79,0x69,0x69,0x78,0x78,#1915
#0x96,0xA5,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1916
#0x95,0xB4,0x96,0xA6,0x96,0x97,0x78,0x79,0x78,0x69,0x78,0x87,#1917
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x77,#1918
#0x96,0xA5,0x97,0x96,0x97,0x87,0x79,0x79,0x69,0x69,0x78,0x78,#1919
#0x96,0xA5,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1920
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x78,0x79,0x78,0x69,0x78,0x87,#1921
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x77,#1922
#0x96,0xA4,0x96,0x96,0x97,0x87,0x79,0x79,0x69,0x69,0x78,0x78,#1923
#0x96,0xA5,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1924
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x78,0x79,0x78,0x69,0x78,0x87,#1925
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1926
#0x96,0xA4,0x96,0x96,0x97,0x87,0x79,0x79,0x79,0x69,0x78,0x78,#1927
#0x96,0xA5,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1928
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1929
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1930
#0x96,0xA4,0x96,0x96,0x97,0x87,0x79,0x79,0x79,0x69,0x78,0x78,#1931
#0x96,0xA5,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1932
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1933
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1934
#0x96,0xA4,0x96,0x96,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1935
#0x96,0xA5,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1936
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1937
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1938
#0x96,0xA4,0x96,0x96,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1939
#0x96,0xA5,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1940
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1941
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1942
#0x96,0xA4,0x96,0x96,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1943
#0x96,0xA5,0x96,0xA5,0xA6,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1944
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1945
#0x95,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x78,0x69,0x78,0x77,#1946
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1947
#0x96,0xA5,0xA6,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#1948
#0xA5,0xB4,0x96,0xA5,0x96,0x97,0x88,0x79,0x78,0x79,0x77,0x87,#1949
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x78,0x79,0x78,0x69,0x78,0x77,#1950
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x79,0x79,0x79,0x69,0x78,0x78,#1951
#0x96,0xA5,0xA6,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#1952
#0xA5,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1953
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x78,0x79,0x78,0x68,0x78,0x87,#1954
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1955
#0x96,0xA5,0xA5,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#1956
#0xA5,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1957
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1958
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1959
#0x96,0xA4,0xA5,0xA5,0xA6,0x96,0x88,0x88,0x88,0x78,0x87,0x87,#1960
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1961
#0x96,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1962
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1963
#0x96,0xA4,0xA5,0xA5,0xA6,0x96,0x88,0x88,0x88,0x78,0x87,0x87,#1964
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1965
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1966
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1967
#0x96,0xA4,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#1968
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1969
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1970
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x79,0x69,0x78,0x77,#1971
#0x96,0xA4,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#1972
#0xA5,0xB5,0x96,0xA5,0xA6,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1973
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1974
#0x96,0xB4,0x96,0xA6,0x97,0x97,0x78,0x79,0x78,0x69,0x78,0x77,#1975
#0x96,0xA4,0xA5,0xB5,0xA6,0xA6,0x88,0x89,0x88,0x78,0x87,0x87,#1976
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#1977
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x78,0x87,#1978
#0x96,0xB4,0x96,0xA6,0x96,0x97,0x78,0x79,0x78,0x69,0x78,0x77,#1979
#0x96,0xA4,0xA5,0xB5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#1980
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x77,0x87,#1981
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1982
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x78,0x79,0x78,0x69,0x78,0x77,#1983
#0x96,0xB4,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x87,#1984
#0xA5,0xB4,0xA6,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#1985
#0xA5,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#1986
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x79,0x78,0x69,0x78,0x87,#1987
#0x96,0xB4,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#1988
#0xA5,0xB4,0xA5,0xA5,0xA6,0x96,0x88,0x88,0x88,0x78,0x87,0x87,#1989
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x79,0x77,0x87,#1990
#0x95,0xB4,0x96,0xA5,0x86,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1991
#0x96,0xB4,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#1992
#0xA5,0xB3,0xA5,0xA5,0xA6,0x96,0x88,0x88,0x88,0x78,0x87,0x87,#1993
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1994
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x76,0x78,0x69,0x78,0x87,#1995
#0x96,0xB4,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#1996
#0xA5,0xB3,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#1997
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#1998
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#1999
#0x96,0xB4,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#2000
#0xA5,0xB3,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#2001
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#2002
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#2003
#0x96,0xB4,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#2004
#0xA5,0xB3,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#2005
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2006
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x69,0x78,0x87,#2007
#0x96,0xB4,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x87,0x78,0x87,0x86,#2008
#0xA5,0xB3,0xA5,0xB5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#2009
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2010
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x78,0x87,#2011
#0x96,0xB4,0xA5,0xB5,0xA5,0xA6,0x87,0x88,0x87,0x78,0x87,0x86,#2012
#0xA5,0xB3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x87,#2013
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2014
#0x95,0xB4,0x96,0xA5,0x96,0x97,0x88,0x78,0x78,0x79,0x77,0x87,#2015
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x87,0x88,0x87,0x78,0x87,0x86,#2016
#0xA5,0xC3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x87,#2017
#0xA5,0xB4,0xA6,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2018
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x79,0x77,0x87,#2019
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x97,0x87,0x87,0x78,0x87,0x86,#2020
#0xA5,0xC3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#2021
#0xA5,0xB4,0xA5,0xA5,0xA6,0x96,0x88,0x88,0x88,0x78,0x87,0x87,#2022
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x79,0x77,0x87,#2023
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x97,0x87,0x87,0x78,0x87,0x96,#2024
#0xA5,0xC3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#2025
#0xA5,0xB3,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#2026
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#2027
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x97,0x87,0x87,0x78,0x87,0x96,#2028
#0xA5,0xC3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#2029
#0xA5,0xB3,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#2030
#0xA5,0xB4,0x96,0xA5,0x96,0x96,0x88,0x78,0x78,0x78,0x87,0x87,#2031
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x97,0x87,0x87,0x78,0x87,0x96,#2032
#0xA5,0xC3,0xA5,0xB5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x86,#2033
#0xA5,0xB3,0xA5,0xA5,0xA6,0xA6,0x88,0x78,0x88,0x78,0x87,0x87,#2034
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2035
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x97,0x87,0x87,0x78,0x87,0x96,#2036
#0xA5,0xC3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x86,#2037
#0xA5,0xB3,0xA5,0xA5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#2038
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2039
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x97,0x87,0x87,0x78,0x87,0x96,#2040
#0xA5,0xC3,0xA5,0xB5,0xA5,0xA6,0x87,0x88,0x87,0x78,0x87,0x86,#2041
#0xA5,0xB3,0xA5,0xB5,0xA6,0xA6,0x88,0x88,0x88,0x78,0x87,0x87,#2042
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2043
#0x95,0xB4,0xA5,0xB4,0xA5,0xA6,0x97,0x87,0x87,0x88,0x87,0x96,#2044
#0xA5,0xC3,0xA5,0xB4,0xA5,0xA6,0x87,0x88,0x87,0x78,0x87,0x86,#2045
#0xA5,0xB3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x88,0x78,0x87,0x87,#2046
#0xA5,0xB4,0x96,0xA5,0xA6,0x96,0x88,0x88,0x78,0x78,0x87,0x87,#2047
#0x95,0xB4,0xA5,0xB4,0xA5,0xA5,0x97,0x87,0x87,0x88,0x86,0x96,#2048
#0xA4,0xC3,0xA5,0xA5,0xA5,0xA6,0x97,0x87,0x87,0x78,0x87,0x86,#2049
#0xA5,0xC3,0xA5,0xB5,0xA6,0xA6,0x87,0x88,0x78,0x78,0x87,0x87)#2050
#
#def l_GetLunarHolDay(iYear,iMonth,iDay):
#	Flag,Day=0,0
#	Flag=gLunarHolDay[(iYear-1901)*12+iMonth-1]
#	if iDay<15:
#		Day=15-((Flag >> 4) & 0x0f)
#	else:
#		Day=(Flag & 0x0f)+15
#	if  iDay==Day:
#		if   iDay>15:
#			Result=(iMonth-1)*2+2
#		else:
#			Result=(iMonth-1)*2+1
#	else:
#			Result=0
#	return Result
#
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
#print getGetDayOf(2009,8,6).encode('gbk')
##print l_GetLunarHolDay(2009,8,6)
#





## 使用Decorators实现计算函数的执行时间
#from time import ctime
#def time_func(func):
#	def wrappedFunc(*nkw,**kw):
#		print "*"*20,"[bfr][%s] %s() calling, nkw=%s, kw=%s" % (ctime(),func.__name__,nkw,kw), "*"*20
#		func(*nkw,**kw)
#		print "*"*20,"[aft][%s] %s() called! " % (ctime(),func.__name__),"*"*20,"\n"
#	return wrappedFunc
#
#@time_func
#def foo(test,tt,ds): # 等价于 foo=time_func(foo(test,tt,ds))
#	print "in foo(...), test=%s,tt=%s,ds=%s" % (test,tt,ds)
#
#@time_func
#def bar(): # 等价于 bar=time_func(bar())
#	print "in bar()"
#
#@time_func
#def some(var1,var2=90,var3='f'):
#	print 'in some(...), ', var1,' ',var2,' ',var3
#
#foo('haha','i','am')
#bar()
#some('test',88,'func')
#some('test')
#some('test',var3='mm')
#some(var3='heihei',var1='yeah!')
#some('test',99)
#some(var2=66,var1='come')


## 获取function或者method的名称及参数列表
#def func_name_tmp(df,dd):
#	tmp_var='hello'
#	pass
#t=func_name_tmp
#print "name=",t.func_name # function或者method的名称
#print "args=",t.func_code.co_varnames[:t.func_code.co_argcount] # 获取function或者method的参数名
#print "defaults values=",t.func_defaults # 获取可能存在的参数默认值，但不知道如何对应上是哪个参数的默认值
#class clsTest(object):
#	def __init__(self):
#		self.lll='dfdf'
#	def method_t(self,mm,nn=6):
#		vv='im vv'
#c=clsTest()
#t=c.method_t
#print "name=",t.func_name, " name=",t.func_code.co_name  # function或者method的名称
#print "args=",t.func_code.co_varnames[:t.func_code.co_argcount] # 获取function或者method的参数名
#print "defaults values=",t.func_defaults # 获取可能存在的参数默认值，但不知道如何对应上是哪个参数的默认值

## 使用pywin32的windows API，设置五秒超时的定时器对象并进行阻塞等待
#import win32event
#from time import ctime
#handle=win32event.CreateWaitableTimer(None,True,None)
#dueTime=-10000000L * 5  # set timeout 5 seconds
#rst=win32event.SetWaitableTimer(handle,dueTime,0,None,None,0)
#print "wait...", ctime()
#rst=win32event.WaitForSingleObject(handle,win32event.INFINITE)
#print "done!",ctime()


## 获取并改变cookie
#import cookielib, urllib2
#cj = cookielib.CookieJar()
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) # 构造自己的opener,使用HTTPCookieProcessor取代默认的来处理cookie
#urllib2.install_opener(opener) # 用自己的opener取代默认的
#print isinstance(opener.handle_open['http'][1],urllib2.HTTPHandler)
#opener.handle_open['http'][1].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息
#print "*"*60
#req=urllib2.Request("http://www.google.com")
#urllib2.urlopen(req)
#print "="*60
#print cj
#coo=cj._cookies_for_request(req) # 获得cookie
#for i in coo:
#	if isinstance(i,cookielib.Cookie):
#		pass
##		print dir(i)
##		print "is_expired=",i.is_expired()
##		print "name=",i.name
##		print "path=",i.path
##		print "path_specified=",i.path_specified
##		print "port=",i.port
##		print "port_specified=",i.port_specified
##		print "rfc2109=",i.rfc2109
##		print "secure=",i.secure
##		print "value=",i.value
##		print "version=",i.version
#		i.value="test=1" # 改变cookie
##print coo
#print "*"*40
#print cj
#print "="*60
#urllib2.urlopen(req)
#print "="*60
#print cj


## 解析百度mp3搜索页面(不完美)
#import cookielib, urllib2
#import mx.Tidy as mt
#from BeautifulSoup import BeautifulSoup
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
#initurl=u"http://mp3.baidu.com/m?f=ms&rn=&tn=baidump3&ct=134217728&word=%D2%BB%C8%E7%BC%C8%CD%F9&lm=-1"
#cj = cookielib.CookieJar()
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) # 构造自己的opener,使用HTTPCookieProcessor取代默认的来处理cookie
#urllib2.install_opener(opener) # 用自己的opener取代默认的
#print isinstance(opener.handle_open['http'][1],urllib2.HTTPHandler)
##opener.handle_open['http'][1].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息
#print "*"*60
## (1) 下载页面
#req=urllib2.Request(initurl)
#print cj

## (2) 以utf8写入文件. tidy不支持gb2312,so要转成utf8
#data=urllib2.urlopen(req).read()
#fin=open(r'd:\tmpin.html','wb')
#fin.write(data.decode('gb2312').encode('utf-8'))
#fin.close()

## (3) 用tidy预处理文件,以标准化html
#mt.tidy(open(r'd:\tmpin.html','r'),open(r'd:\tmpout.html','wb'),char_encoding="utf8",wrap=80,output_errors=0,uppercase_tags=1,uppercase_attributes=1,indent='auto')

## (4) 用BeautifulSoup查找
#soup=BeautifulSoup(open(r'd:\tmpout.html','r'),fromEncoding="utf8")
#
#lst_table=soup.body.find('table',attrs={'id':'Tbs'})
#cur_idx=0
#in_d=False
#s=lst_table.findAll(True) # get child tags
#for item in s:
#	# 得到行数列
#	if item.name=='td' and item.has_key('class') and item['class']=='tdn':
#		cur_idx=int(item.string)
#		continue
#	# 进入链接列
#	if item.name=='td' and item.has_key('class') and item['class']=='d':
#		in_d=True
#		continue
#	# 进入链接列的链接项
#	if item.name=='a' and in_d==True and item.has_key('href'):
#		print "%02d" % (cur_idx,)
##		print "len=",str(len(item))
#		# 拼接链接对应的名字,忽略字体信息
#		got_name=''.join([x for x in item.recursiveChildGenerator() if isinstance(x,unicode)])
#		g = item.recursiveChildGenerator()
#		print got_name.encode('gb2312')
#		print item['href']
#		print "="*20
#
#		in_d=False
#		cur_idx=0
#		print "*"*60
#
##raw_input('press ENTER to continue...')
#

## 处理html中一些奇怪的带转义符的编码
#import re
#s='&#64;&#108;&#105;&#101;&#98;&#105;&something-&#64;'
#t=re.sub(r'&#(\d+);', lambda m: unichr(int(m.group(1))), s)
#print t
#




# regular expression for multi line match
# 用正则匹配多行字符串,以AAAAA开始BBBBB结束的
#import re
#text = """AAAAA
#line 1
#line 2
#line 3
#
#line 4
#
#line 5
#BBBBB"""
#print "-"*20
#print re.search(r'AAAAA(.*?)(?:\n\n|BBBBB)', text, re.S).group(1).strip() # 不支持空行
#print "*"*20
#print re.search(r'AAAAA(.*)BBBBB', text, re.S).group(1).strip()  # 支持空行
#print "*"*20
#print re.search(r'AAAAA(.*?)(?:BBBBB)', text, re.S).group(1).strip() # 支持空行
#print "*"*20



## 处理网页上奇怪的编码
#s=r'%E5%88%98%E5%BC%BA'
#import urllib
#t=urllib.unquote(s)
#print unicode(t,'utf8').encode('gbk') # equal to print t.decode('utf8').encode('gbk')
#print s.replace('%',r'\x').decode("string_escape").decode("utf8").encode('gbk')
#name=u'刘强'
#ss=urllib.quote(name.encode('utf8'))
#print ss
#


## 通过COM枚举进程
#import win32pdh
#from win32com.server.exception import COMException
## 获取进程名称列表
#object='process'
#proc_dict={}
#instances=[]
#try:
#	junk, instances = win32pdh.EnumObjectItems(None,None,object, win32pdh.PERF_DETAIL_WIZARD)
#except:
#	raise COMException("Problem getting process list")
#for instance in instances:
#	if proc_dict.has_key(instance):
#		proc_dict[instance] = proc_dict[instance] + 1
#	else:
#		proc_dict[instance]=0
## 获取进程ID
#item='ID Process'
#proc_ids=[]
#for instance, max_instances in proc_dict.items():
#	for inum in xrange(max_instances+1):
#		try:
#			hq = win32pdh.OpenQuery() # initializes the query handle
#			path = win32pdh.MakeCounterPath( (None,object,instance, None, inum, item) )
#			counter_handle=win32pdh.AddCounter(hq, path) #convert counter path to counter handle
#			win32pdh.CollectQueryData(hq) #collects data for the counter
#			type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
#			proc_ids.append(instance+'\t'+str(val))
#			win32pdh.CloseQuery(hq)
#		except:
#			raise COMException("Problem getting process id")
## 排序打印
#proc_ids.sort()
#for i in proc_ids:
#	print i


## 通过调用API枚举进程列表,ctypes和yield的用法值得参考
#import ctypes
#import sys
#TH32CS_SNAPPROCESS = 0x00000002
## 定义pe32结构
#class PROCESSENTRY32(ctypes.Structure):
#	 _fields_ = [("dwSize", ctypes.c_ulong),
#						 ("cntUsage", ctypes.c_ulong),
#						 ("th32ProcessID", ctypes.c_ulong),
#						 ("th32DefaultHeapID", ctypes.c_ulong),
#						 ("th32ModuleID", ctypes.c_ulong),
#						 ("cntThreads", ctypes.c_ulong),
#						 ("th32ParentProcessID", ctypes.c_ulong),
#						 ("pcPriClassBase", ctypes.c_ulong),
#						 ("dwFlags", ctypes.c_ulong),
#						 ("szExeFile", ctypes.c_char * 260)]
#
## 枚举进程
#def getProcList():
#	CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
#	Process32First = ctypes.windll.kernel32.Process32First
#	Process32Next = ctypes.windll.kernel32.Process32Next
#	CloseHandle = ctypes.windll.kernel32.CloseHandle
#	hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
#	pe32 = PROCESSENTRY32()
#	pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
#	if Process32First(hProcessSnap,ctypes.byref(pe32)) == False:
#		print >> sys.stderr, "Failed getting first process."
#		return
#	while True:
#		yield pe32
#		if Process32Next(hProcessSnap,ctypes.byref(pe32)) == False:
#			break
#	CloseHandle(hProcessSnap)
#
## 通过进程ID获取其子进程
#def getChildPid(pid):
#	procList = getProcList()
#	for proc in procList:
#		if proc.th32ParentProcessID == pid:
#			yield proc.th32ProcessID
#
##	 根据进程ID杀死进程及其子进程
#def killPid(pid):
#	childList = getChildPid(pid)
#	for childPid in childList:
#		killPid(childPid)
#	handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
#	ctypes.windll.kernel32.TerminateProcess(handle,0)
#
## 使用示例,列出进程,父进程ID和进程ID
#procList = getProcList()
#for proc in procList:
#	print proc.szExeFile+'  '+str(proc.th32ParentProcessID) + '  '+str(proc.th32ProcessID)
#




## 詠
## FindFirstChangeNotification
## WaitForSingleObject
## FindNextChangeNotification
## FindCloseChangeNotification
#import os
#import time
#import win32api
#import win32event
#import signal
#def mySIGINT(signo,frame):
#	print 'got SIGINT!'
#signal.signal(signal.SIGINT,mySIGINT)
#FILE_NOTIFY_CHANGE_LAST_WRITE=0x00000010
## 监视d盘根目录的最后更新时间的变更事件
#handle=win32api.FindFirstChangeNotification('d:\\',False,FILE_NOTIFY_CHANGE_LAST_WRITE)
#print handle
#old_time=new_time=statinfo=os.stat(r'd:\togo.txt').st_mtime
#while True:
#	reslt=win32event.WaitForSingleObject(handle,win32event.INFINITE)
#	if reslt==win32event.WAIT_ABANDONED:
#		print 'abandoned'
#	elif reslt==win32event.WAIT_OBJECT_0:
#		print '2'
#		statinfo=os.stat(r'd:\togo.txt')
#		new_time=statinfo.st_mtime
#		if new_time!=old_time:
#			old_time=new_time
#			print 'mtime:',time.strftime('%Y%m%d %H:%M:%S',time.localtime(statinfo.st_mtime))
#			print 'size:',statinfo.st_size
#		else:
#			print 'unchanged!'
#		result=win32api.FindNextChangeNotification(handle)
#	elif reslt==win32event.WAIT_TIMEOUT:
#		print 'time out'
#
#win32api.FindCloseChangeNotification(handle)
#


## 排序两个相关列表
#a=['b','e','o','a','x','f']
#b=[45,64,73,44,5,33]
#x,y=map(list,zip(*sorted(zip(a,b)))) # zip用法
#print 'x=',x
#print 'y=',y

## 打印数字的二进制形式
#bin = lambda n : (n > 0) and (bin(n/2) + str(n%2)) or ''
#print bin(73)














## 度分秒(DMS)与度(DES)的换算
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
#from math import floor as floor
#from math import log as log
#from math import sin as sin
#from math import atan as atan
#from math import exp as exp
#import re
## 小数点角度转换为时分秒角度
#def des2dms(des):
#	sign=False
#	if des<0.0:
#		des=-des
#		sign=True
#	d=floor(des)
#	tmp=(des-d)*60.0
#	m=floor(tmp)
#	tmp-=m
#	s=tmp*60
#	print (u"%s%.5f ==> %s%d°%d'%.2f\""%((sign and ['-'] or [''])[0],des,(sign and ['-'] or [''])[0],d,m,s)).encode("gb2312")
#
## 时分秒角度转换为小数点角度
#def dms2des(dms):
#	idx1=dms.find(u"°")
#	d1=dms[0:idx1]
#	sign=False
#	if int(d1)<0:
#		d1=-d1
#		sign=True
##	print "d1=",d1
#	idx2=dms.find(u"'",idx1)
#	d2=dms[idx1+1:idx2]
##	print "d2=",d2
#	idx3=dms.find(u'"',idx2)
#	d3=dms[idx2+1:idx3]
##	print "d3=",d3
#	print (u"%s%s ==>%s%.5f" % ((sign and ['-'] or [''])[0],dms,(sign and ['-'] or [''])[0],int(d1)+int(d2)/60.+float(d3)/3600.)).encode("gb2312")
#
#des2dms(40.34090)
#dms2des(u"40°20'27.24\"")
#print
#des2dms(116.42410)
#dms2des(u"116°25'26.76\"")
#print
#des2dms(108.90616)
#dms2des(u"108°54'22.18\"")
#print
#dms2des(u"120°18'30\"")
#des2dms(40.574110)
#des2dms(116.675400)
#print
#des2dms(151.211)
#des2dms(-33.852)
#
## 经纬度坐标转换为四叉树坐标
## 算法参考 http://intepid.com/2005-07-17/21.50/
## 墨卡托投影参见
## http://www.math.ubc.ca/~israel/m103/mercator/mercator.html
## http://www.blogoutdoor.com/user1/8860/archives/2007/36455.html
#def LongLat2Quadtree(long,lat):
#	PI=3.14159265358979
#	digits=18 # 精度设为18 google map上的最大精度好像是21
#	x=(180.0+long)/360.0
#	print "x=",x
#	y=-lat*PI/180
#	y=sin(y)
#	y=(1+y)/(1-y)
#	y=0.5*log(y)
#	y=y*1.0/(2*PI)
#	y+=0.5
#	print "y=",y
#	quad="t"
#	lookup="qrts"
#	while digits>=0:
#		x-=floor(x)
#		y-=floor(y)
#		quad+=lookup[(x>=0.5 and [1] or [0])[0]+(y>=0.5 and [2] or [0])[0]]
#		x*=2
#		y*=2
#		digits-=1
#
#	return quad
#
#
#print LongLat2Quadtree(116.67540,40.57411) # trstrqqrqrssrrqqttqq , http://kh.google.com/kh?v=3&t=trstrqqrqrssrrqqttqq
#
## 四叉树坐标转换为一个区域的经纬度坐标
## 算法参考 http://www.blogoutdoor.com/UploadFile/2007-11/291252869520.jpg
#def Quadtree2LongLat2(quad):
#	PI=3.14159265358979
#	left=-PI
#	top=3*PI
#	right=3*PI
#	bottom=-PI
#
#	for key in quad:
#		center_x,center_y=(left+right)/2.0,(top+bottom)/2.0
#		if key=='q':
#			right=center_x
#			bottom=center_y
#		elif key=='r':
#			left=center_x
#			bottom=center_y
#		elif key=='t':
#			right=center_x
#			top=center_y
#		elif key=='s':
#			left=center_x
#			top=center_y
#		else:
#			print "invalid quartree parameter: ",key
#			break
#
#	def getLongLat(x,y):
#		rad_long=x
#		rad_lat=(atan(exp(y))-(PI/4))*2.0
#		return "(%f,%f)" % (rad_long*180.0/PI,rad_lat*180/PI)
##	print "west=%f,north=%f,east=%f,south=%f" % (left,top,right,bottom)
#	return "lefttop: %s,rightdown: %s" %(getLongLat(left,top),getLongLat(right,bottom))
#
#print Quadtree2LongLat2("trstrqqrqrssrrqqttqq")
#



















## 判断OS的版本和32/64位情况
#import platform
#print platform.architecture()


















#!/usr/bin/env python
#coding=utf-8








## ''' 构造超级组 '''
## 每个超级组中任意组的成员与其他超级组中任意组的成员都不存在交集
## 构造超级组是为了将海量用户分为相互独立的若干子集合
##    以便于分别执行互不影响的操作
#class myNode(object):
#	def __init__(self,groupid,usr):
#		self._groupid=groupid # 组号
#		self._usr=usr # 用户
#		self._supergroupid=0 # 所属超级组号 0表示未分组
#		self._linked_groups=[] # 包含相同用户的其他组的组号的集合
#	def __repr__(self):
#		return '<%d,%s,%d,%s>'%(self._groupid,self._usr,self._supergroupid,str(self._linked_groups))
#	@property
#	def groupid(self):
#		return self._groupid
#	@property
#	def usr(self):
#		return self._usr
#
#	def get_linked_groups(self):
#		return self._linked_groups
#	def set_linked_groups(self,value):
#		self._linked_groups=value
#	def del_linked_groups(self):
#		self._linked_groups=None
#	linked_groups=property(get_linked_groups,set_linked_groups,del_linked_groups)
#
#	def get_supergroupid(self):
#		return self._supergroupid
#	def set_supergroupid(self,value):
#		self._supergroupid=value
#	supergroupid=property(get_supergroupid,set_supergroupid)
#
#
#def direct_linked_groups(i):
##	print '\tinto linked_groups...(%s)'%(i.linked_groups,)
#	for g in i.linked_groups:
#		for item in grouplist:
#			if item.groupid==g:
##				print '\t\tchecking %s ...'%(item,)
#				if item.supergroupid>0 and item.supergroupid!=i.supergroupid:
#					raise Exception('error! %s %s'%(item,i))
#				else:
#					if item.supergroupid==0:
#						item.supergroupid=i.supergroupid
##						print '\t\t\t set %s'%(item,)
##					break
#	i.linked_groups=[]
#
#def indirect_linked_groups(spgrpid):
##	print '\tindirect ...\n'
#	while True:
#		isDone=True
#		for item in grouplist:
#			if item.supergroupid==spgrpid:
#				if len(item.linked_groups)==0:
#					continue
#				else:
#					direct_linked_groups(item)
#					isDone=False
#					break
#			else:
#				continue
#		if isDone==True:
#			break
#		else:
#			continue
#
#def form_supergroups():
#	supergroupnum=1
#	for i in grouplist:
#		if len(i.linked_groups)==0:
#			continue
#
#		if i.supergroupid==0:
#			i.supergroupid=supergroupnum
#			supergroupnum+=1
##			print 'set %s'%(i,)
#		else:
#			continue
#
#		direct_linked_groups(i)
#		indirect_linked_groups(i.supergroupid)
#
#	for i in grouplist:
#		if i.supergroupid==0:
#			i.supergroupid=supergroupnum
#			supergroupnum+=1
#			print 'final set %s'%(i,)
#
#	print 'grouplist=',grouplist
#	for i in xrange(1,supergroupnum):
#		print i,' ',[x for x in grouplist if x.supergroupid==i]
#
#
#import random
#a=[]
#usrs=('a','b','c','d')
#groups=(1,2,3,4,5,6,7,8,9,10)
#grouplist=[]
## generate
#for i in xrange(1,10):
#	a.append((random.choice(groups),random.choice(usrs)))
##print 'a=',a
#
## unique
#a=list(set(a))
##print 'a=',a
#
## add to grouplist
#for item in a:
#	grouplist.append(myNode(item[0],item[1]))
#print 'grouplist=',grouplist
#
##for u in usrs:
##	print u,' ',[x[0] for x in a if x[1]==u]
##print '='*80
#
## for debug
#for u in usrs:
#	print u,' ',[x.groupid for x in grouplist if x.usr==u]
#print '='*80
#
## for debug
#for x in grouplist:
#	x.linked_groups=[u.groupid for u in grouplist if u.usr==x.usr and u.groupid!=x.groupid]
#print 'grouplist=',grouplist
#print '*'*80
#
#form_supergroups()
#


















## 计算GPS NMEA data每行的校验码
## 参考文章 http://www.cnblogs.com/procoder/archive/2009/05/06/1450219.html
## GPS NMEA data有以下特点：
## * 每一条NMEA data的数据都是以dollar符号开头。
## * 从第二个字符开始的前2个字符表示发送者（talker）和接着3个字符表示数据（message）。其中上面的talker中，GP表示通用的GPS NMEA data，而PG为特定厂商的NMEA data。
## * 所有数据字段（data fields）都是使用逗号隔开(comma-delimited)。
## * 最后一个数据段接着一个星号(asterisk)。
## * 星号后面是两位数字的校正码(checksum)，checksum的计算方法是异或计算在 '$' 和 '*'之间的所有字符。
## * 最后以回车换行(<CR><LF>)结尾。
## Garmin公司的NMEA手册见 http://www8.garmin.com/manuals/425_TechnicalSpecification.pdf
#
## GPS NMEA data的范例
#GPS_NMEA_data="""$GPRMC,000006,A,3754.6240,S,14509.7720,E,010.8,313.1,010108,011.8,E*6A
#$GPGGA,201033,3754.6240,S,14509.7720,E,1,05,1.7,91.1,M,-1.1,M,,*75
#$GPGSA,A,3,,05,10,,,,21,,29,30,,,2.9,1.7,1.3*32
#$GPGSV,3,3,12,29,74,163,41,30,53,337,40,31,09,266,00,37,00,000,00*78
#$PGRME,6.3,M,11.9,M,13.5,M*25
#$PGRMB,0.0,200,,,,K,,N,W*28
#$PGRMM,WGS 84*06"""
#data= GPS_NMEA_data.split('\n')
#for s in data:
#	checksum=0
#	for i in xrange(1,len(s)-3):
#		checksum^=ord(s[i])
#	assert "%.2X" %(checksum,)==s[-2:]
#






## 访问sina获取实时股票信息
#import urllib2
#url=u"http://hq.sinajs.cn/list=sh601001"
#req=urllib2.Request(url)
#resp=urllib2.urlopen(req)
#data= resp.read()
#namelist=(u'股票名字',u'今日开盘价',u'昨日收盘价',u'当前价格',u'今日最高价',u'今日最低价',u'买一',u'卖一报价',u'成交的股票数',u'成交金额',u'买一股数',u'买一报价',u'买二',u'买二报价',u'买三',u'买三报价',u'买四',u'买四报价',u'买五',u'买五报价',u'卖一',u'卖一报价',u'卖二',u'卖二报价',u'卖三',u'卖三报价',u'卖四',u'卖四报价',u'卖五',u'卖五报价',u'日期',u'时间')
#idx_bgn=data.find('"')
#idx_end=data.rfind('"')
#
#data=data[idx_bgn+1:idx_end]
#datalist=data.split(',')
#print len(datalist)
#s_data=[]
#for idx in xrange(len(namelist)):
#	s_data.append((namelist[idx],datalist[idx]))
#for k,v in s_data:
#	print k.encode('gb2312'),v


##  通过HTTP POST方式访问WebServices获取实时股票行情信息
##  webservice:http://www.webxml.com.cn/WebServices/ChinaStockWebService.asmx?op=getStockInfoByCode
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
#content='''theStockCode=sh600565'''
#header='''POST /WebServices/ChinaStockWebService.asmx/getStockInfoByCode HTTP/1.1
#Host: www.webxml.com.cn
#Content-Type: application/x-www-form-urlencoded
#Content-Length: %d
#
#''' % (len(content),)
#print header+content
#import socket
#s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#try:
#	s.connect(("www.webxml.com.cn",80))
#except Exception,e:
#	print e
#s.send(header+content)
#return_data=s.recv(1024)
#print return_data.encode("gb2312")
#s.close()




##  通过SOAP 1.1方式访问WebServices获取实时股票行情信息
##  webservice:http://www.webxml.com.cn/WebServices/ChinaStockWebService.asmx?op=getStockInfoByCode
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
#stockcode='sh600565'
#content='''<?xml version="1.0" encoding="utf-8"?>
#<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
#  <soap:Body>
#    <getStockInfoByCode xmlns="http://WebXml.com.cn/">
#      <theStockCode>%s</theStockCode>
#    </getStockInfoByCode>
#  </soap:Body>
#</soap:Envelope>''' % (stockcode,)
#
#header='''POST /WebServices/ChinaStockWebService.asmx HTTP/1.1
#Host: www.webxml.com.cn
#Content-Type: text/xml; charset=utf-8
#Content-Length: %d
#SOAPAction: "http://WebXml.com.cn/getStockInfoByCode"
#
#''' % (len(content),)
#print header+content
#print "*"*40
#print "*"*40
#import socket
#s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#try:
#	s.connect(("www.webxml.com.cn",80))
#except Exception,e:
#	print e
#s.send(header+content)
#return_data=s.recv(1024)
#print return_data.encode("gb2312")
#s.close()





## 找出一个int型数组里面出现次数大于数组长度一半的数的下标，要求复杂度是O(N)
#def get_half_freq (vals):
#	u'''返回列表中出现次数超过列表长度一半的元素的值 如果不存在这样的值则返回None'''
#	val, count = None, 0
#	# val保存这样的值，如果没有这样的值则val中是一个无意义的值
#	# 此处的方法比较特别
#	for item in vals:
#		if item == val:
#			count += 1
#		elif 0 == count:
#			count = 1
#			val = item
#		else:
#			count -= 1
#
#	# 判断val是否是有效的值
#	vals_len= len(vals)
#	max_val_count = 0
#
#	for item in vals:
#		if item == val:
#			max_val_count += 1
#
#	if max_val_count > vals_len/2:
#		# 打印出现此值的各索引值
##		for i in xrange (0, vals_len):
##			if (vals[i] == val):
##				print i
#		return val
#	else:
##		print 'No such val found!'
#		return None
#
#print get_half_freq([10,3, 2, 3, 7,3, 3, 8, 9])
#print get_half_freq([10,3, 2, 3, 7,3, 3, 3, 8])






## 将字符串按定长分割成list
#L=map(chr,xrange(65,65+26))+map(chr,xrange(97,97+26)) # 要被分割的lsit
#LL=[L[i:i+10] for i in xrange(0,len(L),10) ] # 每10个分一组
#for i in LL: print i











## 使用传统的select方式监听网络事件的服务器
#LISTEN_ADDR=('',23456)
#BUFSIZE=1024
#import socket
#import sys
#import time
#import select
#
#client_list=[]
#rlist=[]
#wlist=[]
#xlist=[]
#sample_html=''
#
#def Listener():
#	try:
#		sServer=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#		sServer.setblocking(False)
#		sServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, sServer.getsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR ) | 1)
#		sServer.bind(LISTEN_ADDR)
#		sServer.listen(5)
#	except Exception,e:
#		print 'error creating listen socket! \n',e
#		sys.exit(1)
#
#	rlist.append(sServer)
#	xlist.append(sServer)
#
#	print 'sServer is ',sServer.fileno()
#	print 'start listening ...'
#	while True:
#		try:
#			print 'select ... ',
#			print 'rlist=[',
#			for e in rlist:
#				print ' ',e.fileno(),
#			print ']'
#			print '='*40
#			infds,outfds,errfds = select.select(rlist,wlist,xlist,None)
#
#			# have incoming data to read
#			if infds:
#				# 有新客户端连接
#				if sServer in infds:
#					sClient,clt_addr=sServer.accept()
#					print 'new client %s from %s' % (sClient.fileno(),clt_addr)
#					client_list.append(sClient)
#					rlist.append(sClient)
##					wlist.append(sClient)
#					xlist.append(sClient)
#
#				for elem in [i for i in infds if i!=sServer]:
#					try:
#						data=elem.recv(BUFSIZE)
##						if len(data.strip('　\r\n\t '))!=0:
#						print 'data from %d: ' % (elem.fileno(),)
#						print '-'*40
#						print '%s' % (data,)
#						print '-'*40
#						print
##						elem.send('[infds]server tiem: %s , hello~~~' % time.strftime('%Y%m%d %H:%M:%S'))
#						elem.send(sample_html) # 对任何请求均返回固定内容，模拟代理服务器
#
#					except socket.error,e:
#						print 'reading error! ',e
#						print 'close ',elem.fileno()
#						elem.close()
#						rlist.remove(elem)
#						if elem in wlist: wlist.remove(elem)
#						if elem in xlist: xlist.remove(elem)
#						client_list.remove(elem)
#
#			# can write
#			if len(outfds)!=0:
#				for elem in outfds:
#					print 'have data to send for ', elem.fileno()
#					elem.send('[outfds]server tiem: %s , hello~~~' % time.strftime('%Y%m%d %H:%M:%S'))
#
##				thread_write_socket(outfds)
#
#			# have errors
#			if len(errfds)!=0:
#				print 'some error occured!'
#				if sServer in errfds:
#					rlist.remove(sServer)
#					xlist.remove(sServer)
#					print 'sServer closed'
#					sServer.close()
#				for elem in errfds:
#					if elem in rlist: rlist.remove(elem)
##					if elem in wlist: wlist.remove(elem)
#					if elem in xlist: xlist.remove(elem)
#					if elem in client_list: client_list.remove(elem)
#					print 'connection to %d closed.' % (elem.fileno(),)
#					elem.close()
#
#		except KeyboardInterrupt,e:
#			print 'got keyboard interrupt!'
#			raw_input('press ENTER to continue...')
#			sys.exit(2)
#		except socket.error,e: # 不处理 由select去发现(recv时)
#			print 'soket.error ! ',e
#		except Exception,e:
#			print 'error occured while waiting for client! \n',e
#			sys.exit(1)
#
#	sServer.close()
#if __name__=='__main__':
#	import os
#	fname=ur'C:\Documents and Settings\Administrator\桌面\www.baidu.com.htm'
#	s=os.stat(fname)
#	print 'size=',s.st_size
#	sample_html=open(fname,'r').read(s.st_size)
#	Listener()
#










## 简单的 twisted 例子 Echo服务器
#def test_twisted():
##	from twisted.web.client import getPage
#	from twisted.internet import reactor
#	from twisted.internet.protocol import Protocol,Factory
#
#	class Echo(Protocol):
#		def connectionMade(self):
#			self.factory.numProtocols = self.factory.numProtocols+1
#			print 'numProtocols=',self.factory.numProtocols
#			if self.factory.numProtocols > 2:
#				self.transport.write("Too many connections, try later")
#				self.transport.loseConnection()
#
#		def connectionLost(self, reason):
#			self.factory.numProtocols = self.factory.numProtocols-1
#			print 'numProtocols=',self.factory.numProtocols
#
#		def dataReceived(self, data):
#			print data
#			self.transport.write(data)
#
#	class MyFactory(Factory):
#		protocol=Echo
#		def __init__(self):
#			self.numProtocols=0
#
#	reactor.listenTCP(23456, MyFactory())
#	reactor.run()
#if __name__=='__main__':
#	test_twisted()







## 排序版本号列表
#v=[]
#v.append(['1.0.1.4', '1.4.1','1.0.2', '1.0.21', '1.2.9','2.7.1', '1.2.11','2.3.1'])
#v.append(['2.3.1','1.0.1.2', '1.4.1','1.2.11','1.0.2', '1.0.21', '1.2.9','2.7.1'])
#v.append(['5.0', '1.4','0.2', '1.0.21', '1.2.9','2.7.1', '1.2.11','2.3.1'])
#v.append(['1.0.1', '1.0.2', '1.0.21', '1.2.9', '1.2.11'])
#v.append([ '1.0.2.11','1.0.2','1.0'])
#def mycmp(x,y):
#	a=map(int,x.split('.'))
#	b=map(int,y.split('.'))
##	print '='*30
##	print a
##	print b
#	for i in range(min(len(a),len(b))):
#		if a[i]>b[i]:
##			print '>'
#			return 1
#		elif a[i]<b[i]:
##			print '<'
#			return -1
#		else: pass
#
#	if len(a)>len(b):
#		return 1
#	elif len(a)<len(b):
#		return -1
#	else:
#		return 0
#
#for i in v:
#	m=sorted(i,mycmp)
#	print m
#
#



















## 将bt文件信息入库
#def initDjangoORM():
#	'''初始化Django的ORM模块'''
#	# 设置变量以便单独使用django的orm模块
#	from django.conf import settings
#	settings.configure(DATABASE_ENGINE="sqlite3",
#										DATABASE_HOST="localhost",
#										DATABASE_NAME="E:/Proj/python/py-prj/test_django/btCollection/sqlite3.db",
#										DATABASE_USER="",
#										DATABASE_PASSWORD="")
#	# 重要】为了能使用django的orm模块，需要创建目录btView，在里面放上空
#	#  文件__init__.py和文件models.py,这样django就会去数据库中找btView_Video,
#	#  btView_Screenshot，btView是创建的另一个ajango应用的app_name
#	# 如何单独使用ajango的orm模块见 http://wiki.woodpecker.org.cn/moin/UsingDjangoAsAnStandaloneORM
#	from btView.models import Video,Screenshot
#	globals()['Video']=Video
#	globals()['Screenshot']=Screenshot
#
#	from django.db import transaction
#	globals()['transaction']=transaction
#
#def parseDir(dpath):
#	'''解析目录 将文件信息入库'''
#	# 遍历目录
#	dir_cnt=file_cnt=0
#	print u'%s' % (dpath,)
#	for dirpath,dirnames,filenames in os.walk(dpath):
##		print "="*80
##		print u'%s, len(dirnames)=%d,len(filenames)=%d' % (dirpath,len(dirnames),len(filenames))
#		dir_cnt+=len(dirnames)
#
#		v=None # 只支持一个目录中只包含一个video文件
#		s=[]
#		for f in filenames:
#			file_cnt+=1
#			fpath=unicode(os.path.join(dirpath,f))
#			st=os.stat(fpath)
#			ftime=st.st_mtime
#			fsize=st.st_size
#
#			if os.path.splitext(f)[-1].lower() in ['.avi','.rmvb','.wmv']:
##				print 'video:'
#				v=Video(name=f,size=fsize,path=dirpath,date=datetime.datetime.fromtimestamp(st.st_mtime))
#				v.save()
#			elif os.path.splitext(f)[-1].lower() in ['.jpg','.bmp']:
##				print 'screenshot:'
#				tmp=Screenshot(name=f,size=fsize,path=dirpath,date=datetime.datetime.fromtimestamp(st.st_mtime))
#				s.append(tmp)
#			else:
#				raise '！！！！！！！！！！！！！！！！！unknown!'
#
#		if v is None:
#			if len(s)!=0:
#				print 'no video file ???'
#				for item in s:
#					item.save()
#		else:
#			v.screenshot_set=s
#
##			print u'%s%s %d %s' % \
##			(' '*len(dirpath.encode('gb18030')),f,fsize,\
##			time.strftime('%Y%m%d %H:%M:%S',time.localtime(st.st_mtime)))
#
#	print 'files %d, dirs %d' % (file_cnt,dir_cnt)
#
#def parseDiskClerk(fn):
#	'''解析diskclerk导出的csv文件 入库'''
#	fi=open(fn,'r')
#	cnt=0
#	tmp=None
#	objtree={}
#	for line in fi.readlines():
#		cnt+=1
#		if cnt<3:continue
#		lne=line.decode('gb18030').strip(u'　\r\n\t ')
#		if lne!="":
#			tmp=None
#
#			s=lne.split(',')
#			fname=s[0]
#			fpath=s[1][0:s[1].rfind(fname)]
#			fsize=s[2]
#			ftime=s[3]
#			ftime=ftime.replace(u'上午',u'AM')
#			ftime=ftime.replace(u'下午',u'PM')
#			ftime=datetime.datetime.fromtimestamp(time.mktime(time.strptime(ftime,'%Y-%m-%d %p %I:%M:%S')))
#			fext=s[4]
#			ftype=s[5]
#			fdesc=s[6] # 不使用
#			diskname=s[7]
#
#			if ftype=='file':
#				if fext.lower() in  ['avi','rmvb','wmv','mpg','rm','mkv']:
##					print 'video:'
#					tmp=Video(name=fname,size=int(fsize),path=fpath,date=ftime,disk_label=diskname)
#				elif fext.lower() in ['jpg','bmp','jpeg']:
##					print 'screenshot:'
#					tmp=Screenshot(name=fname,size=int(fsize),path=fpath,date=ftime,disk_label=diskname)
#				elif fext.lower() in ['txt','url','bak','wav','nfo']:
#					print 'file ignored: ',fname
#					continue
#				else:
#					print fname,fext
#					raise '---------------------unknown!------------------------'
#			else: # 目录
#				continue
#
#			if fpath not in objtree:
#				objtree[fpath]=[]
#			objtree[fpath].append(tmp)
#
##			print fname,", ",fpath,", ",fsize,", ",ftime.strftime('%Y%m%d %H:%M:%S'),", ",diskname
#
#	print "="*60
#	for k,v in objtree.iteritems():
#		print 'k=',k,' videofiles=',str(len(filter(lambda x:isinstance(x,Video),v)))
#		for i in v:
#			print '\t',i
#
#		cnt=len(filter(lambda x:isinstance(x,Video),v))
#		if cnt==1: # 只有一个video文件
#			filter(lambda x:isinstance(x,Video),v)[0].save() # 保存video文件
#			# screenshot文件和此video文件关联
#			filter(lambda x:isinstance(x,Video),v)[0].screenshot_set=filter(lambda x:not isinstance(x,Video),v)
#		else: # 没有video文件或者多余一个video文件，均不关联
#			for s in v:
#				s.save()
#
#
#	fi.close()
#
#def setPicPath(dpath):
#	'''将cdbox中的图片路径更新到btview_screenshot.on_disk_path中'''
#	# 获取待更新的记录列表
#	l=Screenshot.objects.filter(disk_label__isnull=False).filter(on_disk_path__isnull=True)
#	print 'record count :',len(l)
#	# 获取指定目录下的待处理目录列表
#	dirlist=filter(os.path.isdir,[dpath+"\\"+i for i in os.listdir(dpath)])
#	tosave=[]
#	for i in l:
#		print '%s \nname:%s' % ('='*60,i.name)
#		path=i.path[i.path.find(")\\")+2:] # 获取相对路径
#		fpath=filter(lambda x: x.find(i.disk_label)!=-1,dirlist)[0] # 以disk_label圏Ɲՠ
#		checkpath=fpath+"\\"+path+i.name # 构造待检查的全路径名
#		print "check disk path=",checkpath
#		if os.path.exists(checkpath):
#			x= os.stat(checkpath)
#			assert x.st_size==i.size
#			print "path ok"
#			i.on_disk_path=fpath+"\\"+path # 更新on_disk_path
#			tosave.append(i)
#		else:
#			assert 0
#			print "not found! ",checkpath
#
#	for i in tosave:
#		i.save()
#	transaction.commit()
#
#if __name__=='__main__':
#	import os
#	import time
#	import datetime
#	import sys
#	reload(sys)
#	sys.setdefaultencoding('utf8')
#	initDjangoORM()
#	parseDir(ur'j:\v\b')
##	parseDiskClerk(ur'C:\Documents and Settings\Administrator\桌面\1.csv')
#	# 为了使用事务而调用Decorator @transaction.commit_manually
##	setPicPath=transaction.commit_manually(setPicPath)
##	setPicPath(ur'D:\GreenTools\CDBox\disk')













## 根据经纬度计算两点间距离
## 经度 long  纬度 lat
#def GetDistance( lng1,  lat1,  lng2,  lat2):
#	u'''计算两点间球面距离 单位为m'''
#	EARTH_RADIUS = 6378.137 # 地球周长/2*pi 此处地球周长取40075.02km pi=3.1415929134165665
#	from math import asin,sin,cos,acos,radians, degrees,pow,sqrt, hypot,pi
#
#	# 方法0
#	# 最简单的求平面两点间距离 误差比较大
#	d=hypot(lng2-lng1,lat2-lat1)*40075.02/360*1000
#	print 'd0=',d
#
#	# 方法1
#	#  '''  d＝111.12cos{1/[sinΦAsinΦB+cosΦAcosΦBcos(λB—λA)]}    '''
#	# ''' 其中A点经度、纬度分别为λA和ΦA，B点的经度、纬度分别为λB和ΦB，d为距离。'''
#	m=cos(radians(lat1))*cos(radians(lat2))*cos(radians(lng2-lng1))
#	x=1/(sin(radians(lat1))*sin(radians(lat2)) +m)
#	d=111.12*cos(radians(1/x))
#	print 'd1=',d
#
#
#	# 方法2
#	# 据说来源于 google maps 的脚本
#	# 见 http://en.wikipedia.org/wiki/Great-circle_distance 中的 haversine
#	radLat1 = radians(lat1) # a点纬度(单位是弧度)
#	radLat2 = radians(lat2) # b点纬度(单位是弧度
#	a = radLat1 - radLat2 # 两点间的纬度弧度差
#	b = radians(lng1) - radians(lng2) # 两点间的经度弧度差
#	s = 2 * asin(sqrt(pow(sin(a/2),2) + cos(radLat1)*cos(radLat2)*pow(sin(b/2),2))) # 两点间的弧度
#	s = s * EARTH_RADIUS
##	s = round(s * 10000) / 10000 # 四舍五入保留小数点后4位
#	d=s*1000
#	print 'd2=',d
#
#	# 方法3
#	# ''' 经纬坐标为P(x1,y1) Q(x2,y2) '''
#	#	D=arccos[cosy1*cosy2*cos(x1-x2)+siny1*siny2]*2*PI*R/360
#	d=acos(cos(radians(lat1))*cos(radians(lat2))*cos(radians(lng1-lng2))+sin(radians(lat1))*sin(radians(lat2)))*EARTH_RADIUS*1000
#	print 'd3=',d
#
#	return d
#GetDistance(116.95400,39.95400,116.95300,39.95300)
















## 由网站域名查对应的ip ip可能不唯一
#import socket
#print socket.getaddrinfo("www.kaixin001.com", None)
#
#












## 全角半角转换
#def strQ2B(ustring):
#	u"""把字符串全角转半角"""
#	rstring = ""
#	for uchar in ustring:
#		inside_code=ord(uchar)
#		if inside_code==0x3000:
#			inside_code=0x0020
#		else:
#			inside_code-=0xfee0
#		if inside_code<0x0020 or inside_code>0x7e: # 转完之后不是半角字符返回原来的字符
#			rstring += uchar
#		rstring += unichr(inside_code)
#	return rstring
#
#def strB2Q(ustring):
#	u"""把字符串半角转全角"""
#	rstring = ""
#	for uchar in ustring:
#		inside_code=ord(uchar)
#		if inside_code<0x0020 or inside_code>0x7e: # 不是半角字符就返回原来的字符
#			rstring += uchar
#		if inside_code==0x0020: # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
#			inside_code=0x3000
#		else:
#			inside_code+=0xfee0
#		rstring += unichr(inside_code)
#	return rstring
#
#a = strB2Q("abc12345")
#print a.encode('gbk')
#b = strQ2B(a)
#print b.encode('gbk')

















#import re
## 200910010153 学习正则表达式
#
## 贪婪匹配与非贪婪匹配
## "正则表达式默认是贪婪匹配的，为了去掉贪婪匹配  "
## "可以用非贪婪操作符?，这个操作符可以用在*+?{}的后面 它的作用是要求正则表达式引擎匹配的字符越少越好。"
#import re
#data = 'Thu Feb 15 17:46:04 2007::uzifzf@dpyivihw.gov::1171590364-6-8'
#patt=r'.+(\d+-\d+-\d+)'  # 只能匹配 4-6-8，因为前面的.+贪婪地将117159036吃掉了
#patt=r'.+?(\d+-\d+-\d+)' # 能匹配到 1171590364-6-8
#m=re.search(patt,data)
#print 'g=',m.groups() # 所有匹配的元组
#print '0=',m.group()  # 所有匹配部分
#print '1=',m.group(1) # 匹配的元组1
#
#
## http://www.jb51.net/article/15707_3.htm
## 正则中的无捕捉组
#s=r'pathdata  forloop.counter0	as	my_curr_url  '
## ?:表示所在组是无捕获组，其匹配内容不会出现在groups中
#m = re.search(r'\s*(.*?)\s+(.*?)\s+(?:as)?\s+(\w+)?',s)
#print m.groups()
#
#
## 正则中的命名组
## 本例通过逆向引用在一个字符串中找到成双的词
#s='Paris in the the spring'
## (...)\1 这样的表达式所表示的是组号，以便于逆向引用
#m=re.search(r'(\w+)\s+\1',s)
#print m.group()
#print m.group(1)
#
## (?P<name>...)表示命名组，(?P=name)可以使叫 name 的组内容再次在当前位置发现
## 本例和上面的r'(\w+)\s+\1'作用相同，只是以命名组代替组编号
#m=re.search(r'(?P<word>\w+)\s+(?P=word)',s)
#print m.group()
#print m.group('word')
#
#
## (?<=...)
## 如果所含正则表达式...在当前位置前成功匹配则成功，否则失败。...必须是定长
## 正则中的前向肯定界定符
## (?=...)
## 如果所含正则表达式，以 ... 表示，在当前位置成功匹配时成功，否则失败。
## 但一旦所含表达式已经尝试，匹配引擎根本没有提高；模式的剩馀部分还要尝试界定符的右边。
## 正则中的后向肯定界定符
#a='ab c   12   45  6       8   xy z   1  5 67  890  ab z'
#print re.sub(r'(?<=\d)\s+(?=\d)','',a) # 本例把数字之间的空格去掉而不影响数字和字符之间的空格。

#
## 正则中的前向否定界定符
## (?!...)
## 与肯定界定符相反；当所含表达式不能在字符串当前位置匹配时成功
#s='fdfsdf.batdse' # 改为 'fdfsdf.bat' 或 fdfsdf.exe 将匹配失败
#m=re.search(r'.*[.](?!bat$|exe$).*$',s) # 将以 "bat" 或 "exe" 结尾的文件名排除在外。
#print m.group()
#
#
## 括号在正则字符串分片的应用
#s='This ...	is 	a test.'
#p1=re.compile(r'\W+')
#p2 = re.compile(r'(\W+)') # 使用捕获括号可以使定界符本身也当作列表的一部分返回
#print p1.split(s)
#print p2.split(s)
#
#
## 正则搜索替换
#s='blue socks and red shoes'
#p=re.compile( '(blue|white|red)')
#print p.sub( 'colour',s)
#print p.sub( 'colour',s, count=1) # 指定替换最多执行次数
## subn() 方法作用一样 但返回的是包含新字符串和替换执行次数的两元组。
#print p.subn( 'colour',s)
#print p.subn( 'colour','no colours at all')
#
## 空匹配只有在它们没有紧挨着前一个匹配时才会被替换掉
#p = re.compile('x*')
#print p.sub('-', 'abxd')
#
## 这个例子匹配被 "{" 和 "}" 括起来的单词 "section"，并将 "section" 替换成 "subsection"。
#p = re.compile('section{ ( [^}]* ) }', re.VERBOSE)
#print p.sub(r'subsection{\1}','section{First} section{second}')
#
## 还可以指定用 (?P<name>...) 语法定义的命名组。
## "\g<name>" 将通过组名 "name" 用子串来匹配，
## 并且 "\g<number>" 使用相应的组号。所以 "\g<2>" 等于 "\2"，
## 但可能在替换字符串里含义不清，如 "\g<2>0"。
##（"\20" 被解释成对组 20 的引用，而不是对後面跟着一个字母 "0" 的组 2 的引用。）
#p = re.compile('section{ (?P<name> [^}]* ) }', re.VERBOSE)
#s='section{First}'
#print p.sub(r'subsection{\1}',s)
#print p.sub(r'subsection{\g<1>}',s)
#print p.sub(r'subsection{\g<name>}',s)
#
#
## "替换是个函数，该函数将会被模式中每一个不重复的匹配所调用。"
## "在每个调用时，函数被作为 `MatchObject` 的匹配函属，"
## "并可以使用这个信息去计算预期的字符串并返回它。"
## "本例中，替换函数将十进制翻译成十六进制 "
#def hexrepl( match ):
#	"""Return the hex string for a decimal number"""
#	value = int( match.group() )
#	return hex(value)
#p = re.compile(r'\d+')
#print p.sub(hexrepl, 'Call 65490 for printing, 49152 for user code.')












## 尝试提取并解析USBTrace导出的m241Log data文件中的数据
#def parseUsbData(ifn,ofn):
		#p=re.compile(r'^\*\* Data \*\*\n(?P<data>[0-9A-F|\s]*)\n\n',re.M )
		#fc=open(ifn).read()
		#tmp=cStringIO.StringIO()
		## 从USBTrace导出的文件中获取数据
		#for i in re.finditer(p,fc):
				#tmp.write(i.group('data'))

		## 1) 初步解码，将十六进制的数据转换
		#s=tmp.getvalue()
		#tmp.close()
		#outs=map(lambda x:unichr(int(x,16)),s.split())

##	open(ur'd:\tmp.txt','w').write(''.join(outs))

		## 2) 提取log data
		#tmp=cStringIO.StringIO()
		#for line in ''.join(outs).split('\r\n'):
				#if line.startswith('$PMTK182,8,'):
						#ls=line.split(',')
						#rawdata=ls[3][:-3]
##			rawdata=map(lambda x:unichr(int(x,16)),rawdata)
##			print ls[3][-10:-3]
						#tmp.write(''.join(rawdata))

		## 3) 解码log data
		#s=tmp.getvalue()
		#tmp.close()
		#s=[s[i:i+2] for i in xrange(0,len(s),2) ] # 两个char一组
		#s=map(lambda x:chr(int(x,16)),s)

		## 保存解码后的文件
		#with open(ofn,'w') as f:
				#f.write(''.join(s))

#def showdate(ifn):
		#f=open(ifn,'rb')
		#s=f.read()
		#print 'size=',len(s)
		#for i in xrange(0,len(s)-15,16):
				##print i
##		if i>2000: break
				#(tmp,)=struct.unpack_from('I',s,i)

				#try:
						##d=time.strftime('%Y%m%d-%H:%M:%S',time.localtime(tmp))
						#d=time.strftime('%Y%m%d',time.localtime(tmp))
				#except Exception,e:
						#print 'exception,idx=%d,%s'%(idx,e)
				#else:
						#if d=='20091008':
								#print 'idx=%d,%s'%(i,time.strftime('%Y%m%d-%H:%M:%S',time.localtime(tmp)))


#def decodeTest(s):
		#s=[s[i:i+2] for i in xrange(0,len(s),2) ] # 两个char一组
		#s=map(lambda x:chr(int(x,16)),s)
		#(tme,lat,lon,ele,crc)=struct.unpack('Iff3sc',''.join(s))
		#ele=struct.unpack('f','0'+ele)

		## 计算校验和
		#mycrc=0
		#for i in xrange(15):
				#mycrc^=ord(s[i])
		##assert mycrc==ord(crc)

		#print '%06d) %s %.6f %.6f %.2f %.2X'% (1,
				#time.strftime('%Y%m%d-%H:%M:%S',time.localtime(tme)),
				#lat,lon,ele[0],ord(crc))


#if __name__ =='__main__':
		#import re
		#import cStringIO
		#import struct
		#import time
##	parseUsbData(ur'E:\Proj\python\py-prj\usbtrace_export.txt',ur'd:\test.trl')
		#showdate(ur'd:\test1.trl')

##	s='0627CD4A9B3520421E38E8420D0A0E43'
##	decodeTest(s)

		##with open(ur'd:\test.trl','rb') as i:
				##with open(ur'd:\test1.trl','wb') as o:
						##s=i.read()
						##o.write(s[0x03d0:0xedb5])





















## Singleton的所有子类(当然是没有重载__new__方法的子类)都只可能有一个实例.
## 如果该类的子类定义了一个__init__方法,那么它必须保证它的__init__方法
## 能够安全的对同一实例进行多次调用.
#class Singleton(object):
		#_singletons={}
		#def __new__(cls,*args,**kwds):
				#if not cls._singletons.has_key(cls): # 若还没有实例
						#cls._singletons[cls]=object.__new__(cls) # 生成一个
				#return cls._singletons[cls] # 返回这个实例

#s=Singleton()
#print 'id(s)=',id(s)
#m=Singleton()
#print 'id(m)=',id(m)

#class Child(Singleton):
		#def __init__(self,name,value=10):
				#self.name=name
				#self.value=value
		#def getId(self):
				#return self.name
#x=Child('test 1')
#print '\nid(x)=',id(x)
#y=Child('test 2')
#print 'id(y)=',id(y)
#print 'x.getId()=',x.getId()
#print 'y.getId()=',y.getId()

## 摘除自 http://wiki.woodpecker.org.cn/moin/PyNewStyleClass
## 关于新式类（继承自object的类）

## 在传统对象模型中, 方法和属性按 从左至右 深度优先 的顺序查找. 显然, 当多个父类
## 继承自同一个基类时, 这会产生我们不想要的结果. 举例来说, A 是 B 和 C 的子类,
## 而 B 和 C 继承自 D,传统对象模型的的属性查找方法是 A - B - D - C - D. 由于Python
## 先查找 D 后查找 C, 即使 C 对 D 中的方法进行了重定义, 也只能使用 D 中定义的版本.
## 由于这个继承模式固有的问题, 在实际应用中会造成一些麻烦.

## 在新的对象模型中,所有类均直接或间接生成子类对象. python改变了传统对象模型中的
## 解析顺序, 使用上面的例子, 当 D 是一个 new-style class (比如 D 是 object 的直接
## 子类), 新的对象模型的搜索顺序就变为 A - B - C - D.

## 每个内建类型及 new-style class 均内建一个特殊的只读属性 __mro__ ,
## 这是一个tuple, 保存着方法解析类型. 只允许通过类来引用 __mro__ (不允许通过实例).
#class D(object):pass
#class B(D):pass
#class C(D):pass
#class A(B,C):pass
#print '\nA.__mro__=',A.__mro__
















## 创建5×5的列表 的正确方法
#a= [[0]*5]*5 # 错误的方法!!!
#print ('a=',a)
#a[2][3]=5
#print ('a=',a) # 此时 a 中的所有子列表的地4项都被赋值了
#
#b = [[0]*5 for i in range(5)] # 正确的方法
#print ('b=',b)
#b[2][3]=5
#print ('b=',b) # 此时只有第三个子列表的第4项被赋值
#
#
#
## 看看是哪个类的类对象占用内存多
#import gc
#import sys
#from collections import defaultdict
#d = defaultdict(int)
#objects = gc.get_objects()
#print ('gc objects size: ', len(objects))
#for o in objects:
#		d[type(o)] += sys.getsizeof(o)
#
#from pprint import pprint
#pprint(d)








### 利用遗传算法解学生选导师分配问题 http://blog.stevenwang.name/ga-tss-455001.html
##
##import random
##import math
##import copy
##
##def loadData(path='d:'):
##	teachers = []
##	students = []
##	teacherPlanCount = 0;
##	studentCount = 0;
##
##	#导师及可带学生数目
##	for line in open(path + '/teacher.data'):
##		(id, count, major) = line.split(',')[0 : 3]
##		teachers.append((id, int(count), major.rstrip()))
##		teacherPlanCount += int(count)
##
##	#学生及选导师志愿情况
##	for line in open(path + '/student.data'):
##		(id, w1, w2, w3, major) = line.split(',')[0 : 5]
##		students.append((id, (w1, w2, w3), major.rstrip()))
##		studentCount += 1
##
##	return teachers, students, teacherPlanCount, studentCount
##
###输出结果
##def printsolution(vec):
##	slots = []
##	#根据每个导师可带学生数建立工位序列
##	for i in range(len(teachers)):
##		slots += [i for j in range(teachers[i][1])]
##
##	#遍历每一名学生的选择情况
##	for i in range(len(vec)):
##		x = int(vec[i])
##		#从工位序列中选择
##		teacher = teachers[slots[x]][0]
##		#输出学生及其被分配的导师
##		print ('%s %s'%(students[i][0], teacher))
##		#删除该工位
##		del slots[x]
##
###成本函数
##def teachercost(vec):
##	cost = 0
##	#建立工位序列
##	slots = []
##	for i in range(len(teachers)):
##		slots += [i for j in range(teachers[i][1])]
##
##	#遍历每一名学生
##	for i in range(len(vec)):
##		x = int(vec[i])
##		teacherName = teachers[slots[x]][0]
##		teacherMajor = teachers[slots[x]][2]
##		studentWill = students[i][1]
##		studentMajor = students[i][2]
##		#专业不符成本值为10000
##		#第一志愿成本值为0，第二志愿成本值为1
##		#第三志愿成本值为2，没选中成本为3
##		if studentMajor not in teacherMajor:
##			cost += 10000
##		elif studentWill[0] == teacherName:
##			cost += 0
##		elif studentWill[1] == teacherName:
##			cost += 1
##		elif studentWill[2] == teacherName:
##			cost += 2
##		else:
##			cost += 3
##		#删除选中的工位
##		del slots[x]
##	return cost;
##
###遗传算法
##def geneticoptimize(domain, costf, popsize = 5000, step = 1,
##					mutprob = 0.2, elite = 0.4, maxiter = 100):
##	#变异操作
##	def mutate(vec):
##		i = random.randint(0, len(domain) - 1)
##		if random.random() < 0.5 and vec[i] > domain[i][0]:
##			return vec[0 : i] + [vec[i] - step] + vec[i + 1 :]
##		elif vec[i] < domain[i][1]:
##			return vec[0 : i] + [vec[i] + step] + vec[i + 1 :]
##
##	#交叉操作
##	def crossover(r1, r2):
##		i = random.randint(1, len(domain) - 2)
##		return r1[0 : i] + r2[i : ]
##
##	#构造初始种群
##	pop = []
##	for i in range(popsize):
##		vec = [random.randint(domain[i][0], domain[i][1])
##			   for i in range(len(domain))]
##		pop.append(vec)
##
##	#每一代的胜出者数量
##	topelite = int(elite * popsize)
##
##	#主循环
##	for i in range(maxiter):
##		scores = [(costf(v), v) for v in pop]
##		scores.sort()
##		ranked = [v for (s, v) in scores]
##
##		#保留胜出者开始
##		pop = ranked[0 : topelite]
##
##		#添加变异和配对后的胜出者
##		while len(pop) < popsize:
##			if random.random() < mutprob:
##				#变异
##				c = random.randint(0, topelite)
##				v = mutate(ranked[c])
##				if v is not None:
##					pop.append(v)
##			else:
##				#交叉
##				c1 = random.randint(0, topelite)
##				c2 = random.randint(0, topelite)
##				pop.append(crossover(ranked[c1], ranked[c2]))
##		#打印当前最优值
##		print("%d : %d" % (i, scores[0][0]))
##	return scores[0][1]
##
##teachers, students, teacherPlanCount, studentCount = loadData()
##domain = [(0, teacherPlanCount - 1 - i)
##		  for i in range(studentCount)]
##s = geneticoptimize(domain, teachercost)
##printsolution(s)




### 测试 __getattr__ __getattribute__ __setattr__ __delattr__
##class A(object):
##	def __getattr__(self,name):
##		print('in __getattr__ name=%s'%(name,))
##		print('!!! no attribute %s, return -1 !!!'%(name,))
##		return -1
##	def __getattribute__(self,name):
##		print('in __getattribute__ name=%s'%(name,))
##		return object.__getattribute__(self,name)
####		raise AttributeError # 导致__getattr__被调用
##	def __setattr__(self,name,value):
##		print('in __setattr__ name=%s, value=%s'%(name,value))
##		object.__setattr__(self,name,value)
##	def __delattr__(self,name):
##		print('in __delattr__ name=%s'%(name,))
##		object.__delattr__(self,name)
##
##
##a=A()
##a.p=5
##print ('a.p=%d'%(a.p,))
##del a.p
##print ('a.p=%d'%(a.p,))













### DNS本地代理
### http://code.google.com/p/pydnsproxy/source/browse/trunk/dns.py
##from socketserver	import *
##from socket import *
##
##gl_remote_server = '208.67.222.222'
##gl_remote_port=53
##
##class LocalDNSHandler(BaseRequestHandler):
##	def setup(self):
##		self.dnsserver = (gl_remote_server, gl_remote_port)
##
##	def handle(self):
##		data, socket = self.request
##		rspdata = self._getResponse(data)
##		socket.sendto(rspdata, self.client_address)
##
##	def _getResponse(self, data):
##		"Send client's DNS request (data) to remote DNS server, and return its response."
##		sock = socket(AF_INET, SOCK_DGRAM) # socket for the remote DNS server
##		sock.connect(self.dnsserver)
##		sock.sendall(data)
##		sock.settimeout(5)
##		try:
##			rspdata = sock.recv(65535)
##		except Exception as e:
##			print ('%s ignored.'%(e,))
##			return ''
##		# "delicious food" for GFW:
##		while 1:
##			sock.settimeout(0.4)
##			try:
##				rspdata = sock.recv(65535)
##			except timeout:
##				break
##		sock.close()
##		return rspdata
##
##class LocalDNSServer(ThreadingUDPServer):
##	pass
##
##def main():
##	dnsserver = LocalDNSServer(('127.0.0.1', gl_remote_port), LocalDNSHandler)
##	dnsserver.serve_forever()
##
##if __name__ == '__main__':
##	main()













### 用 Python 的 Descriptor 特性解决一个变态的问题
### http://kanrss.com/r/3101009#http://blog.csdn.net/lanphaday/archive/2010/12/02/6051201.aspx
##class TestDescriptors(object):
##	def __init__(self):
##		self._data=None
##	def __get__(self, instance, owner):
##		print('int __get__,instance=%s, owner=%s'%(instance,owner))
##		if len(self._data)==1:
##			tmp=self._data[0]
##			class Wrapper(tmp.__class__):
##				def __iter__(obj):
##					return self._data.__iter__()
##				def next(obj):
##					return self._data.next()
##			return Wrapper(tmp)
##		return self._data
##
##	def __set__(self, instance, value):
##		print('in __set__, instance=%s, value=%s'%(instance,value))
##		if isinstance(value,list):
##			self._data=value
##		else:
##			self._data=[value]
##
##class T(object):
##	item=TestDescriptors()
##
##t=T()
##print('t=%s'%(t,))
##t.item='test'
##print(t.item)
##print('e' in t.item)
##for i in t.item:
##	print(i)
##
##print('='*20)
##t.item=['alpha','beta','gamma','delta','epsilon']
##print(t.item)
##print('gamma' in t.item)
##for i in t.item:
##	print(i)













### 测试闭包
##output = '<int %r id=%#0x val=%d>'
##w = x = y = z = 1
##
##def f1():
##	x = y = z = 2
##
##	def f2():
##		y = z = 3
##
##		def f3():
##			z = 4
##			print (output % ('w', id(w), w))
##			print (output % ('x', id(x), x))
##			print (output % ('y', id(y), y))
##			print (output % ('z', id(z), z))
##
##		clo = f3.__closure__
##		if clo:
##			print ("f3 closure vars: %s"%(','.join([str(c) for c in clo]),))
##		else:
##			print ("no f3 closure vars")
##		f3()
##
##	clo = f2.__closure__
##	if clo:
##		print ("f2 closure vars: %s"%(','.join([str(c) for c in clo]),))
##	else:
##		print ("no f2 closure vars")
##	f2()
##
##	clo = f1.__closure__
##	if clo:
##		print ("f1 closure vars: %s"%(','.join([str(c) for c in clo]),))
##	else:
##		print ("no f1 closure vars")
##
##f1()
##











### 非递归全排列算法,比我以前写的要高效得多！
##def perm(L):
##	result = [L[:1]]
##	for i in L[1:]:
##		result = [ ele[:j]+[i]+ele[j:] for ele in result for j in range(len(ele)+1) ]
####	上面的语句等于：
####	for i in L[1:]:
####		tmpL = []
####		for ele in result:
####			for j in xrange(len(ele)+1):
####				tmpL.append(ele[0:j]+[i]+ele[j:None])
####		result = tmpL
####	print result
##	print ('%d'%(len(result),))
##
##perm(list(range(9)))
##






### 演示 super的使用和子类根据__mro__顺序调用各个基类的__init__
##class base(object):
##	def __init__(self):
##		print ("base!")
##
##class child_a(base):
##	def __init__(self):
##		super(child_a, self).__init__()
##		print ("child_a!")
##
##class child_b(base):
##	def __init__(self):
##		super(child_b, self).__init__()
##		print ("child_b!")
##
##class child_c(child_b,child_a,):
##	def __init__(self):
##		super(child_c, self).__init__()
##		print ("child_c!")
##
##x=child_c()
##print (','.join([ str(x) for x in child_c.__mro__ ]))
##print (','.join([ str(x) for x in child_c.__bases__]))







### 10次射击总数为90环的可能性有多少种
##PssblCnt=0
##def computePssbl(shotCnt,scoreNow):
##	global PssblCnt
##	if shotCnt<=10:
##		if scoreNow==90: # 达到 90环
##			PssblCnt+=1
##		elif scoreNow>90 or 10*(10-shotCnt)+scoreNow<90: # 大于90环或者不可能达到90环
##			pass
##		else:
##			for i in range(11):
##				computePssbl(shotCnt+1,scoreNow+i)
##computePssbl(0,0)
##print ('PssblCnt=%d'%(PssblCnt,))












#### property另外的用法,使用property的类一定要继承自object，否则会有问题
##class TestProperty(object):
##	def __init__(self,width):
##		self._width=width
##
##	@property
##	def area(self):
##		return self._width*self._width
##
##	@property
##	def width(self):
##		return self._width
##
##	@width.setter
##	def width(self,value): self._width=value
##
##tp=TestProperty(7)
##print ('%d'%tp.width)
##print ('%d'%tp.area)
##tp.width=8
##print ('%d'%tp.width)
##print ('%d'%tp.area)











### 用4种方式实现可用于成员函数的decorator
### 通过decorator实现在调用某成员函数前检查是否登录
##
### 1) 用descriptor
##import functools
##class checklogin(object):
##	'''用 descriptor 实现'''
##	def __init__(self,func):
##		self._func=func
##
##	def __get__(self,instance,owner=None):
##		if not instance.islogin():
##			instance.login()
##		return functools.partial(self._func,instance) # 因为self._func 是 unbound,需要将它 bound 到 instance 上
##
### 2) 用callable类实现
##class checkloginwithextraarg(object):
##	'''可以在定义时接受额外参数'''
##	def __init__(self,*args,**kwargs):
##		self._func=None
##		self._args=args
##		self._kwargs=kwargs
##
##	def __call__(self,func):
##		self._func=func
##		def wrapped(obj,*args,**kwargs):
##			print('extra arg: %s,%s'%(self._args,self._kwargs))
##			if not obj.islogin():
##				obj.login()
##			return self._func(obj,*args,**kwargs)
##		return wrapped
##
### 3) 用普通decorator实现
##def checkloginmethod(func):
##	def wrappedFunc(self,*args,**kwargs):
##		if not self.islogin():
##			self.login()
##		return func(self,*args,**kwargs)
##	return wrappedFunc
##
##class X(object):
##	def __init__(self,name):
##		self._name=name
##
##	def islogin(self):
##		print('in islogin')
##		return False
##
##	def login(self):
##		print('in login(), %s'%self._name)
##
##	@staticmethod
##	def mycheck(func):
##		def wrapped(self,*args,**kwargs):
##			if not self.islogin():
##				self.login()
##			return func(self,*args,**kwargs)
##		return wrapped
##
##	@checklogin
##	def foo(self,x,y):
##		print('in foo(), %s, x=%d,y=%d'%(self._name,x,y))
##
##	def bar(self,p,q=7):
##		print('in bar(), %s, p=%d, q=%d'%(self._name,p,q))
##
##	@checkloginwithextraarg('thisi is extra arg')
####	@checkloginwithextraarg()
##	def goo(self,a,b):
##		print('in goo(), %s, a=%d, b=%d'%(self._name,a,b))
##
##	@checkloginmethod
##	def too(self,c,d):
##		print('in too(), %s, c=%d, d=%d'%(self._name,c,d))
##
##
### 4) 用静态方法实现
##X.bar=X.mycheck(X.bar)
##x=X('m')
##x.foo(1,2)
##print('-*'*20)
##x.bar(3,4)
##print('-*'*20)
##x.goo(5,6)
##print('-*'*20)
##x.too(7,8)
##
##y=X('n')
##print('-*'*20)
##y.foo(2,3)
##print('-*'*20)
##y.bar(4,5)
##print('-*'*20)
##y.goo(6,7)
##print('-*'*20)
##y.too(8,9)


















### 获取CPU(核)的数量
##import multiprocessing, os
##print('%d'%os.sysconf("SC_NPROCESSORS_CONF"))
##print('%d'%multiprocessing.cpu_count())
