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
# find rare characters in the mess below:
# 寻找mess里出现的少量字母
def level_02():
	p=re.compile(r'<!--(.*?)-->',re.M|re.S)
	pchar=re.compile(r'[a-z]+')
	r=urllib2.urlopen('http://www.pythonchallenge.com/pc/def/ocr.html')
	if r:
		data=r.read()
		m=p.findall(data)
		for i in m:
			if len(i)<1000: continue # 跳过提示 find rare characters in the mess below:
			print ''.join(pchar.findall(i))
#			d={}
#			s=i.replace('\n','')
#			for c in s:
#				d[c]=d.get(c,0)+1
#			#x=list([(j,i) for i,j in d.items()])
#			#x.sort()
#			#print x
#			avgOC = len(s) // len(d)
#			print avgOC
#			print ''.join([c for c in s if d[c] < avgOC]) # 输出 equality, 去 http://www.pythonchallenge.com/pc/def/equality.html
#			break


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
		print result # 输出 linkedlist, ==> http://www.pythonchallenge.com/pc/def/linkedlist.php


# http://www.pythonchallenge.com/pc/def/linkedlist.php
# 第4关
# 提示：
#　<!-- urllib may help. DON'T TRY ALL NOTHINGS, since it will never
# end. 400 times is more than enough. -->
# 从12345开始顺着链接找
# 到了 http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=92118 后有提示：
# Yes. Divide by two and keep going.
#
# 所以继续从46059开始
# 最后到peak.html ==> http://www.pythonchallenge.com/pc/def/peak.html
def level_04():
	url='http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=12345'
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
# 打出来一看，写着channel  ==> http://www.pythonchallenge.com/pc/def/channel.html
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
# 打开里面有910个文件，readme里面写着
# welcome to my zipped list.
#
# hint1: start from 90052
# hint2: answer is inside the zip
# 类似第4关的顺着找，文件里面包含要找的下个文件的编号
# 最终提取的comment组成了字符图形HOCKEY ==> http://www.pythonchallenge.com/pc/def/hockey.html
# 提示  it's in the air. look at the letters.
# 仔细一看 组成HOCKEY的字母是oxygen ==> http://www.pythonchallenge.com/pc/def/oxygen.html
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

	print ''.join([chr(x) for x in [105, 110, 116, 101, 103, 114, 105, 116, 121]]) # 输出 integrity  ==> http://www.pythonchallenge.com/pc/def/integrity.html

# http://www.pythonchallenge.com/pc/def/integrity.html
# 第8关
# 蜜蜂采花图，点击之，提示需要用户名和密码
# Where is the missing link?
# bee? ==> http://www.pythonchallenge.com/pc/def/bee.html
# and she is BUSY. ==> http://www.pythonchallenge.com/pc/def/busy.html
# all bees sound busy too. 无头绪
# 再回去分析网页源码
# 得到
# un: 'BZh91AY&SYA\xaf\x82\r\x00\x00\x01\x01\x80\x02\xc0\x02\x00 \x00!\x9ah3M\x07<]\xc9\x14\xe1BA\x06\xbe\x084'
# pw: 'BZh91AY&SY\x94$|\x0e\x00\x00\x00\x81\x00\x03$ \x00!\x9ah3M\x13<]\xc9\x14\xe1BBP\x91\xf08'
# 看来是加密过后的用户名和密码了，联系到bee，busy，密文头两个字节为BZh，看来是bz格式 用 bz2
def level_08():
	un='BZh91AY&SYA\xaf\x82\r\x00\x00\x01\x01\x80\x02\xc0\x02\x00 \x00!\x9ah3M\x07<]\xc9\x14\xe1BA\x06\xbe\x084'
	pw='BZh91AY&SY\x94$|\x0e\x00\x00\x00\x81\x00\x03$ \x00!\x9ah3M\x13<]\xc9\x14\xe1BBP\x91\xf08'
	print bz2.decompress(un) # 输出 huge
	print bz2.decompress(pw) # 输出 file 点击图片的热点链接，输入用户名 huge和密码file  ==> http://www.pythonchallenge.com/pc/return/good.html


# http://www.pythonchallenge.com/pc/return/good.html
# 第9关
# 标题是 connect the dots
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
# shit想了半天思路就没对上，看攻略原来是这样：
#  1是1个1，写作11
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

	# 另一解法：
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
# 下面就把那个gfx文件按分牌方式分成五部分分别写入5个文件
# 然后把5个文件改名为gif，得到dis pro port ional ity,最后的ity被划去，所以结果为 disproportional
# ==> http://www.pythonchallenge.com/pc/return/disproportional.html
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
# 看来是需要处理图片了 提示100*100大概是目标大小？那个螺旋状蛋糕是啥意思？
def level_14():
	# 先把wire.png的像素码成100*100
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

	# BZh打头的看来又需要bz2了
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
# 完全没思路，抄老外的一个解法，主要是使用difflib.ndiff()比较两边的相似性，那是相当简洁，佩服！
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
# 1152983631-1153223363/2123456789 得到一个文件,内容PK打头，可能是pkzip？后缀改为zip打开，里面是加密的，用invader反转过来的 redavni
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
# 后面完全没思路了，照抄老外的解法
def level_21():
##	f=zipfile.ZipFile(r'd:\unreal.zip')
##	data=f.open(r'package.pack','r',pwd='redavni').read()
##	open(r'd:\package.pack','wb').write(data)

	# 老外的解法 出处 http://unixwars.com/2007/09/27/python-challenge-level-21-hidden-pack/
	# 思路是先用zlib解，成功则记为' '，失败的话则用bz2解，成功则记为'#'，失败的话则反转数据并复位状态，
	# 如此继续循环，直到上次状态复位后的zlib和bz2尝试都失败则退出
	# 说不清楚还是看程序吧，很诡异。
	st=open(r'd:\package.pack','rb').read()
	log=''
	log_len=len(log)
	while True:
		try: #zlib
			st=zlib.decompress(st)
			log+=' '
		except:
			try: #bzip2
				st=bz2.decompress(st)
				log+='#'
			except: #reverse
				if log_len==len(log): break # 自上次状态复位后的zlib和bz2尝试都失败，则退出
				st=st[::-1] # 反转数据
				print log[log_len:] # 打印上次状态复位后积累的状态字符。 最终输出拼为一个图形字符 显示COPPER ==>  http://www.pythonchallenge.com/pc/hex/copper.html
				log_len=len(log) # 状态复位
	open(r'd:\21_package.unpack','wb').write(st) # 这个结果文件的内容是“look at your logs” ，提示你打印中间的log信息，也就是程序中的状态字符
	print 'done.'


	# 另一个解法，直接根据特征字符选择解压方法或者反转
	data=open(r'd:\package.pack','rb').read()
	result = ""
	while True:
		if data.startswith('x\x9c'):
			data = zlib.decompress(data)
			result += ' '
		elif data.startswith('BZh'):
			data = bz2.decompress(data)
			result += '#'
		elif data.endswith('\x9cx'):
			data = data[::-1]
			result += '\n'
		else:
			print result
			break



# http://www.pythonchallenge.com/pc/hex/copper.html
# 第22关
# emulate
# 网页注释中提示 <!-- or maybe white.gif would be more bright-->
# 打开 http://www.pythonchallenge.com/pc/hex/white.gif
# 看起来是个黑图片(竟然还叫white.gif，囧)，用photoshop打开，提示：
# 这是具有动画效果的GIF。您只能查看一帧。在此文件之上存储会导致信息丢失。
#
# 多帧GIF？我咋看不出来呢。。。
# 用acdsee2.44看会导致程序失去响应。。。 用acdsee9看不出啥来
# 最后用TotalCommander里面的一个可以单独运行的插件Imagine看，发现是133帧的gif
def level_22():
	f=GifImagePlugin.GifImageFile(r'd:\white.gif')
	my=PIL.Image.new('RGB',(640,480)) # 用于画字符的图片
	draw=PIL.ImageDraw.Draw(my)
	curpoint=[0,0]
	pointlist=[tuple(curpoint)]
	frameno=1
	while True:
##		print 'frame=%d'%(frameno,)
		try:
			for y in range(98,103):#f.size[1]):
				for x in range(98,103):#f.size[0]):
					if f.getpixel((x,y))!=0:
						print '%d: %d,%d=%d'%(frameno,x,y,f.getpixel((x,y))) # 可知每帧里面都有个调色板索引为8的点，坐标范围在(98,98)-(102,102)之间且坐标为偶数，相当于在3×3的九宫格中
						k='%d-%d'%(x,y)
						# 到此为止没有思路了。参考攻略，原来是网页上那个游戏摇杆的图片是暗示你九宫格的点是用矢量方法记录的，可以据此划出线条来，太有想象力了！
						#(98,98) (100,98) (102,98)      (-1,-1) (0,-1) (1,-1)
						#(98,100)(100,100)(102,100) ==  (-1,0)  (0,0)  (1,0)
						#(98,102)(100,102)(102,102)     (-1,1)  (0,1)  (1,1)
						d={ '98-98':(-5,-5),'100-98':(0,-5),'102-98':(5,-5),
								'98-100':(-5,0),'100-100':(0,0),'102-100':(5,0),
						    '98-102':(-5,5),'100-102':(0,5),'102-102':(5,5)}
						if d[k]==(0,0):
							print u'回到原点,开始画新字符'
							if len(pointlist)>1:
								draw.line(pointlist) # 画出字符
								del pointlist[:] # 清空列表
								curpoint[0]+=50 # 设定开始画字符的坐标，以免把上一个字符覆盖
								curpoint[1]+=50
								pointlist.append(tuple(curpoint))
							continue
						curpoint[0]+=d[k][0]
						curpoint[1]+=d[k][1]
						pointlist.append(tuple(curpoint))

			f.seek(f.tell()+1) # 跳到下一帧
			frameno+=1

		except EOFError,e: # 最后一帧后会触发此异常
			print 'end of frame.%d'%(frameno,) # 可知此GIF有133帧
			draw.line(pointlist) # 画出最后一个字符
			my.save(ur'd:\22_point.png','png') # 能看出画的字符为 bonus  ==>  http://www.pythonchallenge.com/pc/hex/bonus.html
			break


# http://www.pythonchallenge.com/pc/hex/bonus.html
# 第23关
# what is this module?
# 网页注释中提示
# <!--
# TODO: do you owe someone an apology? now it is a good time to
# tell him that you are sorry. Please show good manners although
# it has nothing to do with this level.
# -->
#
# <!-- 	it can't find it. this is an undocumented module. -->
#
# <!--
# 'va gur snpr bs jung?'
# -->
# 这句话看起来需要移位转换一下
def level_23():
	# 回到第一关的字符串移位转换
	s='va gur snpr bs jung?'
	for i in range(1,27):
		print i
		table = string.maketrans(string.ascii_lowercase,string.ascii_lowercase[i:]+string.ascii_lowercase[:i])
		r=string.translate(s,table)
		print r # i=13 时有意义 in the face of what?
		# PS: 这种用26个字母中的第1个字母替换为第14个，第2个替换为第15个以此类推，
		# 就是前一半字母和后一半字母交换的加密文本的方法有个专有术语叫 ROT13
		#
		# 至此又无思路，看攻略，我靠，原来真有个module就叫"this"
		# import this 得到如下输出
		# The Zen of Python, by Tim Peters
		#
		# Beautiful is better than ugly.
		# Explicit is better than implicit.
		# Simple is better than complex.
		# Complex is better than complicated.
		# Flat is better than nested.
		# Sparse is better than dense.
		# Readability counts.
		# Special cases aren't special enough to break the rules.
		# Although practicality beats purity.
		# Errors should never pass silently.
		# Unless explicitly silenced.
		# In the face of ambiguity, refuse the temptation to guess.
		# There should be one-- and preferably only one --obvious way to do it.
		# Although that way may not be obvious at first unless you're Dutch.
		# Now is better than never.
		# Although never is often better than *right* now.
		# If the implementation is hard to explain, it's a bad idea.
		# If the implementation is easy to explain, it may be a good idea.
		# Namespaces are one honking great idea -- let's do more of those!
		#
		# 所以 in the face of what? 的答案就是 ambiguity  ==>  http://www.pythonchallenge.com/pc/hex/ambiguity.html
		# 不得不说，这个谜题太牛逼了！
		# this.py 这个模块主要就是以ROT13形式加密保存了上面这些python的zen，在import此模块时解密打印出来





# http://www.pythonchallenge.com/pc/hex/ambiguity.html
# 第24关
# from top to bottom
# 好复杂的一张maze图呀
# 开始试着以白色为道路非白色为墙壁，用以前写过的A*算法找路径，结果没有路。
# 又仔细放大图片查看边缘，原来右上角和左下角各有一个黑色像素
# 这么说就是就是以白色为墙壁非白色为道路了，再次找路，找到。
# 又没有头绪了，开始猜想也许通路能组成图形字符，结果啥也看不出来。
# 参考攻略，原来是依次将路径间隔着取所在的像素的r值，存入文件中。
# 存成的文件是个zip，打开，里面有两个文件maze.jpg和mybroken.zip，其中maze.jpg
# 打开是个图片，上面有lake字样  ==>  http://www.pythonchallenge.com/pc/hex/lake.html
# 而mybroken.zip打开里面有个mybroken.gif，不过无法打开，似乎没有用。
def level_24():
	class Node:
		def __init__(self,parent,x,y,h):
			self.parent=parent
			self.x,self.y=x,y
			self.hv = (x << 16) ^ y
			self.g,self.h=0,h
		def __repr__(self):
			return '(%d,%d)'%(self.x,self.y)
		def __eq__(self,other):
			return self.hv == other
		def __hash__(self):
			return self.hv

	class AStarTest:
		def __init__(self,map_max_x,map_max_y,map):
			self.openlist,self.closedlist=[],set()
			self.mapMaxX,self.mapMaxY=map_max_x,map_max_y
			print '%d %d'%(self.mapMaxX,self.mapMaxY)
			self.map=map
		def inCloseList(self,x,y):
			u"""检查(x,y)是否在closedlist中"""
			return (x << 16) ^ y in self.closedlist
		def inOpenList(self,x,y):
			u"""检查(x,y)是否在openlist中"""
			for i,n in enumerate(self.openlist):
				if n.x==x and n.y==y:
					return i
			return -1
		def showPath(self,l,showmark):
			u"""显示路径"""
			tm=[] # 用来保存从起点到终点的路径坐标列表
			for i in l:
				tm.append((i.x,i.y))
			if showmark: # 在新图中显示出路径来
				f=PngImagePlugin.PngImageFile(r'd:\maze.png')
				my=f.copy()
				draw=ImageDraw.Draw(my)
				draw.point(tm,showmark)# (0,0,255,255))
				my.save(r'd:\maze_showpath.png','png')

			# 将路径间隔着取像素的r值保存到zip文件中
			f=PngImagePlugin.PngImageFile(r'd:\maze.png')
			fo=open(r'd:\maze.zip','wb')
			data=[]
			for i in tm[1::2]: # 从第二个像素开始间隔着取
				r,dummy,dummy,dummy=f.getpixel(i)
				data.append(r)
			fo.write(''.join([chr(item) for item in data]))
			fo.close()

		def SubNode(self,node,to_x,to_y):
			u""" 返回节点node的有效子节点"""
			subList=[
				                  (node.x,node.y-1),                      \
				(node.x-1,node.y),                    (node.x+1,node.y),\
				                  (node.x,node.y+1),                   ]
			for x,y in subList:
				if self.map[y][x] !='#': # 坐标值有效
					if not self.inCloseList(x,y): # 不在closedlist中
						item= Node(node,x,y,sqrt((x-to_x)*(x-to_x)+(y-to_y)*(y-to_y))*1.2)
						item.g=item.parent.g+1.0
						yield item

		def getPath(self,from_x,from_y,to_x,to_y,show_mark=None):
			u"""获取两点间的路径
			from_coord 起点
			to_coord 终点
			show_mark 用来显示路径的颜色
			"""
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
							l.reverse()
							self.showPath(l,show_mark)
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

	# 准备地图数据
	f=PngImagePlugin.PngImageFile(ur'd:\maze.png')
	# 将maze转为数组形式存入m
	m,line=[],[]
	for y in range(f.size[1]):
		for x in range(f.size[0]):
			if f.getpixel((x,y))==(255,255,255,255):
				line.append('#') # 白色为墙壁
			else:
				line.append('.') # 其他为通路
		m.append(''.join(line))
		del line[:]

	# 调用A*算法找路
	t=AStarTest(len(m[0]),len(m),m)
	t.getPath(639,0,1,640,(0,0,255,255))






# http://www.pythonchallenge.com/pc/hex/lake.html
# 第25关
# imagine how they sound
# 一个类似puzzle拼图的图片
# 网页注释提示 <!-- can you see the waves? -->
# 脑子转不过来了，看攻略才知道是让你下 http://www.pythonchallenge.com/pc/hex/lake1.wav
# 一直下到5，还有
# 编程实现吧
def level_25():
	# 将25个wave下载
	def part1():
		class myHTTPDefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
			def http_error_default(self, req, fp, code, msg, hdrs):
				if code==404: # 只处理404错误
					return fp
				raise HTTPError(req.get_full_url(), code, msg, hdrs, fp)
		url='http://www.pythonchallenge.com/pc/hex/lake%d.wav'
		baseurl='http://www.pythonchallenge.com/pc/'
		usr,pwd='butter','fly'
		passman=urllib2.HTTPPasswordMgr() # 密码管理
		passman.add_password('pluses and minuses',baseurl,usr,pwd) # uri 参数不能是变量
		authhandler=urllib2.HTTPBasicAuthHandler(passman) # 基本验证handler
		cj=cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),authhandler,myHTTPDefaultErrorHandler)

		opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) chromeframe/4.0')]
		urllib2.install_opener(opener)
	##	opener.handle_open['http'][0].set_http_debuglevel(1) # 设置debug以打印出发送和返回的头部信息
		h={}
		beginidx=1
		while True:
			req=urllib2.Request(url%(beginidx,),None,headers=h)
			r = opener.open(req,timeout=10)
	##		print '%d=%d'%(beginidx,r.code)
			if r and r.code!=404:
				res=r.read()
				open(r'd:\25_lake%d.wav'%(beginidx,),'wb').write(res)
				beginidx+=1
			else:
				print 'done.%d'%(beginidx,) # 可以看到共有25个wave文件，正好和关数一样，也和图片上puzzle拼图的分块数目相同。
				break

	# 至此思路枯竭 找攻略吧。。。
	# 找到一个比较强的攻略：http://garethrees.org/2007/05/07/python-challenge/#level-19
	# 里面说由于用wave editor看波形啥都看不出来,猜想那些不是wave文件
	# 假设是图像文件,由于wave.getnframes()=10800,考虑3字节为1像素,所以有3600像素,
	# 可能是60*60的小图片
	f=wave.open(ur'd:\25_lake1.wav')
	print f.getnframes()
	img=Image.new('RGB',(60,)*2)
	img.fromstring(f.readframes(f.getnframes()))
	img.show() # 能显示，似乎是一张图片的一部分，所以下面尝试将25张图片按5*5方式拼起来

	imgs=[]
	for i in range(1,26): # 将25个wave文件转成25个Image放入imgs
		tmpw=wave.open(ur'd:\25_lake%d.wav'%(i,))
		tmpi=Image.new('RGB',(60,)*2)
		tmpi.fromstring(tmpw.readframes(tmpw.getnframes()))
		imgs.append(tmpi)
	img=Image.new('RGB',(300,)*2)
	for i in range(len(imgs)):
		img.paste(imgs[i],( 60*(i%5),60*(i//5))) # 依次将25个image存到一个300×300的大imge中
##	img.show()
	img.save(ur'd:\26_lake.png','png') # 图片显示 decent  ==>  http://www.pythonchallenge.com/pc/hex/decent.html

##	# 下面是老外的解法，更简洁
##	# 四行完成下载保存wave文件
##	template = "http://butter:fly@www.pythonchallenge.com/pc/hex/lake%i.wav"
##	fname=r'd:\25_lake%d.wav'
##	for i in range(1, 26):
##		urllib.urlretrieve(template % i,fname%i)
##	# 完成拼接
##	l=[]
##	for i in range(1,26):
##		f=wave.open(ur'd:\25_lake%d.wav'%i,'rb')
##		l.append(f.readframes(f.getnframes()))
##		f.close()
##	im=Image.new('RGB',(300,300))
##	for i in range(25):
##		im.paste(Image.fromstring('RGB',(60,60),l[i]),( 60*(i%5),60*(i//5)))
##	im.show()





# http://www.pythonchallenge.com/pc/hex/decent.html
# 第26关
# be a man - apologize!
# 图中是抓耳挠腮的猴子，下面有句话 Hurry up, I'm missing the boat
# 网页注释中有 <!-- you've got his e-mail -->
# 联想到前面第19关解一个邮件里面的音频文件，当时没有记那个email地址
# 回去找，是 leopold.moz@pythonchallenge.com
# 发封邮件到这个地址，既然要道歉，就说sorry吧
# 得到如下输出
# 发件人	Leopold Mozart <leopold.moz@pythonchallenge.com>
# 发送至	keep.studying.everyday@gmail.com
# 日期	2010年1月5日 下午11:58
# 主题	Re: my broken zip Re: sorry
# 邮送域	mail-yw0-f121.google.com
#
# Never mind that.
#
# Have you found my broken zip?
#
# md5: bbb8b499a0eef99b52c7f13f4e78c24b
#
# Can you believe what one mistake can lead to?
#
# 这让我想到第24关的那个mybroken.zip
# 看来要想办法根据md5修复这个zip文件
# 用winrar修复失败
# 又没有思路了。。。
# 看攻略的解法：
# 信中的最后一句意思是你能相信错了一个字节就会出现这个吗？暗示你那个zip文件有一个字节错了。
# 所以修复方法是，枚举每个字节的所有可能值，然后算md5，直到与已知的正确md5值相同为止。
# 从修复好的zip文件里打开gif文件，里面显示 speed  ==> http://www.pythonchallenge.com/pc/hex/speed.html
# 地址不对
# 猜吧，发现正确的是speedboat ==> http://www.pythonchallenge.com/pc/hex/speedboat.html
def level_26():
	data=open(ur'd:\mybroken.zip','rb').read()
	for i in range(len(data)):
		for c in range(256):
			newdata=data[:i]+chr(c)+data[i+1:]
			if hashlib.md5(newdata).hexdigest()=='bbb8b499a0eef99b52c7f13f4e78c24b':
				open(ur'd:\mybroken_repaired.zip','wb').write(newdata) # 修复好的文件打开里面的mybroken.gif, 图中显示 speed
				print 'repaired.'
				return



# http://www.pythonchallenge.com/pc/hex/speedboat.html
# 第27关
# between the tables
# 图中是一只浆，和之字形的线条
# 网页注释中 图片zigzag.jpg旁边有  <!-- did you say gif? -->
# <!-- oh, and this is NOT a repeat of 14 -->
#
# 下载 http://www.pythonchallenge.com/pc/hex/zigzag.gif
# 又是一张杂乱无章的灰度图
# 点击船桨图片进入 http://www.pythonchallenge.com/pc/ring/bell.html 要新的用户名和密码
# 看来这关的目标就是要找到用户名密码
# 既然提示不是第14关的重复，就不是螺旋重组图片，那么是什么呢？
# 又没思路了，下面是参考攻略完成的
def level_27():
	zig=GifImagePlugin.GifImageFile(ur'd:\zigzag.gif')
	zigdata=zig.tostring()
	print ''.join(['%X'%(ord(i),) for i in zigdata[:10]]) # 查看前面几个字节，没有头绪

	print len(zig.getcolors())
	palette=zig.palette.getdata()[1][::3] # 获取其调色板
	print ''.join(['%X'%(ord(i),) for i in palette[:10]])

	t=string.maketrans(''.join([chr(i) for i in range(256)]),palette)
	zigtrans=zigdata.translate(t) # 用调色板值转换像素值
	print ''.join(['%X'%(ord(i),) for i in zigtrans[:10]]) # 还是看不出来什么，不过似乎转换后的数据除了第一个字节外都与原数据很相似

	print zigdata[1:]==zigtrans[:-1]
	# 尝试将两组数据中所有不相同的字节放在一起
	deltas=filter(lambda p:p[0]!=p[1],zip(zigdata[1:],zigtrans[:-1]))
	diffs=[''.join([p[i] for p in deltas]) for i in range(2)]
	print diffs[0][:20] # 看起来是个bz文件
	print diffs[1][:20]

##	bz=bz2.BZ2Decompressor().decompress(diffs[0])
	bz=bz2.decompress(diffs[0])
	print len(bz)
	print bz[:100] # 输出是python的关键字和地址 ../ring/bell.html

	keywords=bz.split(' ')
	keys={}
	for k in keywords: keys[k]=1
	print keys.keys()

	print len(keywords)
	print len(keys.keys()) # 很多关键字
	print len(keywords)/len(keys.keys())

	# 将不一样的像素按位置显示出来
	im=Image.new('1',zig.size,0)
	im.putdata([ p[0]==p[1] for p in zip(zigdata[1:],zigtrans[:-1])])
	im.show() # 有个钥匙图样，左边是not，右边是word，下面是busy?
	# 暗示 not key word
	# 那么找找上面看到的那些关键字里面哪些不是key word

	for k in keys.keys():
		if not keyword.iskeyword(k):
			print k # 打印出来 switch 和 repeat 不是关键字，../ring/bell.html不算。

	# 用switch 和 repeat 分别做用户名和密码
	k1,k2='switch','repeat'
	t=((k1,k2),(k2,k1))
	auth_handler=urllib2.HTTPBasicAuthHandler()
	opener=urllib2.build_opener(auth_handler)
	for i in t:
		try:
			auth_handler.add_password('the order matters','www.pythonchallenge.com',i[0],i[1])
			r=opener.open('http://www.pythonchallenge.com/pc/ring/bell.html')
			if r:
				print 'got, %s,%s'%(i[0],i[1]) # 正确的用户名是repeat 密码是 switch  ==> http://www.pythonchallenge.com/pc/ring/bell.html
				break
		except urllib2.HTTPError:
			pass




# http://www.pythonchallenge.com/pc/ring/bell.html
# 第28关
# 图片是瀑布，湖，丛林，图片上面似乎覆盖着很多长短不一的竖条
# many pairs ring-ring
# 提示 RING-RING-RING say it out loud
# 再次失去思路
# 一个攻略说，传说中ring-ring-ring 反复读会变成green
# 另一个则说，会变成grin
# 先看grin  ==> http://www.pythonchallenge.com/pc/ring/grin.html
# 网页上提示 you are not happy - you are feeling sick.
# 再看green ==> http://www.pythonchallenge.com/pc/ring/green.html
# 网页上提示 yes! green!
# 解码图片上短竖条中的g值
def level_28():
	im=PngImagePlugin.PngImageFile(ur'd:\bell.png')
	l=[]
	for y in range(im.size[1]):
		for x in range(im.size[0]):
			l.append(im.getpixel((x,y))[1])
	print l[:10]
	paris=[(l[i],l[i+1]) for i in range(0,len(l),2)] # 根据"my paris" 将像素两两分为一组
	# 可以看出基本上每个paris内两像素之差都为42
	print paris[:10]

	diffs=[abs(i[0]-i[1]) for i in paris] # 计算两两像素之差的绝对值
	print diffs[:10]

	d=[x for x in diffs if x!=42] # 过滤掉差值等于42的
	print d

	s=''.join([chr(x) for x in d])  # 剩下的差值转为字符
	print s # 输出 whodunnit().split()[0] ?

	# 到此就有些让我奇怪了，whodunnit是到结尾才知道谋杀犯的侦探小说的意思，怎么会联想到Python发明人Guido Van Rossum ？
	# 难道是发音像 who done it 谁做了这些
	print 'Guido Van Rossum'.split()[0] # 输出 guido  ==> http://www.pythonchallenge.com/pc/ring/guido.html

	# 从官方wiki看到获取所有像素的g值的更好方法是
##	im=Image.open(ur'd:\bell.png')
##	green=im.split()[1]
##	greendata=green.getdata()



# http://www.pythonchallenge.com/pc/ring/guido.html
# 第29关
# silence!
# 发现网页源码后面后很多行长短不一的空格行
# 用每行空格的数量组成列表
# 转成字符串，是BZh打头
# 用bz2解压字符串，得到 yankeedoodle
def level_29():
	auth=urllib2.HTTPBasicAuthHandler()
	auth.add_password('the order matters','www.pythonchallenge.com','repeat','switch')
	openr=urllib2.build_opener(auth)
	r=openr.open('http://www.pythonchallenge.com/pc/ring/guido.html')
	data=r.read().split('\n') # 读取网页内容
	print len(data)
	sdata=[x for x in data if x.strip()==u''] # 过滤掉非空格行
	print len(sdata)
	s=''.join([chr(len(x)) for x in sdata]) # 把每行空格数转成字符
	print s # 看到是BZh打头的
	rslt=bz2.decompress(s) # 用bz2解压之
	print rslt # 输出 Isn't it clear? I am yankeedoodle!  ==>  http://www.pythonchallenge.com/pc/ring/yankeedoodle.html




# http://www.pythonchallenge.com/pc/ring/yankeedoodle.html
# 第30关
# relax you are on 30
# 网页注释提示 <!-- while you look at the csv file -->
# 下载 http://www.pythonchallenge.com/pc/ring/yankeedoodle.csv
# 打开一看是逗号分割的，每行七个小于1的浮点数，总共有900多行
# 没思路了，下面是攻略的解法
# 基本思路是：将浮点数的总数(7367)做因式分解，得到53和139
# 然后以此做为宽和高，用浮点数与256的乘积作为灰度值画成图片，
# 调整方向后得到公式
# 根据公式对浮点数3个一组操作，将结果转换为字符，得到下一关的名称。
def level_30():
	f=open(ur'd:\yankeedoodle.csv')
	data=' '.join(f.read().splitlines())
	f.close()
	fields=data.split(', ') # 注意是逗号加空格！如果只是空格，则后面拼message时只会得到乱码。
	print len(fields)

	n=len(fields) # 输出 7367

	# 因式分解之
	def factor(n):
		"Adapted from http://www.math.utah.edu/~carlson/notes/python.pdf"
		d = 2
		factors = []
		while not n % d:
			factors.append(d)
			n /= d
		d = 3
		while n > 1 and d * d <= n:
			if not n % d:
				factors.append(d)
				n /= d
			else:
				d += 2
		if n > 1:
			factors.append(n)
		return factors

	print factor(n) # 输出 [53,139]，也就是说 53*139=7367

##	im=Image.new('L',(53,139))
##	idata=[chr(int(float(x)*256)) for x in fields]
##	im.fromstring(''.join(idata))
	im=Image.new('F',(53,139)) # 'F'表示直接使用浮点数
	im.putdata(map(float,fields),256)
	im=im.transpose(Image.FLIP_LEFT_RIGHT) # 左右翻转
	im=im.transpose(Image.ROTATE_90) # 旋转90度
	im.show() # 能看到公式 n=str(x[i])[5]+str(x[i+1])[5]+str(x[i+2])[6]

	nlist=[]
	for i in range(0,n-2,3):
		n=chr(int(fields[i][5]+fields[i+1][5]+fields[i+2][6]))
		nlist.append(n)
	print ''.join(nlist)
	# 输出 So, you found the hidden message.
	# There is lots of room here for a long message, but we only need very little space to say "look at grandpa", so the rest is just garbage.
	# ==>   http://www.pythonchallenge.com/pc/ring/grandpa.html

# http://www.pythonchallenge.com/pc/ring/grandpa.html
# 第31关
# Where am I?
# 点击岛礁图片 要求用户名和密码，uri是"island : country"
# 网页注释中提示 <!-- short break, this ***REALLY*** has nothing to do with Python -->
# 先猜猜哪个岛礁是哪里？
# google 礁石 形状像性器官，找到 http://www.szvipp.com/ctrip/thalland/thallandscenici.html
# 再google 拉迈海滩之南 性器官 找到 http://www.successfultravel.com.hk/travel_info/koh_samui.htm
# 原来是泰国(thailand)的苏梅岛(koh samui)，这里有两块岩石分别很像男女性器官，分别叫做叫 祖父石 (Hin Ta) 和祖母石 (Hin Yai)
# 用 kohsamui 和 thailand 做用户名密码，进入 http://www.pythonchallenge.com/pc/rock/grandpa.html
# 网页显示 That was too easy. You are still on 31...
# UFOs?
# 没思路啦
# 看攻略。。。。。和分形图有关
# 网页中的图像名为 mandelbrot.gif
# google 得知  mandelbrot 是法国数学家和分形理论家，其发现了著名的 mandelbrot集合
##定义　　曼德布洛特集合（Mandelbrot set）是在复平面上组成分形的点的集合。Mandelbrot集合可以用复二次多项式f(z)=z^2+c来定义。
##　　其中c是一个复参数。对于每一个c，从z=0开始对f(z)进行迭代
##　　序列 (0, f(0), f(f(0)), f(f(f(0))), .......)的值或者延伸到无限大，或者只停留在有限半径的圆盘内。
##　　曼德布洛特集合就是使以上序列不延伸至无限大的所有c点的集合。
##　　从数学上来讲，曼德布洛特集合是一个复数的集合。一个给定的复数c或者属于曼德布洛特集合M，或者不是。
# 根据网页注释中的提示 left="0.34" top="0.57" width="0.036" height="0.027"
# 将上面的数字作为分形函数的参数，攻略上说参数“top”实际上应该是“bottom”
# 自己按照给出的参数画出同样的分形图
# 下面的分形函数 mandelbrot 直接抄袭自官方攻略
def level_31():
	url = 'http://kohsamui:thailand@www.pythonchallenge.com/pc/rock/mandelbrot.gif'
	ufos = Image.open(StringIO(urllib.urlopen(url).read()))
	def mandelbrot(left=0.34, bottom=0.57, width=0.036, height=0.027,max=128, size=(640, 480)):
		xstep = width / size[0]
		ystep = height / size[1]
		for y in xrange(size[1] - 1, -1, -1):
			for x in xrange(size[0]):
				c = complex(left + x * xstep, bottom + y * ystep)
				z = 0+0j
				for i in xrange(max):
					z = z * z + c
					if abs(z) > 2:
						break
				yield i
	# 因式分解之
	def factor(n):
		"Adapted from http://www.math.utah.edu/~carlson/notes/python.pdf"
		d = 2
		factors = []
		while not n % d:
			factors.append(d)
			n /= d
		d = 3
		while n > 1 and d * d <= n:
			if not n % d:
				factors.append(d)
				n /= d
			else:
				d += 2
		if n > 1:
			factors.append(n)
		return factors

	mandel = ufos.copy() # 直接使用原图的类型、大小和调色板
	mandel.putdata(list(mandelbrot()))
	mandel.show() # 自己画出的图像看上去和给出的图一样
	# 通过比较像素确定自己画的图和给出的图的差异
	differences = [(a - b) for a, b in zip(ufos.getdata(), mandel.getdata()) if a != b]
	print len(differences) # 输出 1679，说明实际上有1679处不同
	print set(differences) # 输出set([-16, 16])，说明实际上所有差异都是16或者-16
	# 调用level30里面用过的因式分解函数
	print factor(len(differences)) # 输出 [23, 73] ，说明可以解析为23×73的图像
	# 构造 23×73的图像，放大10倍后显示
	plot=Image.new('L',(23,73))
	plot.putdata([(i < 16) and 255 or 0 for i in differences]) # 是-16则设为255，否则设为0
	plot.resize((230, 730)).show() # 显示一幅奇怪的图像
	# google得知 上面显示的图是由位于美国波多里格的Arecibo天文台的目前全球最大的射电望远镜
	# 发射到外太空以期与外星人沟通的无线电信号。Arecibo天文台的射电望远镜口径350米，就是007《黄金眼》
	# 中出现的那个超大的湖水下的大碗(又想起了里面的漂亮MM ^_^)。
	# 信号含义见 http://zh.wikipedia.org/wiki/%E9%98%BF%E9%9B%B7%E8%A5%BF%E5%8D%9A%E4%BF%A1%E6%81%AF
	# 下一关的key就是 arecibo  ==> http://www.pythonchallenge.com/pc/rock/arecibo.html



# http://www.pythonchallenge.com/pc/rock/arecibo.html
# 第32关
# etch-a-scetch
# 好像是个游戏
# 每行没列前头都用数字表示本行本列各连续方块的个数
# 网页提示 Fill in the blanks <!-- for warmup.txt -->
# 下载 http://www.pythonchallenge.com/pc/rock/warmup.txt
### Dimensions
##9 9
### Horizontal
##2 1 2
##1 3 1
##5
##7
##9
##3
##2 3 2
##2 3 2
##2 3 2
### Vertical
##2 1 3
##1 2 3
##3
##8
##9
##8
##3
##1 2 3
##2 1 3
#
# 网上查了一下，这种根据行列连续块的信息还原点阵图的游戏有个专门的名称叫Nonogram
# 见 http://zh.wikipedia.org/zh-cn/Nonogram
# 完成程序的过程比较曲折：
# 1）一开始看到是9*9的小图，就直接用0-512枚举生成每行每列的可能，
#    然后用穷举的方式通过正则匹配测试，得到了画着上箭头的图 ==>  http://www.pythonchallenge.com/pc/rock/up.html
#    此时得到的需要还原的图是 32*32 的大图，原来的生成每行每列可能排列的方法的效率太低，没法用了；
# 2）然后用非递归方式写出生成每行每列可能排列的新方法（genlist()），但是在进行穷举时，发现
#    需要穷举的次数是个天文数字了，根本不可能短时间内算出结果；
# 3）经过仔细研究，开始尝试先从现有的可能排列中得到能确定是留空还是填充的点，再根据这些点反过来再次过滤所有
#    可能以去掉不符合的排列，然后再根据保留下的可能排列再次得到能确定的新的留空/填充的点，再用这些点反过来
#    过滤掉不符合的排列，如此反复进行 确定留空/填充点->过滤不符合排列->确定新的留空/填充点，经过26次后
#    终于将32*32个点都确定，最终得到画着蟒蛇的图；
# 4）最初的程序需要执行近22秒，经过优化后，单独执行大概需要近2秒，基本满意。后来从攻略中看到了
#    通过递归生成每行每列可能排列的函数（genv()），稍微修改就拿来用了，比genlist()要快0.5秒。
#    现在的程序算这个32*32的蟒蛇图需要约1.5秒(test3())。
# 5）考虑到应该尽早的以行/列新确定的点为过滤条件减少对应列/行的可能排列，这样可以减少迭代次数，并且减少函数调用
#    将主要逻辑放在一起，经测试32*32需要约1.3秒(test4())
# 根据蟒蛇图 ==>  http://www.pythonchallenge.com/pc/rock/python.html
# ps: 值得注意是网页也给出了解出的蟒蛇图js代码（http://www.pythonchallenge.com/pc/rock/python.js）
# 网页提示：
# Congrats! You made it through to the smiling python.
# "Free" as in "Free speech", not as in "free...
#
# 上面每个单词都认识，组合起来啥意思不知道:(，google之
# 搜 “Free as in Free speech, not as in free”搜到第一条是
# http://www.gnu.org/philosophy/free-sw.html 中的
# "Free software" is a matter of liberty, not price. To understand the concept, you should think of "free" as in "free speech," not as in "free beer."
# 好像意思是说自由软件指权利上的自由而不是指免费。要理解这一点，你可以比较“自由演讲”和“免费啤酒”中的free的区别。
# 所以提示中"free..."中的"..."指的是 beer  ==>   http://www.pythonchallenge.com/pc/rock/beer.html
def level_32():

	def test3(width,height):
		UNKNOWN,FILL,EMPTY='?','1',' '
		resovled=[[UNKNOWN for _ in xrange(width)] for _ in xrange(height)]

		totalnumber=width*height
		print totalnumber

		def genv(v,l,marks):
			'''递归方式获取可能的排列
			v=描述串(tuple列表) l=行/列长度 marks=(填满,留空)
			'''
			r=[]
			j=0
			if v:
				if len(v)==1:
					j=1
				for i in range(l+2-len(v)-sum(v)):
					ri=marks[1]*i+marks[0]*v[0]+marks[1]*(1-j)
					if j:
						rr=[marks[1]*(l-len(ri))]
					else:
						rr=genv(v[1:],l-len(ri),marks)
					r+=[ri+vv for vv in rr]
				return r
			else:
				return [marks[1]*l]

		# 非递归方式获取可能的排列，比上面递归方式的genv要慢一点
		def genlist(dim,blocklist,marks=('1','0')):
			'''非递归方式获取可能的排列
			dim=行/列长度 blocklist=描述串(tuple列表)  marks=(填满,留空)
			'''
			ret=[]
			blankcnt=dim-sum(blocklist)
			blockcnt=len(blocklist)
			idxl=[1 for i in xrange(blockcnt+1)]
			idxl[0]=0
			idxl[-1]=blankcnt-(blockcnt-1)

			cur=len(idxl)-2
			tmp=cur
			while tmp!=-1:
				tmpstr=''.join([ marks[1]*idxl[x]+marks[0]*blocklist[x] for x in range(blockcnt)]+[marks[1]*idxl[-1],])
				ret.append(tmpstr)

				if idxl[-1]==0: # 需要进位
					tmp=cur-1 # 上一位
					while tmp!=-1: # tmp=-1 无位可进，说明列举完毕，退出
						if idxl[tmp]<blankcnt-(blockcnt-tmp-1)-sum(idxl[:tmp]): # 此位可以再增加1
							idxl[tmp]+=1
							for i in range(tmp+1,blockcnt):
								idxl[i]=1
							idxl[-1]=blankcnt-sum(idxl[:-1])
							break
						else: # 此位不能再增加，需要查看更前的一位
							tmp-=1
				else:
					idxl[cur]+=1
					for i in range(cur+1,blockcnt):
						idxl[i]=1
					idxl[-1]=blankcnt-sum(idxl[:-1])

			return ret
	##	assert sum(sum(x) for x in Horizontal)==sum(sum(x) for x in Vertical)

	##	Hlist=[genlist(width,item,(FILL,EMPTY)) for item in Horizontal]
	##	Vlist=[genlist(height,item,(FILL,EMPTY)) for item in Vertical]
		Hlist=[genv(a,width,(FILL,EMPTY)) for a in Horizontal]
		Vlist=[genv(a,height,(FILL,EMPTY)) for a in Vertical]
		print 'all possible row/col generated.'

		def checksingle(idx,l):
			'''检查l中所有item的第idx项是否一致，不一致则返回None，否则返回这项的值'''
			for item in l:
				if item[idx]!=l[0][idx]:
					return None
			return l[0][idx]

		def confirmed():
			'''根据现有的Hlist Vlist搜索可确定的块，在resovled中标出，并返回包含这些新确定的块的列表'''
			ret=[]
			# 按行搜索可确定块
			for i,rows in enumerate(Hlist):
				for j in range(width):
					if resovled[i][j]==UNKNOWN:
						t= checksingle(j,rows)
						if t:
							resovled[i][j]=t
							ret.append((i,j))
			# 按列搜索可确定块
			for i,cols in enumerate(Vlist):
				for j in range(height):
					if resovled[j][i]==UNKNOWN:
						t= checksingle(j,cols)
						if t:
							resovled[j][i]=t
							ret.append((j,i))
			return ret

		def reducePossible(obj2check):
			'''根据obj2check过滤不符合条件的可能排列'''
			for i,j in obj2check:
				# 行过滤
				c=resovled[i][j] # 有此中间变量可使程序快0.05s
				Hlist[i]=[item for item in Hlist[i] if item[j]==c]
				# 列过滤
				Vlist[j]=[item for item in Vlist[j] if item[i]==c]
			print 'H after: ',
			print ','.join([str(len(x)) for x in Hlist])
			print 'V after: ',
			print ','.join([str(len(x)) for x in Vlist])

		resovlednumber=0
		itercnt=1
		while resovlednumber!=totalnumber:
			print 'itercnt=%d'%(itercnt,)
			tocheck=confirmed()
			if len(tocheck)==0:
				print 'no more number can confirm! %d'%(resovlednumber,)
				break
			resovlednumber+=len(tocheck)
			reducePossible(tocheck)

			print 'resolved number: %d'%(resovlednumber,)
	##		print out
			itercnt+=1
		print	'\n'.join([''.join(j)  for j in resovled])
		print '%s done! %s'%('='*30,'='*30)

	def test4(width,height):
		UNKNOWN,FILL,EMPTY='?','1',' '
		resovled=[[UNKNOWN for _ in xrange(width)] for _ in xrange(height)]

		totalnumber=width*height
		print totalnumber

		def genv(v,l,marks):
			r=[]
			j=0
			if v:
				if len(v)==1:
					j=1
				for i in range(l+2-len(v)-sum(v)):
					ri=marks[1]*i+marks[0]*v[0]+marks[1]*(1-j)
					if j:
						rr=[marks[1]*(l-len(ri))]
					else:
						rr=genv(v[1:],l-len(ri),marks)
					r+=[ri+vv for vv in rr]
				return r
			else:
				return [marks[1]*l]

		def checksingle(idx,l):
			'''检查l中所有item的第idx项是否一致，不一致则返回None，否则返回这项的值'''
			for item in l:
				if item[idx]!=l[0][idx]:
					return None
			return l[0][idx]

		Hlist=[genv(a,width,(FILL,EMPTY)) for a in Horizontal]
		Vlist=[genv(a,height,(FILL,EMPTY)) for a in Vertical]
		print 'all possible row/col generated.'


		resovlednumber=0
		itercnt=1
		while resovlednumber!=totalnumber:
			print '\nitercnt=%d'%(itercnt,)
			for i,rows in enumerate(Hlist):
				for j in range(width):
					if resovled[i][j]==UNKNOWN:
						t=checksingle(j,rows)
						if t:
							resovled[i][j]=t
							Vlist[j]=[item for item in Vlist[j] if item[i]==t] # 马上用确定的点来减少Vlist对应列的可能数量
							resovlednumber+=1
			for i,cols in enumerate(Vlist):
				for j in range(height):
					if resovled[j][i]==UNKNOWN:
						t= checksingle(j,cols)
						if t:
							resovled[j][i]=t
							Hlist[j]=[item for item in Hlist[j] if item[i]==t] # 马上用确定的点来减少Hlist对应行的可能数量
							resovlednumber+=1

			print 'H after: ',
			print ','.join([str(len(x)) for x in Hlist])
			print 'V after: ',
			print ','.join([str(len(x)) for x in Vlist])
			itercnt+=1

		print	'\n'.join([''.join(j)  for j in resovled])
		print '%s done! %s'%('='*30,'='*30)


	Horizontal=((2,1,2),(1,3,1),(5,),(7,),(9,),(3,),(2,3,2),(2,3,2),(2,3,2))
	Vertical=((2,1,3),(1,2,3),(3,),(8,),(9,),(8,),(3,),(1,2,3),(2,1,3))
	test4(9,9)

	Horizontal=((3,2),(8,),(10,),(3,1,1),(5,2,1),(5,2,1),(4,1,1),(15,),(19,),(6,14),(6,1,12),(6,1,10),(7,2,1,8),(6,1,1,2,1,1,1,1),(5,1,4,1),(5,4,1,4,1,1,1),(5,1,1,8),(5,2,1,8),(6,1,2,1,3),(6,3,2,1),(6,1,5),(1,6,3),(2,7,2),(3,3,10,4),(9,12,1),(22,1),(21,4),(1,17,1),(2,8,5,1),(2,2,4),(5,2,1,1),(5,))
	Vertical=((5,),(5,),(5,),(3,1),(3,1),(5,),(5,),(6,),(5,6),(9,5),(11,5,1),(13,6,1),(14,6,1),(7,12,1),(6,1,11,1),(3,1,1,1,9,1),(3,4,10),(8,1,1,2,8,1),(10,1,1,1,7,1),(10,4,1,1,7,1),(3,2,5,2,1,2,6,2),(3,2,4,2,1,1,4,1),(2,6,3,1,1,1,1,1),(12,3,1,2,1,1,1),(3,2,7,3,1,2,1,2),(2,6,3,1,1,1,1),(12,3,1,5),(6,3,1),(6,4,1),(5,4),(4,1,1),(5,))
	test4(32,32)

# http://www.pythonchallenge.com/pc/rock/beer.html
# 第33关
# 33 bottles of beer on the wall
# 网页注释中提示:
# <!--
# If you are blinded by the light,
# remove its power, with its might.
# Then from the ashes, fair and square,
# another truth at you will glare.
# -->
#
# 注意到图像名称是beer1.jpg，看看 http://www.pythonchallenge.com/pc/rock/beer2.jpg
# 图上提示 no, png，看看 http://www.pythonchallenge.com/pc/rock/beer2.png
# 好像是个有个x的灰度杂波图
# 查看图片信息(通过img.getcolors()) 可知，图像有66种颜色:
# [(1532, 1), (232, 2), (963, 7), (189, 8), (724, 13), (329, 14), (549, 19), (243, 20),
#  (144, 25), (424, 26), (119, 31), (328, 32), (126, 37), (339, 38), (126, 43), (357, 44),
#  (107, 49), (225, 50), (79, 55), (609, 56), (181, 61), (356, 62), (70, 67), (298, 68),
#  (23, 73), (164, 74), (26, 79), (354, 80), (47, 85), (341, 86), (139, 91), (257, 92),
#  (104, 97), (505, 98), (192, 103), (224, 104), (114, 109), (310, 110), (32, 115), (183, 116),
#  (238, 121), (198, 122), (117, 127), (327, 128), (110, 133), (342, 134), (118, 139), (342, 140),
#  (145, 145), (323, 146), (152, 151), (324, 152), (161, 157), (323, 158), (175, 163), (317, 164),
#  (183, 169), (317, 170), (171, 175), (337, 176), (198, 181), (318, 182), (241, 187), (283, 188),
#  (1348, 193), (272, 194)
# 仔细看发现,每两种颜色值相邻，可以分为一组(1和2, 7和8, 13和14 ...)，
# 每组颜色的像素数累加后开平方可得一个整数，比如颜色1和2的像素数 sqrt(1532+232)=42，
# 颜色1，2，7和8的像素数 sqrt(1532+232+963+189)=54
# 颜色1，2，7，8，13和14的像素数 sqrt(1532+232+963+189+724+329)=63
# 再根据提示中的"light"，"remove its power"和"square" 猜想：
# 0) 以所有像素为整体开始；
# 1) 以当前像素数开平方的值做为宽高建立新图片；
# 2) 将当前像素中颜色值最大的一组像素标为最暗其他则标为最亮(反过来也行)，然后输出到新图片中；
# 3) 从当前像素中去掉当前颜色值最大的一组(因为最亮嘛)，然后转到第1)步；
# 如此循环共建立33个新图片，查看一下输出是否有意义
def level_33():
	img=Image.open(r'd:\beer2.png')
	colors=img.getcolors()
	cl=len(colors)
	l=img.getdata() # 当前操作的像素集合
##	starttime=clock()

	i=cl-1 # 65
	while i>0:
		dim=sqrt(len(l)) # 确定宽高
##		assert dim==dim/1 # 可开方为整数
		newimg=Image.new('P',(dim,dim))
		out=[ 255 if x!=colors[i][1] else 0 for x in l] # 亮色赋值为0，其他为255
		newimg.putdata(out)
		newimg.save('d:\\level33_%02d.png'%((cl-i+1)/2,),'png') # 存成33幅图片
##		newimg.show()
		tmp=[m[1] for m in colors[i-1:i+1]] # 本次操作后需要滤掉的像素值集合
		l=[item for item in l if item not in tmp] # 产生下次需要操作的像素
		i-=2

##	print 'time=',clock()-starttime
	# 存成的33幅图片，每个图片上有一个字母分别是：
	# x x x x x      x x x x x
	# x x v i n      e [g] a [r] w
	# i n [e] [m] o  [l] d [i] [n] o
	# [s] l o
	# 其中带[]的表示字母是被方框圈起来的
	# 带[]的字母连起来是 gremlins，查字典是精灵的意思  ==> http://www.pythonchallenge.com/pc/rock/gremlins.html
	# 终于来到了页面 Temporary End!
	# 至此闯关完毕！
	#



if __name__=="__main__":
	import re
	import urllib2
	import cookielib
	import pickle
	import zipfile
	from PIL import PngImagePlugin
	from PIL import JpegImagePlugin
	from PIL import GifImagePlugin
	from PIL import ImageDraw
	from PIL import Image
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
	import zlib
	import string
	from math import sqrt
	import hashlib
	import keyword
	from cStringIO import StringIO
	from time import clock
	level_33()