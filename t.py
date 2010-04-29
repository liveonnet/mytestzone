#encoding=utf-8
from PIL import PngImagePlugin
from PIL import Image
from PIL import ImagePalette
from PIL import ImageChops
from glob import glob
import os
import time
import hashlib
import sys


def imgFilter(fname):
	'''过滤干扰线和杂色点'''
	img=PngImagePlugin.PngImageFile(fname)
	img=img.crop((0,img.size[1]/2,img.size[0],img.size[1])) # 取图片下半部
	#print("%s"%(img.size,))
	nimg=Image.eval(img,lambda x: 0 if x!=216 else 216) # 不是索引216(绿)则置为索引0(白)
	return nimg

def imgCompositeSame(odir,datadate,grouptime=None):
	'''将同一组文件叠加以得到完整字符图像，返回图像文件列表'''
	result=[]
	if grouptime==None:
		l=glob('d:\\gardenspirit\\%s-*.png'%(datadate,))
		s=set()
		for i in l:
			k=i.split('-',2)[1]
			s.add(k) # 根据时间分组
	else:
		s=set((grouptime,))

	nlist=['d:\\gardenspirit\\%s-%s-*.png'%(datadate,i) for i in s]

	for idx,n in enumerate(nlist): # 每组
		print('%s\n%02d %s\n%s'%('='*40,idx+1,n,'='*40))

		fnamelist=glob(n)
		nimg=Image.new('P',(400,30))
		_,oname=os.path.split(n)
		# 构造输出文件名
		oname=oname.replace('*','merged')
		oname=os.path.join(odir,oname)

		for i,filename in enumerate(fnamelist): # 一组中的每个文件
			print(filename)
			nimg=Image.blend(nimg,imgFilter(filename),0.5)

##		print(nimg.getcolors())
		nimg=Image.eval(nimg,lambda x: 255 if x==0 else 0) # 索引0(黑)置为索引255(白)，其他索引置为0
		nimg=nimg.convert('1')
		nimg.save(oname)
		result.append(oname)

	return result


def imgFilterInsularPoint(imgdata,magic,radius,pointvalue):
	'''消除孤立点,以点为中心, radius为半径获取方块，如果方块中有效点数目小于pointvalue则认为是孤立点'''
	for x in range(0,imgdata.size[0],1):
		col=imgdata.crop((x,0,x+1,imgdata.size[1]))
		bs=list(col.getdata())
		cnt=bs.count(magic)
		if cnt>=1 and cnt<=2:
			for y,p in enumerate(bs): # (x,y)
				if p==magic:
					assert imgdata.getpixel((x,y))==magic
					left= x-radius if x-radius>0 else 0
					top= y-radius if y-radius>0 else 0
					right= x+radius if x+radius<imgdata.size[0] else imgdata.size[0]
					bottom= y+radius if y+radius<imgdata.size[1] else imgdata.size[1]
					area=list(imgdata.crop((left,top,right,bottom)).getdata())
					if area.count(magic)<pointvalue:
##						print(u"(%d,%d) 是孤立点"%(x,y))
						imgdata.putpixel((x,y),255)



def imgSplit(odir,datadate,grouptime=None):
	'''分割每个图片的各字段，返回包含所有找到的图片文件的各5个字段图片的列表'''
	result=[]
	magic=0
	if grouptime==None:
		fname='%s%s-*-merged.png'%(odir,datadate)
		nlist=glob(fname)
	else:
		fname='%s%s-%s-merged.png'%(odir,datadate,grouptime)
		nlist=[fname]

	for n in nlist:
		print(n)
		nimg=Image.open(n)
		#nimg.show()

		imgFilterInsularPoint(nimg,magic,8,4)
		#nimg.show()

		# 确定上下边界
		edgey=[0,nimg.size[1]] # 上下
		g=((0,nimg.size[1],1,0),(nimg.size[1]-1,0,-1,1))
		for edgeidx,(begin,end,step,offset) in enumerate(g):
			for y in range(begin,end,step):
				row=nimg.crop((0,y,nimg.size[0],y+1))
				bs=list(row.getdata())
				if bs.count(magic)>5:
					edgey[edgeidx]=y+offset
#					print edgey[idx]
					break
		# 确定左右边界
		edgex=[0,nimg.size[0]] # 左右
		g=((0,nimg.size[0],1,0),(nimg.size[0]-1,0,-1,1))
		for edgeidx,(begin,end,step,offset) in enumerate(g):
			for x in range(begin,end,step):
				col=nimg.crop((x,0,x+1,nimg.size[1]))
				bs=list(col.getdata())
				if bs.count(magic)>=1:
					edgex[edgeidx]=x+offset
#					print edgex[idx]
					break

		nimg=nimg.crop((edgex[0],edgey[0],edgex[1],edgey[1]))
		print("%s"%(nimg.size,))
##		nimg.show()

		# 构造每列及其后18列的区块
		imgcols=[]
		for x in range(0,nimg.size[0]-22,1): # 最右边留下22列，最后一个字段最少也是22列
			col=nimg.crop((x,0,x+18,nimg.size[1]))
			bs=list(col.getdata())
			imgcols.append(bs)

		lastidx=0
		for colidx,curcol in enumerate(imgcols):
			if colidx<=lastidx:
				continue
			if curcol.count(magic)==0:# 当前列及其后18列都不含有效点，认为是当前字段的结束
				print("idx=%d"%(colidx,))
				assert colidx>lastidx+22 # 至少相隔两个字
				one=nimg.crop((lastidx,0,colidx,nimg.size[1]))
				result.append(one)
##				one.show()
				# 寻找下一字段起点
##				print ("nimg.size[0]=%d"%(nimg.size[0],))
				for x in range(colidx+18,nimg.size[0]-22,1):
					tmpcol=nimg.crop((x,0,x+1,nimg.size[1])) # 取一列
					bs=list(tmpcol.getdata())
##					print("%d %d count=%d"%(x,nimg.size[0]-22,bs.count(magic),))
					if bs.count(magic)>=1: # 此列包含至少一个有效点
						print("find next chars at %d"%(x,))
						lastidx=x
						break
		# 最后一个字段
		last=nimg.crop((lastidx,0,nimg.size[0],nimg.size[1]))
##		last.show()
		result.append(last)

	return result

def removeDup(fname):
	d={}
	nlist=glob(fname)
	for i in nlist:
		k=hashlib.md5(open(i,'rb').read()).hexdigest()
		if k in d:
			_,name= os.path.split(i)
			if name.startswith('00'):
				print(u"删除 %s"%(i,))
				os.remove(i)
			else:
				print(u"删除 %s"%(d[k],))
				os.remove(d[k])
				d[k]=i
		else:
			d[k]=i


def cmpPic(datadate,timegroup,ids):
	assert timegroup!=None 
	assert timegroup!=''
	print(ids)
	imgCompositeSame('d:\\gardenspirit\\merged\\',datadate,timegroup)
	l=imgSplit('d:\\gardenspirit\\merged\\',datadate,timegroup)
	assert len(l)==5
	seedids=ids.split(',')
	assert len(seedids)==5
	result={}
	baseimgdict={}
	for seedid in seedids:
		fn='d:\\gardenspirit\\base\\%s.png'%(seedid,)
		print("need %s"%(fn,))
		if os.path.exists(fn):
			img=PngImagePlugin.PngImageFile(fn)
			baseimgdict[seedid]=img
		else:
			print(u"can't find base file %s!"%(seedid,))
			return result

	d={}
	for unidx,unimg in enumerate(l):
		d[str(unidx)]=unimg

	while len(d)!=0:
		un_todel=[]
		base_todel=[]
		for unk,unimg in d.iteritems():
			uwidth,uheight=unimg.size
			for basek,baseimg in baseimgdict.iteritems():
				# size check
				bwidth,bheight=baseimg.size
				if abs(uwidth-bwidth)<9 and abs(uheight-bheight)<9: # 尺寸相差小于一个字
					print('='*30)
					print("%s VS. %s"%(unimg.size,baseimg.size))
					#unimg.show()
					#baseimg.show()
					r=ImageChops.difference(unimg,baseimg) # 比较内容
					bs=list(r.getdata())
					#r.show()
					dif=bs.count(255)
					print("unknown pic %s DIFF base %s = %d"%(unk,basek,dif))
					if dif<8:
						result[unk]=basek
						un_todel.append(unk)
						base_todel.append(basek)
						break

			for x in base_todel:
				del baseimgdict[x]
			if len(un_todel)!=0:
				break
		for x in un_todel:
			del d[x]


	if len(result)==5:
		return result


def processImg2Base(odir,datadate):
	imgCompositeSame(odir,datadate)
	l=imgSplit(odir,datadate)
	for idx,i in enumerate(l):
		i.save('d:\\gardenspirit\\base\\%05d.png'%(idx,))

	removeDup('d:\\gardenspirit\\base\\*.png')


if __name__=='__main__':
##	imgCompositeSame('d:\\','20100417','202254')
##	l=imgSplit('d:\\','20100417','134400')

	##rslt=cmpPic('20100417', '132310','13,15,19,38,39')
	#rslt=cmpPic('20100417', '202254','1,5,7,13,41')
	#if len(rslt)==5:
	#	rtn=['',]*5
	#	for k,v in rslt.items():
	#		rtn[int(k)]=v
	#	print (u"结果=%s"%(','.join(rtn)))
	#else:
	#	print(u"未能识别!")


	s = sys.stdin.readline()
	datadate,timegroup,seedids=s.split('|')
	#f=open(r'd:\getdata.txt','w')
	#f.write(datadate)
	#f.write('\n' )
	#f.write(timegroup)
	#f.write('\n' )
	#f.write(seedids)
	#f.write('\n' )
	#f.close()
	rslt=cmpPic(datadate, timegroup,seedids)
	if len(rslt)==5:
		rtn=['',]*5
		for k,v in rslt.items():
			rtn[int(k)]=v
		sys.stderr.write(",%s"%(','.join(rtn)))
	else:
		sys.stdout.write("!")
	#sys.stdout.write('I have got the data!\n')
	
	
	

	#imgCompositeSame('d:\\','20100417')
	#l=imgSplit('d:\\','20100417')
	#for idx,i in enumerate(l):
	#	i.save('d:\\gardenspirit\\base\\%05d.png'%(idx,))

	#removeDup('d:\\gardenspirit\\base\\*.png')
