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
##	# 尝试把不是粉短线的颜色都去掉
##	f=GifImagePlugin.GifImageFile(ur'd:\mozart.gif')
##	mf=PIL.Image.new('P',f.size)
##	for y in range(f.size[1]):
##		for x in range(f.size[0]):
##			if f.getpixel((x,y))==195:
##				mf.putpixel((x,y),195)
##	mf.save(ur'd:\16.gif','gif') # 啥都看不出来 查看攻略 原来所谓get this straight是说把这些粉短线都按行对齐

	f=GifImagePlugin.GifImageFile(ur'd:\mozart.gif')
	mf=PIL.Image.new('P',f.size)
	mf.putpalette(f.getpalette()) # 用原图的调色板
	for y in range(f.size[1]):
		for x in range(f.size[0]):
			if f.getpixel((x,y))==195: # 找到头一个粉色像素 以此为对准线
				for mx in range(f.size[0]):
					mf.putpixel((mx,y),f.getpixel(((mx+x)%f.size[0],y))) # 将从这个粉色像素开始的一行复制到新图片中
				break
	mf.save(ur'd:\16.gif','gif') # 图像中包含romance ==> http://www.pythonchallenge.com/pc/return/romance.html


	# 我上面的方法得几秒钟才能完成，主要是getpixel putpixel频繁调用效率很低
	# 而老外的方法相当快，主要是避免了多重循环中的单像素操作

	# 这是老外用正则的解法，很强大！速度相当快！
	# 思路是将数据转换为640为一行的数组，
	# 用正则匹配每行中的[第一个粉块前][第一个粉块][第一个粉块后]三部分，将其调
	# 整为[第一个粉块][第一个粉块后][第一个粉块前]
	# 最后再转换回去
	import Image, re
	img = Image.open(ur"d:\mozart.gif")
	imgtext = img.tostring().replace('\n','0') # 转换数据为string并将本来可能存在的'\n'先替换掉
	imgtext = '\n'.join([imgtext[i*640:(i+1)*640] for i in range(480)]) # 按640为一行成为480行
	imgtext = re.compile('^(.*?)(\xc3{5})(.*?)$',re.M).sub(r'\2\3\1', imgtext).replace('\n',"") # 将第一个5像素粉块移到开头
	img.fromstring(imgtext) # 保存回处理后的数据
	img.save(ur"d:\mozartnew.gif")

	# 另一个不错的方法
	# 按行处理，每行用PIL的专门方法重新设定偏移
	import Image,ImageChops
	im = Image.open(ur"d:\mozart.gif")
	magic = chr(195)
	for y in range(im.size[1]):
		box = 0, y, im.size[0], y+1 # box bounding row y 设定边界，就是选定一行
		row = im.crop(box) # 按边界剪切下一行
		bytes = row.tostring() # 将此行数据转换为string
		# Rotate 195 to the first column.
		i = bytes.index(magic) # 确定第一个粉色点
		row = ImageChops.offset(row, -i) # 根据第一个粉色点设定偏移，完成对齐
		im.paste(row, box)  # overwrite the original row 覆盖原来的行
	im.save(ur"d:\out.gif")  # or just "im.show()" 保存为另一个文件


# http://www.pythonchallenge.com/pc/return/romance.html
# 第17关
# eat?
# 图片名字是 http://www.pythonchallenge.com/pc/return/cookies.jpg
# 难道跟cookie有关?
# 用firebug 查看页面的cookie，有提示 info=you+should+have+followed+busynothing...
# 回到第4关的链接，nothing改为busynothing ==> http://www.pythonchallenge.com/pc/def/linkedlist.php?busynothing=12345
# 得到提示
# If you came here from level 4 - go back!
# You should follow the obvious chain...
#
# and the next busynothing is 92512
# cookie中 info=B，看来又得顺着链接提取每个页面里面的cookies的info值 拼起来
def level_17():
	busynothing='12345'
	url='http://www.pythonchallenge.com/pc/def/linkedlist.php?busynothing=%s'
	p=re.compile(r'and the next busynothing is (\d+)',re.M)
	info=''
	while True:
		res=urllib.urlopen(url%(busynothing,))
		s=res.info().getheaders('set-cookie')[0].split(';',1)[0].split('=')[1]
		print s
		info+=s
		data=res.read()
		m=p.search(data)
		if m:
			busynothing=m.group(1)
			print 'busynothing=',busynothing
		else:
			print data
			print info # 输出 BZh91AY%26SY%94%3A%E2I%00%00%21%19%80P%81%11%00%AFg%9E%A0+%00hE%3DM%B5%23%D0%D4%D1%E2%8D%06%A9%FA%26S%D4%D3%21%A1%EAi7h%9B%9A%2B%BF%60%22%C5WX%E1%ADL%80%E8V%3C%C6%A8%DBH%2632%18%A8x%01%08%21%8DS%0B%C8%AF%96KO%CA2%B0%F1%BD%1Du%A0%86%05%92s%B0%92%C4Bc%F1w%24S%85%09%09C%AE%24%90
			break

	# BZ打头的看来又需要bz2了
	info=urllib.unquote_plus(info) # 本来用unquote()，结果下面的解压就会失败。原来unquote_plus()是先将'+'替换为' '然后再调用unquote()，都是'+'惹的祸
	print bz2.decompress(info) # 输出 is it the 26th already? call his father and inform him that "the flowers are on their way". he'll understand.

	# google 得知mozart的老爸叫 Leopold
	# 回 13关的电话薄
	conn=xmlrpclib.ServerProxy("http://www.pythonchallenge.com/pc/phonebook.php")
	result=conn.phone('Leopold') # 查Mozart老爸的电话
	print result # 输出 555-VIOLIN ==> http://www.pythonchallenge.com/pc/return/violin.html
	# 提示 no! i mean yes! but ../stuff/violin.php. ==> http://www.pythonchallenge.com/pc/stuff/violin.php
	# 显示 it's me. what do you want? 图片是 Leopold的头像？
	# 把 the flowers are on their way 这句话放到cookies的info里面发过去试试
	h={}
	h['cookie']='info='+urllib.quote_plus('the flowers are on their way')
	conn=httplib.HTTPConnection('www.pythonchallenge.com')
	conn.set_debuglevel(1)
	conn.request('GET','http://www.pythonchallenge.com/pc/stuff/violin.php',headers=h)
	res=conn.getresponse()
	print res.read() #	输出网页中提示 oh well, don't you dare to forget the balloons.  ==>  http://www.pythonchallenge.com/pc/return/balloons.html

	# 看老外的解法，里面对cookie的操作很有启发
	# http://wiki.pythonchallenge.com/index.php?title=Level17:Main_Page
##	import cookielib
##	cj = cookielib.CookieJar()
##	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
##	......
##	request = urllib2.Request('http://www.pythonchallenge.com/pc/def/linkedlist.php?busynothing=12345')
##	response = opener.open(request)
	# 这一步将本次请求和响应对的所有的cookies都放到了变量cookies中
##	cookies = cj.make_cookies(response, request) # extract all cookies that this request-response pair added to the jar
##	......
##	cookie = cookies[0] # from the previous code clock 取第一个名为info的cookie
##	cookie.value = 'the flowers are on their way' # 将其值设为要发送的，不必自己转码
##	request = urllib2.Request('http://www.pythonchallenge.com/pc/stuff/violin.php')
	# 使用修改后的cookie
##	cj.set_cookie(cookie) # overwrite the current info='whatever' cookie in the jar with the "flowers" cookie
##	cj.add_cookie_header(request) # add the Cookie: header to request 将cookies放入请求头部
##	print urllib2.urlopen(request).read()


# http://www.pythonchallenge.com/pc/return/balloons.html
# 第18关
# can you tell the difference?
# 网页注释提示 <!-- it is more obvious that what you might think -->
# 很显然是亮度 brightness  ==>  http://www.pythonchallenge.com/pc/return/brightness.html
# 还是这幅画
# 网页注释提示 <!-- maybe consider deltas.gz --> ==> http://www.pythonchallenge.com/pc/return/deltas.gz
# 里面是个文件delta.txt，类似hex视图比较，左右两部分都以 89 50 4e 47 开头 42 60 82 结尾
# 大概是两个文件，图像文件？
# 完全没思路，抄老外的一个解法，主要是使用difflib.ndiff()比较两边的相似性，那是相当简介，佩服！
def level_18():
	data=gzip.GzipFile(ur'd:\deltas.gz').read() # 打开gz文件读取数据
	data=data.splitlines() # 转换为字符串列表
	left,right,png=[],[],['','','']
	for line in data:
		left.append(line[:53]) # 保存左半部份
		right.append(line[56:]) # 保存右半部分
	diff=list(difflib.ndiff(left,right)) # 关键是这句 调用ndiff比较两个字符串列表，返回的每行开头为'- '或'+ '或'  '指示本行是对左边唯一还是对右边唯一还是两边都包含

	for line in diff:
		bytes=[chr(int(byte,16)) for byte in line[2:].split()] # 转换编码
		if line[0]=='-': png[0]+=''.join(bytes) # '- ' line unique to sequence 1
		elif line[0]=='+': png[1]+=''.join(bytes) # '+ ' line unique to sequence 2
		elif line[0]==' ': png[2]+=''.join(bytes) # '  ' line common to both sequences

	for i in range(3):
		open(ur'd:\18_%d.png'%i,'wb').write(png[i]) # 18_0.png: 显示fly    18_1.png: 显示butter    18_2.png: 显示../hex/bin.html
		# ==> http://www.pythonchallenge.com/pc/hex/bin.html 用户名 butter 密码 fly (提示框指示 "pluses and minuses" 即 + -)



# http://www.pythonchallenge.com/pc/hex/bin.html
# 第19关
# please!
# 印度的地图？
# 网页注释中有封编码了的邮件，要你解码
# 边界指示 --===============1295515792==
# 是个音频文件 indian.wav 貌似base64编码过
def level_19():
##	data=urllib.urlopen('http://butter:fly@www.pythonchallenge.com/pc/hex/bin.html').read()
####	m=re.search(r'--===============1295515792==\n(.*?)--===============1295515792==',data,re.M|re.S)
##	m=re.search(r'Content-transfer-encoding: base64\n\n(.*?)\n\n--===============1295515792==',data,re.M|re.S)
##	if m:
##		s=base64.b64decode(m.group(1))
##		open(ur'd:\indian.wav','w').write(s) # 这个文件啥都听不出来 只好翻攻略

	# 下面是攻略的解法
##	data=urllib.urlopen('http://butter:fly@www.pythonchallenge.com/pc/hex/bin.html').read()
##	m=re.search(r'<!--\n(.*?)-->',data,re.M|re.S)
##	mail=email.message_from_string(m.group(1)) # email模块以前从未用到
##	for part in mail.walk():
##		if part.get_content_maintype()=='audio':
##			audio=part.get_payload(decode=1)
##			open(ur'd:\19_indian.wav','w').write(audio) # 此处解出的文件和我的一样，攻略中说能听出sorry，可我还是啥都听不出来。。。
##			# 攻略说能看出来印度地图反了，想到 'inverted India'==>'inverted endian'
##			# 也就是反转字节

	wi=wave.open(ur'd:\19_indian.wav','rb') # wave模块以前从未用到
	wo=wave.open(ur'd:\19_indian_inv.wav','wb')
	wo.setparams(wi.getparams()) # 输出文件设置成与输入文件相同的参数
	a=array.array('i') # array模块以前从未用到，'i'代表数组中的数据类型是有符号整型
	a.fromstring(wi.readframes(wi.getnframes())) # 将所有帧放入数组
	a.byteswap() # 关键是这步，两两交换字节
	wo.writeframes(a.tostring())
	wi.close(),wo.close() # 据说新文件能听到 you are an idiot ==> http://www.pythonchallenge.com/pc/hex/idiot.html
	# "Now you should apologize..."
	# ==> http://www.pythonchallenge.com/pc/hex/idiot2.html
	# 总之这关似乎有问题，音频文件听起来乱糟糟的，实在听不出来任何有意义的发音


# http://www.pythonchallenge.com/pc/hex/idiot2.html
# 第20关
# go away!
# but inspecting it carefully is allowed.
# 图片是有警告牌的铁栅栏 用firebug查看 http://www.pythonchallenge.com/pc/hex/unreal.jpg
# 的http头部可见 Content-Range	bytes 0-30202/2123456789 字样
# 让人联想断点续传中的分块下载，可见得到的图片并不完整
# 设想模拟http协议每次多取一部分
# 用HTTP协议的协议头 Range 指定不同范围提交请求以猜测数据
# 结果在以下范围得到有意义的返回：
# 30203-30236/2123456789   Why don't you respect my privacy?
# 30237-30283/2123456789  we can go on in this way for really long time.
# 30284-30294/2123456789  stop this!
# 30295-30312/2123456789  invader! invader!
# 30313-30346/2123456789  ok, invader. you are inside now.
# 后面以100为步长，半天没结果，
# 尝试从最后倒着来，找到：
# 2123456744-2123456788/2123456789 esrever ni emankcin wen ruoy si drowssap eht
# 尝试打开 http://www.pythonchallenge.com/pc/hex/invader.html
# 得到 Yes! that's you!
# 看来不对。。。。
#
# 再往前10000字节找
# beginidx=2123456743-10000
# endidx=2123456743
# step=100
# 在扫描2123456743-2123456743时得到  2123456712-2123456743/2123456789 and it is hiding at 1152983631.
#
# 根据上面的提示直接获取
# 1152983631-1153223363/2123456789 得到一个文件,内容PK打头，可能是pkzip？后缀改为zip打开，里面是加密的，用invader反转过来的redavni
# 打开readme.txt内容：
# Yes! This is really level 21 in here.
# And yes, After you solve it, you'll be in level 22!
#
# Now for the level:
#
# * We used to play this game when we were kids
# * When I had no idea what to do, I looked backwards.
#
# 这么说已经过了20关，包里的文件package.pack就是第21关的题了。
def level_20():
	class myHTTPDefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
		def http_error_default(self, req, fp, code, msg, hdrs):
			if code=='416':
				print 'haha'
				return fp
	url='http://www.pythonchallenge.com/pc/hex/unreal.jpg'
	usr,pwd='butter','fly'
##	passman=urllib2.HTTPPasswordMgrWithDefaultRealm()
	passman=urllib2.HTTPPasswordMgr() # 密码管理
	passman.add_password('pluses and minuses',url,usr,pwd)
	authhandler=urllib2.HTTPBasicAuthHandler(passman) # 基本验证handler
	cj=cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),authhandler,myHTTPDefaultErrorHandler)

	opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) chromeframe/4.0')]
	urllib2.install_opener(opener)
	opener.handle_open['http'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息
	h={}
	beginidx=1152983631#2123456743-10000#30203
	endidx=2123456743#beginidx+1000000#30347#beginidx+100
	p=re.compile('bytes \d+-(\d+)/2123456789')
	while True:
		h['Range']='bytes=%d-%d'%(beginidx,endidx)
		req=urllib2.Request(url,None,headers=h)
		# 此法可以简单模拟基本验证，不过不推荐，还是用HTTPPasswordMgr和HTTPBasicAuthHandler正规
##	base64string = base64.encodestring('%s:%s' % ('butter','fly'))[:-1]
##	req.add_header("Authorization", "Basic %s" % base64string)
		r = opener.open(req,timeout=5)
		if r:
			res=r.read()
			s=r.info().getheaders('Content-Range')[0]
			m=p.search(s)
			if m: # 代表得到有效的内容，保存
				open(r'd:\unreal.jpg','wb').write(res)
				beginidx=int(m.group(1))+1
				endidx+=10000
				raw_input('next:%d-%d>'%(beginidx,endidx)) # 得到有效内容后暂停一下
				continue
##		endidx+=1000000
		beginidx+=    100
		if beginidx>2123456744:
			print 'done.'
			break



# 没有url
# 第21关
# 上一关得到的 package.pack
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
	from PIL import GifImagePlugin
	import PIL
	import bz2
	import calendar
	import urllib
	import httplib
	import xmlrpclib
	import gzip
	import difflib
	import base64
	import email
	import wave
	import array
	level_20()