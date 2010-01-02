#!/usr/bin/env python
#coding=utf-8

# http://www.pythonchallenge.com/pc/def/0.html
# 第0关
# 计算2的38次方
def level_00():
	result=2**38 # 或者 1<<38
	print result # 274877906944 ==> http://www.pythonchallenge.com/pc/def/274877906944.html


# http://www.pythonchallenge.com/pc/def/map.html
# 第1关
# 字符串移位转换 K->M O->Q E->G，此话翻译后提示将url做转换 map->ocr
def level_01():
	s="""g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj. """
	s='map' # ==> ocr ==> http://www.pythonchallenge.com/pc/def/ocr.html
	import string
	for i in s:
		if i.isalpha():
			print chr(((ord(i)+2)<=ord('z') and [ord(i)+2] or [ord(i)-24])[0]),
		else: print i,

	# 比较好的方法,用string.maketrans()构造转换表
	s="""g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj. """
	table = string.maketrans(string.ascii_lowercase,string.ascii_lowercase[2:]+string.ascii_lowercase[:2])
	r=string.translate(s,table)
	print r



# http://www.pythonchallenge.com/pc/def/ocr.html
# 第2关
# 寻找mess里面出现次数最少的字符（好像也可以理解为出现在mess里面的字母）
def level_02():
	p=re.compile(r'<!--(.*?)-->',re.M|re.S)
	r=urllib2.urlopen('http://www.pythonchallenge.com/pc/def/ocr.html')
	if r:
		data=r.read()
		m=p.findall(data)
		for i in m:
			if len(i)<1000: continue # 跳过提示 find rare characters in the mess below:
			d={}
			s=i.replace('\n','')
			for c in s:
				d[c]=d.get(c,0)+1
			#x=list([(j,i) for i,j in d.items()])
			#x.sort()
			#print x
			avgOC = len(s) // len(d)
			print avgOC
			print ''.join([c for c in s if d[c] < avgOC]) # 输出 equality, 去 http://www.pythonchallenge.com/pc/def/equality.html
			break


# http://www.pythonchallenge.com/pc/def/equality.html
# 第3关
# 寻找两边个被正好三个大写字母包围的小写字母
#  One small letter, surrounded by EXACTLY three big bodyguards on each of its sides.
def level_03():
	r=urllib2.urlopen('http://www.pythonchallenge.com/pc/def/equality.html').read()
	pdata=re.compile(r'<!--(.*?)-->',re.M|re.S)
	m=pdata.search(r)
	if m:
		p=re.compile(r'[a-z]+[A-Z]{3}([a-z])[A-Z]{3}[a-z]+',re.M)
		result=''.join(p.findall(m.group(1)))
		print result # 输出 linkedlist, 去 http://www.pythonchallenge.com/pc/def/linkedlist.html ==》 http://www.pythonchallenge.com/pc/def/linkedlist.php

# http://www.pythonchallenge.com/pc/def/linkedlist.php
# 第4关
# 顺着链接找
# 先找到peak.html ==> http://www.pythonchallenge.com/pc/def/peak.html
def level_04():
	url='http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=33110'
	opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
	opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
	urllib2.install_opener(opener)
	p=re.compile(r'and the next nothing is (\d+)')
	while True:
		res=opener.open(urllib2.Request(url),timeout=30).read()
		m=re.search(p,res)
		if m:
			nothing=m.group(1)
			print 'nothing=',nothing
			url='http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=%s'%(nothing,)
		else:
			print res
			break


# http://www.pythonchallenge.com/pc/def/peak.html
# 第5关
# pronounce it <!-- peak hell sounds familiar ? -->
# pickle ? ==> http://www.pythonchallenge.com/pc/def/pickle.html
# yes pickle!
# 下载 http://www.pythonchallenge.com/pc/def/banner.p
# 查看里面是个list，每个列表中的元素又是一个包含若干tuple的list，所有list中第二个数字之和
#  总为95，第一个要么是空格要么是井号，猜想是由95个字符为一行的多行字符组成的图形
# 打出来一看，写着channel
# 去 http://www.pythonchallenge.com/pc/def/channel.html
def level_05():
	p=pickle.load(open(ur'd:\banner.p'))
	fo=open(ur'd:\banner.txt','w')
	for i in p:
		fo.write(''.join(map(lambda x:x[0]*x[1],i))+'\n')
	fo.close()


# http://www.pythonchallenge.com/pc/def/channel.html
# 第6关
# 图像是个拉锁 zip? 还有个donate的链接，网页comment里说这个链接跟题目无关，无视之...
# 去 http://www.pythonchallenge.com/pc/def/zip.html
# yes. find the zip.
# 猜想 http://www.pythonchallenge.com/pc/def/channel.zip
# 打开里面有910文件，readme里面写着
# welcome to my zipped list.
#
#hint1: start from 90052
#hint2: answer is inside the zip
# 类似第4关的顺着找，文件里面包含要找的下个文件的编号
# 最终提取的comment组成了字符图形HOCKEY ==》 http://www.pythonchallenge.com/pc/def/hockey.html
# 提示  it's in the air. look at the letters.
# 仔细一看 组成HOCKEY的字母是oxygen
# 去 http://www.pythonchallenge.com/pc/def/oxygen.html
def level_06():
	f=zipfile.ZipFile(ur'd:\channel.zip')
	n='90052.txt'
	p=re.compile('(\d+)')
	fo=open(ur'd:\channel.txt','w')
	while True:
		m=re.search(p,f.open(n).read())
		if m:
			n=m.group(1)+'.txt'
			fo.write(f.getinfo(n).comment) # 记录每个文件的comment，这也太难想到了，winrar里面根本看不到comment
			continue
		break
	fo.close()

# http://www.pythonchallenge.com/pc/def/oxygen.html
# 第7关
# 是个图像，中间一行灰条
# 下载 http://www.pythonchallenge.com/pc/def/oxygen.png
# 用photoshop看那个灰度条，大概7个像素宽(0-609) 9个像素高(44-52)
# 115 109 97 114 116 32 103 117 121 44 32 121
# 111 117 32 109 97 100 101 32 105 116 46 32 116 104 101 32 110 101 120
# 116 32 108 101 118 101 108 32 105 115 32 91 ... 这才数了一半，还是用PIL吧
# 将得到的灰度数转为ascii
def level_07():
	f=PngImagePlugin.PngImageFile(ur'd:\oxygen.png')
	c=[]
	for i in range(0,f.size[0],7):
		c.append(f.getpixel((i,46))[0])
	print ''.join([chr(x) for x in c]) # 输出 smart guy, you made it. the next level is [105, 110, 116, 101, 103, 114, 105, 116, 121]jld

	print ''.join([chr(x) for x in [105, 110, 116, 101, 103, 114, 105, 116, 121]]) # 输出 integrity ，去 http://www.pythonchallenge.com/pc/def/integrity.html

# http://www.pythonchallenge.com/pc/def/integrity.html
# 第8关
# 蜜蜂采花图
# Where is the missing link?
# bee? ==> http://www.pythonchallenge.com/pc/def/bee.html
# and she is BUSY. ==> http://www.pythonchallenge.com/pc/def/busy.html
# all bees sound busy too. 无头绪
# 再回去分析网页源码
# 得到
# un: 'BZh91AY&SYA\xaf\x82\r\x00\x00\x01\x01\x80\x02\xc0\x02\x00 \x00!\x9ah3M\x07<]\xc9\x14\xe1BA\x06\xbe\x084'
# pw: 'BZh91AY&SY\x94$|\x0e\x00\x00\x00\x81\x00\x03$ \x00!\x9ah3M\x13<]\xc9\x14\xe1BBP\x91\xf08'
# 看来是加密过后的用户名和密码了，联系到bee，busy，密文头两个字节为BZ，看来是bz格式 用 bz2
def level_08():
	un='BZh91AY&SYA\xaf\x82\r\x00\x00\x01\x01\x80\x02\xc0\x02\x00 \x00!\x9ah3M\x07<]\xc9\x14\xe1BA\x06\xbe\x084'
	pw='BZh91AY&SY\x94$|\x0e\x00\x00\x00\x81\x00\x03$ \x00!\x9ah3M\x13<]\xc9\x14\xe1BBP\x91\xf08'
	print bz2.decompress(un) # 输出 huge
	print bz2.decompress(pw) # 输出 file 点击图片的热点链接，输入用户名 huge和密码file，到 http://www.pythonchallenge.com/pc/return/good.html


# http://www.pythonchallenge.com/pc/return/good.html
# 第9关
# 标题是 connect th dots
# 图中一堆黑点，网页注释中first和second是一堆数字, first+second=?
# 看来要在图中画点
def level_09():
	f=[146,399,163,403,170,393,169,391,166,386,170,381,170,371,170,355,169,346,167,335,170,329,170,320,170,
310,171,301,173,290,178,289,182,287,188,286,190,286,192,291,194,296,195,305,194,307,191,312,190,316,
190,321,192,331,193,338,196,341,197,346,199,352,198,360,197,366,197,373,196,380,197,383,196,387,192,
389,191,392,190,396,189,400,194,401,201,402,208,403,213,402,216,401,219,397,219,393,216,390,215,385,
215,379,213,373,213,365,212,360,210,353,210,347,212,338,213,329,214,319,215,311,215,306,216,296,218,
290,221,283,225,282,233,284,238,287,243,290,250,291,255,294,261,293,265,291,271,291,273,289,278,287,
279,285,281,280,284,278,284,276,287,277,289,283,291,286,294,291,296,295,299,300,301,304,304,320,305,
327,306,332,307,341,306,349,303,354,301,364,301,371,297,375,292,384,291,386,302,393,324,391,333,387,
328,375,329,367,329,353,330,341,331,328,336,319,338,310,341,304,341,285,341,278,343,269,344,262,346,
259,346,251,349,259,349,264,349,273,349,280,349,288,349,295,349,298,354,293,356,286,354,279,352,268,
352,257,351,249,350,234,351,211,352,197,354,185,353,171,351,154,348,147,342,137,339,132,330,122,327,
120,314,116,304,117,293,118,284,118,281,122,275,128,265,129,257,131,244,133,239,134,228,136,221,137,
214,138,209,135,201,132,192,130,184,131,175,129,170,131,159,134,157,134,160,130,170,125,176,114,176,
102,173,103,172,108,171,111,163,115,156,116,149,117,142,116,136,115,129,115,124,115,120,115,115,117,
113,120,109,122,102,122,100,121,95,121,89,115,87,110,82,109,84,118,89,123,93,129,100,130,108,132,110,
133,110,136,107,138,105,140,95,138,86,141,79,149,77,155,81,162,90,165,97,167,99,171,109,171,107,161,
111,156,113,170,115,185,118,208,117,223,121,239,128,251,133,259,136,266,139,276,143,290,148,310,151,
332,155,348,156,353,153,366,149,379,147,394,146,399]

	s=[156,141,165,135,169,131,176,130,187,134,191,140,191,146,186,150,179,155,175,157,168,157,163,157,159,
157,158,164,159,175,159,181,157,191,154,197,153,205,153,210,152,212,147,215,146,218,143,220,132,220,
125,217,119,209,116,196,115,185,114,172,114,167,112,161,109,165,107,170,99,171,97,167,89,164,81,162,
77,155,81,148,87,140,96,138,105,141,110,136,111,126,113,129,118,117,128,114,137,115,146,114,155,115,
158,121,157,128,156,134,157,136,156,136]

	dot1=[(f[i],f[i+1]) for i in xrange(0,len(f),2)] # 两个一组
	dot2=[(s[i],s[i+1]) for i in xrange(0,len(s),2)] # 两个一组
##	print len(dot1)
##	print len(dot2)
	img=PIL.Image.new('RGB',(400,600),(255,255,255))
	for xy in dot1:
		img.putpixel(xy,(255,0,0))
	for xy in dot2:
		img.putpixel(xy,(0,0,255))
	img.save(ur'd:\out.png','png') # 画出来的是头牛，cow ？ ==> http://www.pythonchallenge.com/pc/return/cow.htmlhttp://www.pythonchallenge.com/pc/return/cow.html  提示 hmm. it's a male. 那就是公牛bull ==> http://www.pythonchallenge.com/pc/return/bull.html





# http://www.pythonchallenge.com/pc/return/bull.html
# 第10关
# what are you looking at?
# 提示 len(a[30]) = ?
# 点击图片 ==> http://www.pythonchallenge.com/pc/return/sequence.txt
# a = [1, 11, 21, 1211, 111221,
# 找规律
# shit想了半天思路就没对上，看攻略原来是这样
#  1是1个1，写作1
#  11是2个1，写作21
#  21是1个2，1个1，写作1211
#  1211是1个1，1个2，2个1，写作111221
def level_10():
	a=['1']
	p=re.compile(r'(\d)(\1{0,})')
	while len(a)<=31:
##		print a[-1:][0]
		m=p.finditer(a[-1:][0])
		x=''
		for i in m:
			x+='%d%s'%(len(i.group(2))+1,i.group(1))
##		print 'new=%s'%(x,)
		a.append(x)

	print 'result=%d'%(len(a[30]),) # 输出 5808 ==> http://www.pythonchallenge.com/pc/return/5808.html

	# 可以优化为4行
	# 与以前相比，不用保存以前的值 少一个匹配组 不用每次都判断长度
	# 还是老外的解法牛逼！
	a='1'
	for dummy in range(30):
		a=''.join([str(len(i.group(0)))+i.group(1) for i in re.finditer(r'(\d)\1*',a)]) 	# 经分析可知数字不会超过3，所以另一个可行的匹配为：	a=''.join([str(len(i))+i[0] for i in  re.findall("(1+|2+|3+)",a)])
	print len(a)


# http://www.pythonchallenge.com/pc/return/5808.html
# 第11关
# odd even
# 图片像是被选中的样子，死活看不出来有啥特别，尝试再次取黑方块值，也看不出来什么
# 最后看攻略，靠，说能看出来evil字样，去 http://www.pythonchallenge.com/pc/return/evil.html 就算过关
# firefox IE opera都试了可我咋看都看不出来！莫名其妙的一关！
# 补充：刚才看了另外一个攻略 http://blog.csdn.net/BillStone/archive/2009/09/12/4546725.aspx
# 原来是按照间隔提取值构造新图片，那些看起来的黑方块可以构造成一幅原图一半大小的图像，里面是鲜血和evil字样！
def level_11():
	f=JpegImagePlugin.JpegImageFile(ur'd:\cave.jpg')
	l=[]
	oddf=PIL.Image.new('RGB',(f.size[0]/2,f.size[1]/2))
	evenf=PIL.Image.new('RGB',(f.size[0]/2,f.size[1]/2))
##	print 'x,y=%d,%d'%(f.size[0],f.size[1])
	for y in range(f.size[1]):
		for x in range((y+1)%2,f.size[0],2):
			oddf.putpixel((x/2,y/2),f.getpixel((x,y))) # 取正常点
	for y in range(f.size[1]):
		for x in range(y%2,f.size[0],2): # 取那些网格黑方块点
			evenf.putpixel((x/2,y/2),f.getpixel((x,y)))

	oddf.save(r'd:\1.png','png') # 相当于缩小一半的原图
	evenf.save(r'd:\2.png','png') # evil字样在本图中

# http://www.pythonchallenge.com/pc/return/evil.html
# 第12关
# dealing evil
# 看来半天没头绪，原来这个图片 http://www.pythonchallenge.com/pc/return/evil1.jpg命名上是evil1.jpg
# 试着找 http://www.pythonchallenge.com/pc/return/evil2.jpg
# 提示not jpg -- .gfx ==> http://www.pythonchallenge.com/pc/return/evil2.gfx
# 试着找 http://www.pythonchallenge.com/pc/return/evil3.jpg
# 提示no more evils
# 试着找 http://www.pythonchallenge.com/pc/return/evil4.jpg
# 提示 Bert is evil! go back!
# 不得不说好变态，原来是http://www.pythonchallenge.com/pc/return/evil1.jpg暗示你要分成5堆
# 下面就吧那个gfx文件按分牌方式分成五部分分别写入5个文件
# 然后把5个文件改名为gif，得到dis pro port ional ity,最后的ity被划去，所以结果为 disproportional
# 去 http://www.pythonchallenge.com/pc/return/disproportional.html
def level_12():
	f=open(ur'd:\evil2.gfx','rb') # 注意要二进制方式打开
	data=f.read()
	for i in range(5):
		fo=open(ur'd:\%d.gfx'%(i,),'wb') # 二进制写
		fo.write(data[i::5])
		fo.close()
	f.close()




# http://www.pythonchallenge.com/pc/return/disproportional.html
# 第13关
# call him           phone that  evil
# 点击图片进入 http://www.pythonchallenge.com/pc/phonebook.php
# 遇到xml返回的出错信息
# 前面 http://www.pythonchallenge.com/pc/return/evil4.jpg 说 Bert is evil
# 所以用Bert作为关键字查询其电话号码
# 下面代码是copy自 http://lampeter123.javaeye.com/blog/401030
# 对rpc调用不熟悉，不靠攻略我是做不出来了
def level_13():
	import xmlrpclib
	conn=xmlrpclib.ServerProxy("http://www.pythonchallenge.com/pc/phonebook.php")
	result=conn.phone('Bert')
	print result # 输出 555-ITALY ==> http://www.pythonchallenge.com/pc/return/italy.html


# http://www.pythonchallenge.com/pc/return/italy.html
# 第14关
# walk round
# 网页注释里面提示： <!-- remember: 100*100 = (100+99+99+98) + (...  -->
# 蛋糕图像下面的像条形码的图片 wire.png 拖出来一看竟然是个 10000*1 的图片
# 看来处理图片了 提示100*100大概是目标大小？那个螺旋状蛋糕是啥意思？
def level_14():
	# 先吧wire.png的像素码成100*100
##	my=PIL.Image.new('RGB',(100,100))
##	f=PngImagePlugin.PngImageFile(ur'd:\wire.png')
##	for y in xrange(100):
##		for x in xrange(100):
##			my.putpixel((x,y), f.getpixel((y*100+x,0)))
##	my.save(ur'd:\14.png','png') # 得到的图片里面有红色bit字样 ==> http://www.pythonchallenge.com/pc/return/bit.html
	# 提示 you took the wrong curve.
	# curve是曲线，这么说是要像蛋糕一样把像素盘起来？
	# 提示里面 100*100 = (100+99+99+98) + (...  -->
	# 100*100 图像，从一边开始盘，100->99->99->98正好四条边盘完，再向内侧盘
	# 98->97->97->96 找到规律 x->x-1->x-1->x-2
	# 从左上角顺时针盘
	my=PIL.Image.new('RGB',(100,100))
	f=PngImagePlugin.PngImageFile(ur'd:\wire.png')
	print 'x,y=%d,%d'%(f.size[0],f.size[1])
	n=100 # 每条边长度
	x,y=0,0
	i=0
	while i<10000:
##		print 'i,n=%d,%d'%(i,n)
		# 上
		for cnt in range(n):
			my.putpixel((x+cnt,y),f.getpixel((i,0)))
			i+=1

		x+=(n-1)
		# 右
		for cnt in range(1,n):
			my.putpixel((x,y+cnt),f.getpixel((i,0)))
			i+=1

		y+=(n-2)
		# 下
		for cnt in range(1,n):
			my.putpixel((x-cnt,y),f.getpixel((i,0)))
			i+=1

		x-=(n-2)
		# 左
		for cnt  in range(1,n-1):
			my.putpixel((x,y-cnt),f.getpixel((i,0)))
			i+=1
		y-=(n-3)

		n-=2 # 调整要画的边长

	my.save(ur'd:\14.png','png') # 输出是一只花猫的图像 cat? ==> http://www.pythonchallenge.com/pc/return/cat.html
	# 获得提示 and its name is uzi. you'll hear from him later. ==> http://www.pythonchallenge.com/pc/return/uzi.html


# http://www.pythonchallenge.com/pc/return/uzi.html
# 第15关
# whom?
# 看来要猜个人名 污损的挂历，要先找出1月26日是星期一的1XX6年都有哪年
# 仔细看右下角的二月份有29天，那一年是闰年
# 网页注释中提示
# <!-- he ain't the youngest, he is the second -->
# <!-- todo: buy flowers for tomorrow -->


def level_15():
	some=[]
	for i in range(10):
		for j in range(10):
			some.append(int('1%d%d6'%(i,j))) # 所有的可能

	for i in some:
		if calendar.weekday(i,1,26)==0: # 1月26日那天是周一
			# 判断是否是闰年
			if ((i/4.0==i//4.0) and (i/100.0!=i//100.0)) or (i/400.0==i//400.0): # 能被4整除但不能被100整除，或者能被400整除
				print i # 输出 1176 1356 1576 1756 1976
				# 提示明天买花，说明1月27日是某人的诞辰or祭日？ google那天都有谁的诞辰
				# http://zh.wikipedia.org/wiki/1%E6%9C%8827%E6%97%A5
				# 所谓不是最年轻而是第二年轻大概是指不是1976而是1756
				# 最接近的1756年1月27日 奥地利作曲家莫扎特诞辰（1791年逝世）。==> http://www.pythonchallenge.com/pc/return/mozart.html
				# 开始我试 http://www.pythonchallenge.com/pc/return/Mozart.html 不行，大小写是不同的。。。



# http://www.pythonchallenge.com/pc/return/mozart.html
# 第16关
# let me get this straight
# 一幅噪声图像
def level_16():
	pass
def level_17():
	pass
def level_18():
	pass
def level_18():
	pass
def level_19():
	pass
def level_20():
	pass
def level_21():
	pass
def level_22():
	pass
def level_23():
	pass
def level_24():
	pass
def level_25():
	pass
def level_26():
	pass
def level_27():
	pass
def level_28():
	pass
def level_29():
	pass
def level_30():
	pass
def level_31():
	pass
def level_32():
	pass
def level_33():
	pass
if __name__=="__main__":
	import re
	import urllib2
	import cookielib
	import pickle
	import zipfile
	from PIL import PngImagePlugin
	from PIL import JpegImagePlugin
	import PIL
	import bz2
	import calendar
	level_16()