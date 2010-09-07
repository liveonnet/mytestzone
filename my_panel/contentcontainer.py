#coding=utf-8
import codecs
import re
import logging
import os
import struct
import gzip
from io import BufferedReader
import urllib, urllib.request, urllib.error, urllib.parse, http.cookiejar, json
import time
import datetime
##from feed import GoogleFeed
import threading
from _thread import start_new_thread
from collections import deque
import mmap
import codecs

class WordFile(object):
	def __init__(self,fname):
		self.logger=logging.getLogger(self.__class__.__name__)
		try:
			self.wordlist=codecs.open(fname,encoding='gb18030').readlines()
		except UnicodeDecodeError:
			self.wordlist=codecs.open(fname,encoding='utf8').readlines()
		self.wordlist=[ i.strip() for i in self.wordlist if len(i.strip())!=0]
		self.maxidx=len(self.wordlist)-1
		self.curidx=0

	def __iter__(self):
		return self

	def __next__(self):
		if self.curidx<self.maxidx:
			self.curidx+=1
			return self.wordlist[self.curidx-1]
		else:
			raise StopIteration()

	def __len__(self):
		return len(self.wordlist)

	def __getitem__(self,key):
		return self.wordlist[key]

	def setStart(self,idx):
		if idx<self.maxidx:
			self.curidx=idx
		else:
			self.curidx=self.maxidx

	def getIdx(self):
		return self.curidx-1


class SubtitleFile(object):
	def __init__(self,fname):
		self.logger=logging.getLogger(self.__class__.__name__)
		try:
			self.wordlist=codecs.open(fname,encoding='gb18030').readlines()
		except UnicodeDecodeError:
			self.wordlist=codecs.open(fname,encoding='utf8').readlines()

		logging.debug('use %s to split...',repr(os.linesep*2))
		self._wordlist=re.split(os.linesep*2,''.join(self.wordlist))
		if len(self._wordlist)<10:
			logging.debug('use %s to split...',repr(os.linesep))
			self._wordlist=re.split(os.linesep,''.join(self.wordlist))

		self.wordlist=self._wordlist
		logging.debug('len(self.wordlist)=%d',len(self.wordlist))
		logging.debug('self.wordlist[:3]=%s',self.wordlist[:3])
		self.maxidx=len(self.wordlist)-1
		self.curidx=0

	def __iter__(self):
		return self

	def __next__(self):
		if self.curidx<self.maxidx:
			self.curidx+=1
			return self.wordlist[self.curidx-1]
		else:
			raise StopIteration()

	def __len__(self):
		return len(self.wordlist)

	def __getitem__(self,key):
		return self.wordlist[key]

	def setStart(self,idx):
		if idx<self.maxidx:
			self.curidx=idx
		else:
			self.curidx=self.maxidx

	def getIdx(self):
		return self.curidx-1


class StartDictFile(object):
	__maxWordStrLen=256
	__maxOffsetLen=4
	__functionMaping={
		'm':'__readDict_m','l':'__readDict_l','g':'__readDict_g',
		't':'__readDict_t','x':'__readDict_x','y':'__readDict_y',
		'k':'__readDict_k','w':'__readDict_w','h':'__readDict_h',
		'r':'__readDict_r','W':'__readDict_W','P':'__readDict_P',
		'X':'__readDict_X','n':'__readDIct_n'}

	def __init__(self,fname):
		self.logger=logging.getLogger(self.__class__.__name__)
		self.__baseFileName=''
		tmp=fname.rpartition('.')
		self.__dictFileName=None
		if fname.endswith(('.dz','.DZ','.dZ','.Dz')):
			logging.debug('the file name is dz file!')
			self.__dictFileName=fname.lower()
			tmp=tmp.rpartition('.')
		if tmp[0] is None and tmp[1] is None:
			self.logger.debug("no dot found in filename %s",fname)
			self.__baseFileName=tmp[2]
		else:
			self.__baseFileName=tmp[0]
		self.__idxFileName=self.__baseFileName+'.idx'
		self.__ifoFileName=self.__baseFileName+'.ifo'
		if not self.__dictFileName:
			if not os.path.exists(self.__baseFileName+'.dict'):
				self.__dictFileName=self.__baseFileName+'.dict.dz'
			else:
				self.__dictFileName=self.__baseFileName+'.dict'

		self.__dictInfo={}
		self.__dictIndex={}


	def getIdxList(self):
		return sorted(self.__dictIndex.keys())


	def readIFO(self):
		with codecs.open(self.__ifoFileName,'r',encoding='utf-8') as f:
			for line in f:
				line=line.rstrip()
				if line.find("=")==-1:
					continue
				kv=line.split("=")
				if len(kv)<1:
					continue
				self.__dictInfo[kv[0]]=(len(kv)>1 and [kv[1]] or [None])[0]

		if self.__dictInfo["version"]=="3.0.0" and self.__dictInfo.has_key("idxoffsetbits"):
				self.__class__.__maxOffsetLen=int(self.__dictInfo["idxoffsetbits"])/8
				logging.debug("word_data_offset is %d bytes !",self.__class__.__maxOffsetLen)

		self.logger.debug("self.__dictInfo=%s",self.__dictInfo);


	def readIDX(self):
		with open(self.__idxFileName,'rb') as f:
			fmap=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
			cur=0
##			wordStr=""
##			wordDataOffset,wordDataSize=0,0
			while True:
				cur,wordStr=self.__readUntilZeroEx(fmap,cur)
				if not wordStr:
##					self.logger.debug("wordStr=\"\",break!")
					fmap.close()
					break
##				cur,self.__dictIndex[wordStr]=cur+8,\
##					(fmap[cur]<<24|fmap[cur+1]<<16|fmap[cur+2]<<8|fmap[cur+3],\
##					fmap[cur+4]<<24|fmap[cur+5]<<16|fmap[cur+6]<<8|fmap[cur+7])
				cur,self.__dictIndex[wordStr]=self.__readNumbers(fmap,cur,self.__class__.__maxOffsetLen*2)
			fmap.close()

		self.logger.debug("len(self.__dictIndex)=%d",len(self.__dictIndex))

	def __readUntilZero(self,fileObj,maxRead=0,debug=False):
		if maxRead:
			return fileObj.read(maxRead)

		strRtn=b""
		while True:
			by=fileObj.read(1)
			if by=="":
				break
			try:
				tmp=by.decode('utf-8')
				if tmp=="\0" :# or by=="": # TODO: no EOF check here!
					break
				strRtn+=by
			except UnicodeDecodeError:
				strRtn+=by

		return strRtn.decode('utf-8')

	def __readUntilZeroEx(self,f,pos,size=0):
		if size:
			return pos+size,f[pos:pos+size]

		idx=f.find(b'\0',pos)
		if idx!=-1:
			return idx+1,f[pos:idx].decode('utf-8')
		else:
##			raise Exception('no zero found! cur %d',f.tell())
			return pos,''

##		idx=f.find(b'\0',pos)
##		if idx!=-1:
##			s=f.read(idx-pos).decode('utf-8')
##			f.seek(1,os.SEEK_CUR)
##			return s
##		else:
####			raise Exception('no zero found! cur %d',f.tell())
##			return ''

	def __readNumber(self,fileObj,numberSize=4):
		strRtn=fileObj.read(numberSize)
		intRtn=struct.unpack("!I",strRtn)[0]
#		logging.debug("strRtn=|%s| intRtn=%d",' '.join(["%02X"%(ord(c)) for c in strRtn]),intRtn)
		return intRtn

	def __readNumbers(self,f,pos,numberSize=4):
		strRtn=f[pos:pos+numberSize]
		return pos+numberSize,struct.unpack("!II",strRtn)
#		logging.debug("strRtn=|%s| intRtn=%d",' '.join(["%02X"%(ord(c)) for c in strRtn]),intRtn)
##		return int1,int2

	def getMeaning(self,strToSearch):
		if not self.__dictIndex:
			self.logger.debug("index file not load!")
			return None

		if not strToSearch:
			self.logger.debug("strToSearch is invalid!")
			return None

		self.logger.debug("strToSearch=|%s|",strToSearch)

		sametype=self.__dictInfo.get("sametypesequence")

		offset,size=self.__dictIndex.get(strToSearch,(None,None))
		if (not offset) or (not size):
			self.logger.debug("key not found!")
			return None
		self.logger.debug("offset=%d,size=%d",offset,size)

		rslt=''

		if self.__dictFileName.endswith('.dz'):
			f= gzip.GzipFile(self.__dictFileName,'rb')
		else:
			f= codecs.open(self.__dictFileName,'rb')
		try:
			f.seek(offset,os.SEEK_SET)
			cnt=0
			by=""
			if not sametype:
				self.logger.debug("sametypesequence not defined!")
				while cnt<size:
					by=f.read(1)
					cnt+=1
					tmpSize=0
					if not self.__class__.__functionMaping.has_key(by):
						self.logger.debug("can't judge data type %s!",ord(by))
						raise Exception()
					tmpSize,tmpText=getattr(self,"_"+self.__class__.__name__+self.__class__.__functionMaping[by])(f,offset,size)
					cnt+=tmpSize
			else:
#				logging.debug("sametypesequence=%s",sametype)
				for datatype in sametype:
					tmpSize=0
					if datatype not in self.__class__.__functionMaping:
						self.logger.debug("can't judge data type %s!",ord(datatype))
						raise Exception()
					tmpSize,tmpText=getattr(self,"_"+self.__class__.__name__+self.__class__.__functionMaping[datatype])(f,offset,size)
					rslt+=tmpText
					cnt+=tmpSize
		finally:
			f.close()

		return rslt


	def __readDict_m(self,fileObj,offset,size):
		# Word's pure text meaning.
		# The data should be a utf-8 string ending with '\0'.'
##		strText=self.__readUntilZeroEx(fileObj,size).decode()
		strText=fileObj.read(size).decode()
##		strText=strText.replace('\n','\\n')
		return (len(strText)+1,strText)
	def __readDict_l(self,fileObj,offset,size):
		# Word's pure text meaning.
		# The data is NOT a utf-8 string, but is instead a string in locale
		# encoding, ending with '\0'.  Sometimes using this type will save disk
		# space, but its use is discouraged.
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_g(self,fileObj,offset,size):
		# A utf-8 string which is marked up with the Pango text markup language.
		# For more information about this markup language, See the "Pango
		# Reference Manual."
		# You might have it installed locally at:
		# file:///usr/share/gtk-doc/html/pango/PangoMarkupFormat.html
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_t(self,fileObj,offset,size):
		# English phonetic string.
		# The data should be a utf-8 string ending with '\0'.
		# Here are some utf-8 phonetic characters:
		# θʃŋʧðʒæıʌʊɒɛəɑɜɔˌˈːˑṃṇḷ
		# æɑɒʌәєŋvθðʃʒɚːɡˏˊˋ
		strPhonetic=""
		strPhonetic=self.__readUntilZero(fileObj)
		self.logger.debug("strPhonetic=|%s|",strPhonetic)
		return (len(strPhonetic)+1,strPhonetic)
	def __readDict_x(self,fileObj,offset,size):
		# A utf-8 string which is marked up with the xdxf language.
		# See http://xdxf.sourceforge.net
		# StarDict have these extention:
		# <rref> can have "type" attribute, it can be "image", "sound", "video"
		# and "attach".
		# <kref> can have "k" attribute.
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_y(self,fileObj,offset,size):
		# Chinese YinBiao or Japanese KANA.
		# The data should be a utf-8 string ending with '\0'.
		strYinBiao=""
		strYinBiao=self.__readUntilZero(fileObj)
		self.logger.debug("strYinBiao=|%s|",strYinBiao)
		return (len(strYinBiao)+1,strYinBiao)
	def __readDict_k(self,fileObj,offset,size):
		# KingSoft PowerWord's data. The data is a utf-8 string ending with '\0'.
		# It is in XML format.
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_w(self,fileObj,offset,size):
		# MediaWiki markup language.
		# See http://meta.wikimedia.org/wiki/Help:Editing#The_wiki_markup
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_h(self,fileObj,offset,size):
		''' Html codes.'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_r(self,fileObj,offset,size):
		'''# Resource file list.
		 The content can be:
		 img:pic/example.jpg	// Image file
		 snd:apple.wav		// Sound file
		 vdo:film.avi		// Video file
		 att:file.bin		// Attachment file
		 More than one line is supported as a list of available files.
		 StarDict will find the files in the Resource Storage.
		 The image will be shown, the sound file will have a play button.
		 You can "save as" the attachment file and so on.
		'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_W(self,fileObj,offset,size):
		''' wav file.
		 The data begins with a network byte-ordered guint32 to identify the wav
		 file's size, immediately followed by the file's content.
		'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_P(self,fileObj,offset,size):
		''' Picture file.
		 The data begins with a network byte-ordered guint32 to identify the picture
		 file's size, immediately followed by the file's content.
		'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_X(self,fileObj,offset,size):
		''' this type identifier is reserved for experimental extensions.'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_None(self,fileObj,offset,size):
		self.logger.debug("do nothing!",)
		return (0,None)

	def __readDict_n(self,fileObj,offset,size):
		'''WordNet data.'''
		self.logger.debug("not implement yet!")
		return (0,None)

	def loadFile(self):
		self.readIFO()
		self.readIDX()

		if self.__dictIndex:
			for key in self.__dictIndex.iterkeys():
				self.getMeaning(key)

	def Dict2Txt(self,ofilename):
		self.readIFO()
		idxFile=""
		dictFile=""
		with open(self.__idxFileName,'rb') as f:
			idxFile=f.read()
		lenidx=len(idxFile)
		with open(self.__dictFileName,'rb') as f:
			dictFile=f.read()
		lendict=len(dictFile)
		of=open(ofilename,'w')
		wordCnt=0
		s=[]
		idx=0
		try:
			while True:
				old_idx=idx
				while idx<lenidx:
					if idxFile[idx]=='\0':
						break
					idx+=1

				if old_idx==idx:
					self.logger.debug("wordStr=\"\",break!")
					break

				wordStr=buffer(idxFile,old_idx,idx-old_idx)
#				offset=ord(idxFile[idx+1])<<24|ord(idxFile[idx+2])<<16|ord(idxFile[idx+3])<<8|ord(idxFile[idx+4])
				offset=struct.unpack_from(">i",idxFile,idx+1)[0]
#				size=ord(idxFile[idx+5])<<24|ord(idxFile[idx+6])<<16|ord(idxFile[idx+7])<<8|ord(idxFile[idx+8])
				size=struct.unpack_from(">i",idxFile,idx+5)[0]

#				logging.debug("wordStr=%s,offset=%d,size=%d",wordStr,offset,size)
				idx+=9

#				wordCnt+=1
#				if wordCnt>10:
#					break

				strText=dictFile[offset:offset+size].replace('\n','\\n')
				s.append("%s\t%s\n"%(wordStr,strText))

			of.writelines(s)
		finally:
			of.close()

		self.logger.debug("done.")


class C4GRApi(object):
	'''简单支持几个google reade api
	refer to http://code.google.com/p/pyrfeed/wiki/GoogleReaderAPI
	'''
	CLIENT_ID='my_panel/0.0.1'
	URL_GR_LOGIN='https://www.google.com/accounts/ClientLogin'
	URL_GR_TOKEN='https://www.google.com/reader/api/0/token'

	URL_GR_API_BASE='https://www.google.com/reader/api/0/'
	URL_GR_API_STREAM_READING_LIST='https://www.google.com/reader/api/0/stream/contents/user/-/state/com.google/reading-list'
	URL_GR_API_TAG_LIST=URL_GR_API_BASE+'tag/list'
	URL_GR_API_UNREAD_COUNT=URL_GR_API_BASE+'unread-count'
	URL_GR_API_SUBSCRIPTION_LIST=URL_GR_API_BASE+'subscription/list'
	URL_GR_API_EDIT_TAG=URL_GR_API_BASE+'edit-tag'

	URL_GR_ATOM_BASE='https://www.google.com/reader/atom/'
	URL_GR_ATOM_STATE_BASE=URL_GR_ATOM_BASE+'user/-/state/com.google/'
	URL_GR_ATOM_STATE_READING_LIST=URL_GR_ATOM_STATE_BASE+'reading-list'
	URL_GR_ATOM_STATE_READ=URL_GR_ATOM_STATE_BASE+'read'
	URL_GR_ATOM_STATE_KEPT_UNREAD=URL_GR_ATOM_STATE_BASE+'kept-unread'
	URL_GR_ATOM_STATE_TRACAKING_KEPT_UNREAD=URL_GR_ATOM_STATE_BASE+'tracking-kept-unread'
	URL_GR_ATOM_STATE_STARRED=URL_GR_ATOM_STATE_BASE+'starred'


	class myHTTPDefaultErrorHandler(urllib.request.HTTPDefaultErrorHandler):
		def http_error_default(self, req, fp, code, msg, hdrs):
			if code==401:
				logger=logging.getLogger(self.__class__.__name__)
				logger.debug('got 401 error')
				return fp

	def __init__(self,email,pwd,cookiefile):
		self.logger=logging.getLogger(self.__class__.__name__)
		self._email=email
		self._pwd=pwd

		self._cookiefile=cookiefile # 保存cookie的文件的名称
##		self._sid=None # 登录后获得的sid
		self._auth=None
		self._token=None
		self._continuation=None
##		self.headers=None
		self._signed_in=False # 标识登录与否

		self.readinglist=None
		self.taglist=None
		self.subscriptionlist=None
		self.unreadlist=None

		self._cj = http.cookiejar.LWPCookieJar()
		try:
			self._cj.revert(self._cooikefile)
		except:
			None
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cj),self.__class__.myHTTPDefaultErrorHandler)
		self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
		urllib.request.install_opener(self.opener)


	@classmethod
	def checkLogin(cls,func):
		'''保证已经登录'''
		def wrap_func(self,*args,**kwargs):
##			self.logger.debug('check login ...')
			if not self.signed():
##				self.logger.debug('try login ...')
				if not self.login(True):
					return None
##				self.logger.debug('login ok ...')
##			else:
##				self.logger.debug('check login done')
			return func(self,*args,**kwargs)
		return wrap_func


	def signed(self):
		return self._signed_in

	def login(self,force=False):
		'''登录'''
		if self.signed() and (not force):
			self.logger.debug('already signed in!')
			return self.signed()

		data={}
		data['service']='reader'
		data['Email']=self._email
		data['Passwd']=self._pwd
		r,_=self.getResponse(self.__class__.URL_GR_LOGIN,data)
		if not r:
			self._signed_in=False
		else:
			r=r.decode()
##			self.logger.debug('login request return %s',r)

			if 'Auth=' in r:
				self._auth=r[r.find('Auth=')+5:r.find('\n',r.find('Auth='))]
				self.logger.debug('Auth=%s',self._auth)
				self._signed_in=True

##				cookie = http.cookiejar.Cookie(version=0, name='SID', value=self._sid, port=None, port_specified=False, domain='.google.com', domain_specified=True, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires='1600000000', discard=False, comment=None, comment_url=None, rest={})
##				self._cj.set_cookie(cookie)
##				cookie = http.cookiejar.Cookie(version=0, name='Auth', value=self._auth, port=None, port_specified=False, domain='.google.com', domain_specified=True, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires='1600000000', discard=False, comment=None, comment_url=None, rest={})
##				self._cj.set_cookie(cookie)
			else:
				self.logger.debug('no Auth found in response! login failed!')

		return self._signed_in

	def getResponse(self,url,data=None,headers=None,**kwargs):
		"""获得请求url的响应"""
		res,rurl=None,None
		req=urllib.request.Request(url,urllib.parse.urlencode(data) if data else None)
		if 	headers:
			for k,v in headers:
				req.add_header(k,v)

		for i in range(3): # 尝试3次
			if i!=0:
				logging.info("第 %d 次尝试...",i+1)
			try:
##				logging.debug("访问 %s",url)
				r = self.opener.open(
					req)#,
##					timeout=30)
				res=r.read()
				rurl=r.geturl()
				break
			except urllib.error.HTTPError as e:
				logging.exception("请求出错！ %s",e)
			except urllib.error.URLError as e:
				logging.info("访问地址 %s 失败! %s",url,e)
			except IOError as e:
				logging.info("IO错误! %s",e)
			except Exception as e:
				logging.info("未知错误! %s",e)
				raise

		return (res,rurl)

##	def getReadingList(self,n=20):
##		'''获取待读的item的列表'''
##		args={'n':n,
##		       'client':self.__class__.CLIENT_ID,
##		       'r':'n',
##           'ck': '%d'%(time.time(),),
##		       'xt':'user/-/state/com.google/read'
##		       }
##		if self._continuation:
##			args['c']=self._continuation
##		url='?'.join((self.__class__.URL_GR_ATOM_STATE_READING_LIST,urllib.parse.urlencode(args)))
##
##		for _ in range(3):
##			headers=[('Authorization','GoogleLogin auth=%s'%(self._auth,))]
##			r,_=self.getResponse(url,None,headers)
##			if r:
##				r=r.decode()
####				self.logger.debug('return %s',r)
##				try:
##					x=GoogleFeed(r)
##				except Exception:
##					if r.find('401 Client Error')!=-1:
##						self.logger.debug('got 401 error, try login ...')
##						self.login(True)
##						continue
##				else:
##					self._continuation=x.get_continuation()
##					return x.get_entries()
##
##		return None


	def getReadingList(self,n=20,cont=True):
		'''获取待读的item的列表'''
		args={'n':n,
		       'client':self.__class__.CLIENT_ID,
		       'r':'n',
           'ck': '%d'%(time.time(),),
		       'ot':'%d'%(time.mktime((datetime.date.today()-datetime.timedelta(30)).timetuple()),),  # 30天前
		       'xt':'user/-/state/com.google/read'
		       }
		if self._continuation and cont:
			args['c']=self._continuation
		url='?'.join((self.__class__.URL_GR_API_STREAM_READING_LIST,urllib.parse.urlencode(args)))

		for _ in range(3):
			headers=[('Authorization','GoogleLogin auth=%s'%(self._auth,))]
			r,_=self.getResponse(url,None,headers)
			if r:
				r=r.decode()
##				self.logger.debug('return %s',r)
				try:
					data=json.loads(r)
				except Exception:
					if r.find('401 Client Error')!=-1:
						self.logger.debug('got 401 error, try login ...')
						self.login(True)
						continue
				else:
					self._continuation=data.get('continuation',None)
					return data.get('items',None)

		return None

	def getTagList(self):
		'''获取tag列表'''
		args={'output':'json',
		       'client':self.__class__.CLIENT_ID,
           'ck': '%.3f'%(time.time(),)
		       }
		url='?'.join((self.__class__.URL_GR_API_TAG_LIST,urllib.parse.urlencode(args)))
		headers=[('Authorization','GoogleLogin auth=%s'%(self._auth,))]
		r,_=self.getResponse(url,None,headers)
		if r:
			r=r.decode()
##			self.logger.debug('return %s',r)
			data=json.loads(r)
			for item in data['tags']:
				self.logger.debug('%s=%s',item['id'],item['sortid'])



	def getSubscriptionList(self):
		'''获取订阅的rss地址列表'''
		args={'output':'json',
		       'client':self.__class__.CLIENT_ID,
           'ck': '%.3f'%(time.time(),)
		       }
		url='?'.join((self.__class__.URL_GR_API_SUBSCRIPTION_LIST,urllib.parse.urlencode(args)))
		headers=[('Authorization','GoogleLogin auth=%s'%(self._auth,))]
		r,_=self.getResponse(url,None,headers)
		if r:
			r=r.decode()
##			self.logger.debug('return %s',r)
			data=json.loads(r)
			self.logger.debug('total subscription : %d',len(data['subscriptions']))
			for item in data['subscriptions']:
				cl=item['categories']
				for c in cl:
					self.logger.debug('%s(%s)',c['id'],c['label'])
				t=int(item['firstitemmsec'])/1000.0
				d=datetime.datetime.fromtimestamp(t)
				self.logger.debug('%s: %s %s at %s\n',item['id'],item['title'],item['sortid'],d.strftime("%Y-%m-%d %H:%M:%S"))

	def getToken(self,force=True):
		if self._token and (not force):
			self.logger.debug('no need get token')
			return True

		for _ in range(2):
			headers=[('Authorization','GoogleLogin auth=%s'%(self._auth,))]
			r,_=self.getResponse(self.__class__.URL_GR_TOKEN,None,headers)
			if r:
				r=r.decode()
				if r.find('401 Client Error')!=-1:
					self.logger.debug('got 401 error, try login ...')
					self.login(True)
					continue
				self._token=r
				self.logger.debug('new token=%s',self._token)
				return True

		return False

	def editTag(self,entry,add,remove,pos,source,token=None):
		'''更改item的tag'''
		for _ in range(4):
			if not token:
				if not self._token:
					self.getToken()
				token=self._token

			headers=[('Authorization','GoogleLogin auth=%s'%(self._auth,))]

			data={'i':entry, # item的id
				    'a':add, # 要添加 state
				    'pos':pos,
				    'T':token,
				    's':source, # streamId
				    'async':'true',
				    }
			if remove:
				data['r']=remove
			r,_=self.getResponse(self.__class__.URL_GR_API_EDIT_TAG+'?client='+self.__class__.CLIENT_ID,data,headers)
			if r:
				r=r.decode()
				if r=='OK':
					self.logger.debug('edit tag succ~')
					return True
				elif r.find('401 Client Error')!=-1:
					self.logger.debug('got 401 error, try login ...')
					self.login(True)
					continue
				else:
					self.logger.debug('unknown response: %s',r) # 认为是失败
					break

			if r==b'':
				self.logger.debug('return empty, need update token? try ...')
				token,self._token=None,None
				continue

		self.logger.debug('edit tag failed!')
		return False



	def getUnreadCount(self):
		args={'output':'json',
		      'all': True,
		       'client':self.__class__.CLIENT_ID,
           'ck': '%.3f'%(time.time(),)
		       }
		url='?'.join((self.__class__.URL_GR_API_UNREAD_COUNT,urllib.parse.urlencode(args)))
		for _ in range(3):
			headers=[('Authorization','GoogleLogin auth=%s'%(self._auth,))]
			r,_=self.getResponse(url,None,headers)
			if r:
				r=r.decode()
##				self.logger.debug('return %s',r)
				try:
					data=json.loads(r)
				except ValueError:
					if r.find('401 Client Error')!=-1:
						self.logger.debug('got 401 error, try login ...')
						self.login(True)
						continue
				else:
##					self.logger.debug('%s=%s','max',data['max'])
					return data

##			for item in data['unreadcounts']:
##				t=int(item['newestItemTimestampUsec'])/1000000.0
##				d=datetime.datetime.fromtimestamp(t)
##				self.logger.debug('%s: %s %s',item['id'],item['count'],d.strftime("%Y-%m-%d %H:%M:%S"))

		return None

	def getAuthInfo(self):
		return self._auth

	def setAuthInfo(self,auth):
		self._auth=auth
		self._signed_in=True

C4GRApi.getReadingList=C4GRApi.checkLogin(C4GRApi.getReadingList)
C4GRApi.getTagList=C4GRApi.checkLogin(C4GRApi.getTagList)
C4GRApi.getSubscriptionList=C4GRApi.checkLogin(C4GRApi.getSubscriptionList)
C4GRApi.editTag=C4GRApi.checkLogin(C4GRApi.editTag)
C4GRApi.getUnreadCount=C4GRApi.checkLogin(C4GRApi.getUnreadCount)


class RSSFile(object):
	'''封装rss条目，以类似文件的形式使用'''
	def __init__(self,email,pwd,cookiefile):
		self.logger=logging.getLogger(self.__class__.__name__)
		self.gr=C4GRApi(email,pwd,cookiefile)
		self.itemlist=[]
		self.maxidx=len(self.itemlist) # 每次实际获取到的item
		self.curidx=0 # 要显示的每次实际获取到的item中的索引
		self.actualmax=len(self.itemlist) # 目前为止总共从server获取了多少
		self.totalcuridx=0 # 记录server端实际上总共有多少
		self.plist=deque() # 需要设置为各种状态的item的列表
		self.eventExit=threading.Event()
		self.pCount=re.compile('user/(\d{20})/state/com.google/reading-list',re.I)
		start_new_thread(self.thread4Plist,())

	def __iter__(self):
		return self

	def __next__(self):
		if self.curidx>=self.maxidx:
			if self.maxidx==0: # 只第一次时获取一次
				self.updateCount()

			if self.actualmax>0 and self.actualmax>(self.totalcuridx+self.maxidx): # 尝试获取更多
				self.totalcuridx+=self.maxidx
				self.logger.debug('try to get more items...')
				self.itemlist=self.gr.getReadingList(20 if self.actualmax-self.totalcuridx>20 else self.actualmax-self.totalcuridx,False if self.maxidx==0 else True)
				self.maxidx=len(self.itemlist)
				self.curidx=0
				self.logger.debug('got %d this time',self.maxidx)
			else:
				self.logger.debug('got all ~')

		if self.curidx<self.maxidx:
			self.curidx+=1
			return self.itemlist[self.curidx-1]
		else:
			raise StopIteration()

	def __len__(self):
		return len(self.itemlist)

##	def __getitem__(self,key):
##		return self.itemlist[key]

	def getActualMax(self):
		return self.actualmax

	def getIdx(self):
##		return self.curidx-1
		return self.totalcuridx+self.curidx-1

	def getAuthInfo(self):
		return self.gr.getAuthInfo()

	def setAuthInfo(self,auth):
		return self.gr.setAuthInfo(auth)

	def updateCount(self):
		'''更新 self.actualmax '''
		data=self.gr.getUnreadCount()
		if not data:
			self.logger.debug('can\'t got actualmax!')
		else:
			for eh in data['unreadcounts']:
				if self.pCount.match(eh['id']):
					self.actualmax=eh['count']
					self.logger.debug('total %d unread',self.actualmax)
					break
			else:
				self.logger.debug('0 unread?')

	def setEditItem(self,item):
		'''将对应的item加入self.plist队列'''
		self.plist.append(item)

	def setExit(self):
		'''设置退出标志使工作线程退出'''
		self.eventExit.set()

	def checkRss(self):
		'''reset内部数据结构以便触发重新获取待读条目'''
		self.maxidx=0
		self.curidx=0
		self.totalcuridx=0
		self.actualmax=0


	def thread4Plist(self):
		'''处理self.plist列表中item状态的线程'''
		m=None
		pendingLen=None
		while True:
			# do work
			try:
				pendingLen=len(self.plist)
				m=self.plist.popleft()
			except IndexError:
				pass
			else:
				self.logger.debug('total %d pending task',pendingLen)
				if m['a']=='read':
					if not self.gr.editTag(m['i'],'user/-/state/com.google/read',None,m['pos'],m['s']):
						self.plist.append(m) # 失败的重新插回
				else:
					self.logger.debug('action %s unknown!',m['a'])

			# sleep
			if self.eventExit.wait(3):
				self.logger.debug('eventExit set, exit ...')
				break





if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG,format='%(thread)d %(message)s')
##	t=C4GRApi('email','pwd','')
##	t.login()
##	t.getTagList()
##	t.getUnreadCount()
##	t.getSubscriptionList()
##	t.getReadingList()


	t=StartDictFile(r'D:\Program Files\StarDict\dic\stardict-langdao-ec-gb-2.4.2\langdao-ec-gb.ifo')
	t.readIFO()
	start=time.time()
	t.readIDX()
	print('%.3f'%(time.time()-start,))
	print(t.getMeaning('test'))
	import sys
	sys.exit()

	import cProfile,pstats
	cProfile.runctx('''t.readIDX()''',globals(),locals(),r'd:\stardict-profile.txt')
	p=pstats.Stats(r'd:\stardict-profile.txt')
	p.sort_stats('time', 'cum').print_stats('')

##	input('press ENTER to exit...')
